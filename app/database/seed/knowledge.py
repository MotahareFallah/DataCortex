from app.services.embedding import EmbeddingService
from app.services.knowledge import KNOWLEDGE_BASE
from app.services.rag_repository import RAGRepository


def seed_knowledge() -> None:
    embedding_service = EmbeddingService()
    repository = RAGRepository()

    for document in KNOWLEDGE_BASE:
        embedding = embedding_service.embed(
            f"{document['title']}. {document['content']}"
        )

        repository.upsert_document(
            document_id=document["id"],
            title=document["title"],
            content=document["content"],
            embedding=embedding,
        )


if __name__ == "__main__":
    seed_knowledge()
    print("Knowledge documents seeded successfully.")
