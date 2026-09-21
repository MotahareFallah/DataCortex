from typing import Any

from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str | None = None
    sql: str


class QueryResult(BaseModel):
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int
