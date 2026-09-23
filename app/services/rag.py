from app.services.knowledge import search_knowledge, semantic_search


class RAGService:
    def retrieve(self, query: str) -> list[dict]:
        return search_knowledge(query)

    def semantic_retrieve(self, query: str) -> list[dict]:
        return semantic_search(query)
