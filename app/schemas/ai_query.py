from typing import Any

from pydantic import BaseModel


class AIQueryRequest(BaseModel):
    question: str


class AIQueryResponse(BaseModel):
    question: str
    sql: str
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int
    answer: str
    truncated: bool = False
