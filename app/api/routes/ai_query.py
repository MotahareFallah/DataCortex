import logging

from fastapi import APIRouter, HTTPException, status

from app.database.query import SQLExecutionError
from app.database.sql_validator import UnsafeSQLQueryError
from app.schemas.ai_query import AIQueryRequest, AIQueryResponse
from app.services.ai_query import AIQueryService

router = APIRouter()


@router.post("/ai/query", response_model=AIQueryResponse)
def ai_query(request: AIQueryRequest) -> AIQueryResponse:
    service = AIQueryService()

    try:
        return service.query(request.question)
    except UnsafeSQLQueryError as exc:
        # Technical details stay in the log; the user gets a friendly message.
        logging.warning("Rejected AI-generated SQL: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "I couldn't turn this question into a valid, safe SQL query. "
                "Please rephrase it or be more specific about what data you need."
            ),
        ) from exc
    except SQLExecutionError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
