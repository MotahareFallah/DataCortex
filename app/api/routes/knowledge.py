from fastapi import APIRouter

from app.schemas.knowledge import (
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
)
from app.services.rag import RAGService

router = APIRouter(
    prefix="/knowledge",
    tags=["knowledge"],
)


@router.post(
    "/search",
    response_model=KnowledgeSearchResponse,
)
def search_knowledge(
    request: KnowledgeSearchRequest,
) -> KnowledgeSearchResponse:
    service = RAGService()

    results = service.retrieve(request.query)

    return KnowledgeSearchResponse(
        results=results,
    )
