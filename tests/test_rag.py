from fastapi.testclient import TestClient

from app.main import app
from app.services.knowledge import search_knowledge, semantic_search
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


def test_semantic_search_returns_ranked_results():
    results = semantic_search("money received from completed orders")

    assert len(results) == 3
    assert results[0]["score"] >= results[1]["score"]
    assert results[1]["score"] >= results[2]["score"]


def test_semantic_search_returns_sales_related_document():
    results = semantic_search("revenue generated from customer purchases")

    result_ids = [result["id"] for result in results]

    assert "sales_definition" in result_ids


def test_semantic_search_returns_scores():
    results = semantic_search("customer purchases")

    for result in results:
        assert "score" in result
        assert isinstance(result["score"], float)


def test_semantic_search_respects_top_k():
    results = semantic_search(
        "customer purchases",
        top_k=2,
    )

    assert len(results) == 2


def test_semantic_search_default_top_k():
    results = semantic_search("customer purchases")

    assert len(results) == 3


def test_semantic_search_scores_are_sorted():
    results = semantic_search("customer purchases")

    scores = [result["score"] for result in results]

    assert scores == sorted(scores, reverse=True)
