from app.services.embedding import EmbeddingService
from app.services.knowledge import search_knowledge
from app.services.rag_repository import RAGRepository

DEFAULT_SEMANTIC_THRESHOLD = 0.30


class RAGService:
    def __init__(
        self,
        semantic_threshold: float = DEFAULT_SEMANTIC_THRESHOLD,
    ) -> None:
        self.embedding_service = EmbeddingService()
        self.repository = RAGRepository()
        self.semantic_threshold = semantic_threshold

    def retrieve(self, query: str) -> list[dict]:
        return search_knowledge(query)

    def semantic_retrieve(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[dict]:
        query_embedding = self.embedding_service.embed(query)

        results = self.repository.semantic_search(
            query_embedding=query_embedding,
            top_k=top_k,
        )

        return [
            result for result in results if result["score"] >= self.semantic_threshold
        ]
