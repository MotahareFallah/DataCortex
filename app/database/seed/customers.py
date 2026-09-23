from faker import Faker
from sqlalchemy import text

from app.database.connection import engine

fake = Faker()


def seed_customers() -> None:
    with engine.begin() as connection:
        for _ in range(50):
            connection.execute(
                text(
                    """
                    INSERT INTO customers (
                        name,
                        email,
                        country
                    )
                    VALUES (
                        :name,
                        :email,
                        :country
                    )
                    """
                ),
                {
                    "name": fake.name(),
                    "email": fake.unique.email(),
                    "country": fake.country(),
                },
            )
