from pydantic import BaseModel


class ColumnSchema(BaseModel):
    name: str
    type: str
    nullable: bool
    default: str | None


class ForeignKeySchema(BaseModel):
    columns: list[str]
    references_table: str
    references_columns: list[str]


class TableSchema(BaseModel):
    columns: list[ColumnSchema]
    primary_key: list[str]
    foreign_keys: list[ForeignKeySchema]


class DatabaseSchema(BaseModel):
    database: str
    tables: dict[str, TableSchema]
