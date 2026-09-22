from fastapi.testclient import TestClient

from app.main import app
from app.services.knowledge import search_knowledge
from app.services.rag import RAGService

client = TestClient(app)


def test_search_knowledge_returns_relevant_document():
    results = search_knowledge("total sales")

    assert len(results) == 2
    assert results[0]["id"] == "sales_definition"
    assert results[1]["id"] == "order_status"


def test_search_knowledge_returns_empty_for_unrelated_query():
    results = search_knowledge("employee vacation policy")

    assert results == []


def test_search_knowledge_is_case_insensitive():
    results = search_knowledge("TOTAL SALES")

    assert len(results) == 2


def test_rag_service_retrieves_relevant_documents():
    service = RAGService()

    results = service.retrieve("total sales")

    assert len(results) == 2
    assert results[0]["id"] == "sales_definition"


def test_knowledge_search_api_returns_results():
    response = client.post(
        "/knowledge/search",
        json={"query": "total sales"},
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["results"]) == 2
    assert data["results"][0]["id"] == "sales_definition"


def test_knowledge_search_api_returns_empty_results():
    response = client.post(
        "/knowledge/search",
        json={"query": "employee vacation policy"},
    )

    assert response.status_code == 200
    assert response.json()["results"] == []
