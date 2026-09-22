from app.services.knowledge import search_knowledge


class RAGService:
    def retrieve(self, query: str) -> list[dict]:
        return search_knowledge(query)
