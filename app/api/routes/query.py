from fastapi import APIRouter, HTTPException, status

from app.database.query import execute_query
from app.database.sql_validator import UnsafeSQLQueryError
from app.schemas.query import QueryRequest, QueryResult

router = APIRouter()


@router.post("/query", response_model=QueryResult)
def query_database(request: QueryRequest) -> QueryResult:
    try:
        return execute_query(request.sql)
    except UnsafeSQLQueryError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
