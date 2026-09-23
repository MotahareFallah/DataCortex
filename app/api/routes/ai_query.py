import logging

from fastapi import APIRouter, HTTPException

from app.database.query import SQLExecutionError
from app.database.sql_validator import UnsafeSQLQueryError
from app.schemas.ai_query import AIQueryRequest, AIQueryResponse
from app.services.ai_query import AIQueryService
from app.services.exceptions import (
    QuestionNotAnswerableError,
    WriteRequestError,
)

router = APIRouter()

# Plain 422: avoids the deprecated starlette constant name across versions.
UNPROCESSABLE = 422


@router.post("/ai/query", response_model=AIQueryResponse)
def ai_query(request: AIQueryRequest) -> AIQueryResponse:
    service = AIQueryService()

    try:
        return service.query(request.question)
    except WriteRequestError as exc:
        logging.warning("Write request rejected: %s", request.question)
        raise HTTPException(
            status_code=UNPROCESSABLE,
            detail=(
                "This system is read-only. It can answer questions about "
                "the data, but it cannot modify it."
            ),
        ) from exc
    except QuestionNotAnswerableError as exc:
        logging.warning("Question not answerable: %s", request.question)
        raise HTTPException(
            status_code=UNPROCESSABLE,
            detail=(
                "I can't answer this question with the data available. "
                "Try asking about the tables and fields that exist."
            ),
        ) from exc
    except UnsafeSQLQueryError as exc:
        logging.warning("Rejected AI-generated SQL: %s", exc)
        raise HTTPException(
            status_code=UNPROCESSABLE,
            detail=(
                "I couldn't turn this question into a valid, safe SQL query. "
                "Please rephrase it or be more specific about what data you need."
            ),
        ) from exc
    except SQLExecutionError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
