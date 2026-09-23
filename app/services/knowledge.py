from app.services.embedding import EmbeddingService

KNOWLEDGE_BASE = [
    {
        "id": "sales_definition",
        "title": "Sales Definition",
        "content": (
            "Total sales represent the total monetary value of completed "
            "customer orders."
        ),
    },
    {
        "id": "order_status",
        "title": "Order Status",
        "content": (
            "Only completed orders should be included when calculating "
            "official total sales."
        ),
    },
    {
        "id": "customer_definition",
        "title": "Customer Definition",
        "content": (
            "A customer is a person or organization that has placed at least "
            "one order in the system."
        ),
    },
]


_embedding_service = EmbeddingService()


for document in KNOWLEDGE_BASE:
    document["embedding"] = _embedding_service.embed(
        f"{document['title']}. {document['content']}"
    )


def search_knowledge(query: str) -> list[dict]:
    query_words = set(query.lower().split())

    results = []

    for document in KNOWLEDGE_BASE:
        document_text = (f"{document['title']} {document['content']}").lower()

        document_words = set(document_text.split())

        if query_words & document_words:
            results.append(document)

    return results


def semantic_search(
    query: str,
    top_k: int = 3,
) -> list[dict]:
    query_embedding = _embedding_service.embed(query)

    results = []

    for document in KNOWLEDGE_BASE:
        score = sum(
            query_value * document_value
            for query_value, document_value in zip(
                query_embedding,
                document["embedding"],
                strict=False,
            )
        )

        results.append(
            {
                "id": document["id"],
                "title": document["title"],
                "content": document["content"],
                "score": score,
            }
        )

    results.sort(
        key=lambda document: document["score"],
        reverse=True,
    )

    return results[:top_k]
