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


def search_knowledge(query: str) -> list[dict]:
    query_words = set(query.lower().split())

    results = []

    for document in KNOWLEDGE_BASE:
        document_text = (f"{document['title']} {document['content']}").lower()

        document_words = set(document_text.split())

        if query_words & document_words:
            results.append(document)

    return results
