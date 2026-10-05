from app.database.connection import engine
from app.services.rag_repository import RAGRepository

TEST_DOCUMENT_ID = "test_document"


def delete_test_document() -> None:
    with engine.begin() as connection:
        connection.exec_driver_sql(
            """
            DELETE FROM datacortex.knowledge_documents
            WHERE id = 'test_document'
            """
        )


def test_upsert_document_creates_document():
    delete_test_document()

    repository = RAGRepository()

    repository.upsert_document(
        document_id=TEST_DOCUMENT_ID,
        title="Test Document",
        content="Initial content",
        embedding=[0.1] * 384,
    )

    with engine.connect() as connection:
        row = (
            connection.exec_driver_sql(
                """
            SELECT id, title, content
            FROM datacortex.knowledge_documents
            WHERE id = 'test_document'
            """
            )
            .mappings()
            .one()
        )

    assert row["id"] == TEST_DOCUMENT_ID
    assert row["title"] == "Test Document"
    assert row["content"] == "Initial content"

    delete_test_document()


def test_upsert_document_updates_existing_document():
    delete_test_document()

    repository = RAGRepository()

    repository.upsert_document(
        document_id=TEST_DOCUMENT_ID,
        title="Original Title",
        content="Original content",
        embedding=[0.1] * 384,
    )

    repository.upsert_document(
        document_id=TEST_DOCUMENT_ID,
        title="Updated Title",
        content="Updated content",
        embedding=[0.2] * 384,
    )

    with engine.connect() as connection:
        row = (
            connection.exec_driver_sql(
                """
            SELECT id, title, content
            FROM datacortex.knowledge_documents
            WHERE id = 'test_document'
            """
            )
            .mappings()
            .one()
        )

    assert row["id"] == TEST_DOCUMENT_ID
    assert row["title"] == "Updated Title"
    assert row["content"] == "Updated content"

    delete_test_document()
