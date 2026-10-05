from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.database.connection import engine
from app.database.rag_models import KnowledgeDocument


class RAGRepository:
    def upsert_document(
        self,
        *,
        document_id: str,
        title: str,
        content: str,
        embedding: list[float],
        metadata: dict | None = None,
    ) -> None:
        table = KnowledgeDocument.__table__

        statement = insert(table).values(
            id=document_id,
            title=title,
            content=content,
            metadata=metadata,
            embedding=embedding,
        )

        statement = statement.on_conflict_do_update(
            index_elements=[table.c.id],
            set_={
                "title": statement.excluded.title,
                "content": statement.excluded.content,
                "metadata": statement.excluded.metadata,
                "embedding": statement.excluded.embedding,
            },
        )

        with engine.begin() as connection:
            connection.execute(statement)

    def semantic_search(
        self,
        query_embedding: list[float],
        top_k: int = 3,
    ) -> list[dict]:
        distance = KnowledgeDocument.embedding.cosine_distance(query_embedding)

        statement = (
            select(
                KnowledgeDocument.id,
                KnowledgeDocument.title,
                KnowledgeDocument.content,
                distance.label("distance"),
            )
            .order_by(distance)
            .limit(top_k)
        )

        with engine.connect() as connection:
            rows = connection.execute(statement).mappings().all()

        return [
            {
                "id": row["id"],
                "title": row["title"],
                "content": row["content"],
                "score": 1 - row["distance"],
            }
            for row in rows
        ]
