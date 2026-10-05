from sqlalchemy import create_engine

from app.core.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    connect_args={
        "options": f"-csearch_path={settings.postgres_schema},public",
    },
)
