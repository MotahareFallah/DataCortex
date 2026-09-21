from sqlalchemy import text

from app.database.connection import engine


def seed_departments() -> None:
    departments = [
        "Finance",
        "Sales",
        "Marketing",
        "Human Resources",
        "Operations",
        "IT",
        "Procurement",
        "Logistics",
        "Legal",
        "Analytics",
    ]

    with engine.begin() as connection:
        for name in departments:
            connection.execute(
                text(
                    """
                    INSERT INTO departments (name)
                    VALUES (:name)
                    """
                ),
                {"name": name},
            )
