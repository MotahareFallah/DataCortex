import re
from difflib import SequenceMatcher

from app.services.embedding import EmbeddingService


class EntityResolutionService:
    def __init__(self) -> None:
        self.embedding_service = EmbeddingService()

    def normalize(self, value: str) -> str:
        value = value.lower().strip()
        value = re.sub(r"[^\w\s]", "", value)
        value = re.sub(r"\s+", " ", value)

        return value

    def resolve(
        self,
        query: str,
        entities: list[str],
        threshold: float = 0.8,
    ) -> str | None:
        normalized_query = self.normalize(query)

        best_match = None
        best_score = 0.0

        for entity in entities:
            normalized_entity = self.normalize(entity)

            score = SequenceMatcher(
                None,
                normalized_query,
                normalized_entity,
            ).ratio()

            if score > best_score:
                best_score = score
                best_match = entity

        if best_score >= threshold:
            return best_match

        return None

    def resolve_semantic(
        self,
        query: str,
        entities: list[str],
    ) -> str | None:
        if not entities:
            return None

        query_embedding = self.embedding_service.embed(query)

        best_match = None
        best_score = -1.0

        for entity in entities:
            entity_embedding = self.embedding_service.embed(entity)

            score = sum(
                query_value * entity_value
                for query_value, entity_value in zip(
                    query_embedding,
                    entity_embedding,
                    strict=True,
                )
            )

            if score > best_score:
                best_score = score
                best_match = entity

        return best_match
