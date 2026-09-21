from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_query_endpoint_returns_result():
    response = client.post(
        "/query",
        json={
            "sql": """
                SELECT id, name
                FROM products
                ORDER BY id
                LIMIT 3
            """
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["columns"] == ["id", "name"]
    assert data["row_count"] == 3
    assert len(data["rows"]) == 3


def test_query_endpoint_respects_limit():
    response = client.post(
        "/query",
        json={
            "sql": """
                SELECT id
                FROM products
                LIMIT 5
            """
        },
    )

    assert response.status_code == 200
    assert response.json()["row_count"] == 5


def test_query_endpoint_rejects_unsafe_sql():
    response = client.post(
        "/query",
        json={
            "sql": "DROP TABLE products",
        },
    )

    assert response.status_code == 400
