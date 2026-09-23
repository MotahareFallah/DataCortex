from app.services.entity_resolution import EntityResolutionService


def test_normalize_lowercases_text():
    service = EntityResolutionService()

    result = service.normalize("Acme Corporation")

    assert result == "acme corporation"


def test_normalize_removes_extra_spaces():
    service = EntityResolutionService()

    result = service.normalize("  Acme   Corporation  ")

    assert result == "acme corporation"


def test_normalize_removes_punctuation():
    service = EntityResolutionService()

    result = service.normalize("Acme, Inc.")

    assert result == "acme inc"


def test_resolve_returns_best_match():
    service = EntityResolutionService()

    result = service.resolve(
        "Acme Corporation",
        [
            "ACME Corporation",
            "Microsoft",
            "Apple",
        ],
    )

    assert result == "ACME Corporation"


def test_resolve_returns_none_below_threshold():
    service = EntityResolutionService()

    result = service.resolve(
        "Toyota",
        [
            "Microsoft",
            "Apple",
            "Amazon",
        ],
    )

    assert result is None


def test_resolve_respects_threshold():
    service = EntityResolutionService()

    result = service.resolve(
        "Acme Corp",
        [
            "ACME Corporation",
        ],
        threshold=0.99,
    )

    assert result is None


def test_resolve_semantic_returns_best_match():
    service = EntityResolutionService()

    result = service.resolve_semantic(
        "company that makes iPhones",
        [
            "Apple",
            "Microsoft",
            "Amazon",
        ],
    )

    assert result == "Apple"


def test_resolve_semantic_returns_best_semantic_match():
    service = EntityResolutionService()

    result = service.resolve_semantic(
        "online shopping marketplace",
        [
            "Amazon",
            "Microsoft",
            "Apple",
        ],
    )

    assert result == "Amazon"


def test_resolve_semantic_returns_none_for_empty_entities():
    service = EntityResolutionService()

    result = service.resolve_semantic(
        "Apple",
        [],
    )

    assert result is None
