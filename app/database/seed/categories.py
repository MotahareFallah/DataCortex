from sqlalchemy import text

from app.database.connection import engine


def seed_categories() -> None:
    categories = [
        "Electronics",
        "Software",
        "Hardware",
        "Office Supplies",
        "Industrial Equipment",
        "Raw Materials",
        "Services",
        "Consulting",
        "Logistics",
        "Energy",
        "Mining",
        "Construction",
        "Automotive",
        "Healthcare",
        "Education",
        "Finance",
        "Food",
        "Retail",
        "Security",
        "Telecommunications",
    ]

    with engine.begin() as connection:
        for name in categories:
            connection.execute(
                text(
                    """
                    INSERT INTO categories (name)
                    VALUES (:name)
                    """
                ),
                {"name": name},
            )
