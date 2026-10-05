from sqlalchemy import inspect

from app.core.config import settings
from app.database.connection import engine
from app.schemas.database import (
    ColumnSchema,
    DatabaseSchema,
    ForeignKeySchema,
    TableSchema,
)

EXCLUDED_TABLES = {"knowledge_documents"}


def discover_schema() -> DatabaseSchema:
    inspector = inspect(engine)

    tables = {}

    for table_name in inspector.get_table_names(schema=settings.postgres_schema):
        if table_name in EXCLUDED_TABLES:
            continue

        columns = inspector.get_columns(
            table_name,
            schema=settings.postgres_schema,
        )
        primary_key = inspector.get_pk_constraint(
            table_name,
            schema=settings.postgres_schema,
        )
        foreign_keys = inspector.get_foreign_keys(
            table_name,
            schema=settings.postgres_schema,
        )

        tables[table_name] = TableSchema(
            columns=[
                ColumnSchema(
                    name=column["name"],
                    type=str(column["type"]),
                    nullable=column["nullable"],
                    default=(
                        str(column["default"])
                        if column["default"] is not None
                        else None
                    ),
                )
                for column in columns
            ],
            primary_key=primary_key["constrained_columns"],
            foreign_keys=[
                ForeignKeySchema(
                    columns=foreign_key["constrained_columns"],
                    references_table=foreign_key["referred_table"],
                    references_columns=foreign_key["referred_columns"],
                )
                for foreign_key in foreign_keys
            ],
        )

    return DatabaseSchema(
        database=engine.url.database,
        tables=tables,
    )
