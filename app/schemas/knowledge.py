from pydantic import BaseModel


class KnowledgeSearchRequest(BaseModel):
    query: str


class KnowledgeSearchResponse(BaseModel):
    results: list[dict]
