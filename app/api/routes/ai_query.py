from fastapi import APIRouter, HTTPException, status

from app.database.query import SQLExecutionError
from app.schemas.ai_query import AIQueryRequest, AIQueryResponse
from app.services.ai_query import AIQueryService

router = APIRouter()


@router.post("/ai/query", response_model=AIQueryResponse)
def ai_query(request: AIQueryRequest) -> AIQueryResponse:
    service = AIQueryService()

    try:
        return service.query(request.question)
    except SQLExecutionError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
