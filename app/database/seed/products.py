import random

from faker import Faker
from sqlalchemy import text

from app.database.connection import engine

fake = Faker()


def seed_products() -> None:
    with engine.begin() as connection:
        for index in range(1, 101):
            cost = round(random.uniform(10, 900), 2)
            price = round(cost * random.uniform(1.2, 2.5), 2)

            connection.execute(
                text(
                    """
                    INSERT INTO products (
                        category_id,
                        name,
                        sku,
                        price,
                        cost,
                        is_active
                    )
                    VALUES (
                        :category_id,
                        :name,
                        :sku,
                        :price,
                        :cost,
                        :is_active
                    )
                    """
                ),
                {
                    "category_id": random.randint(1, 20),
                    "name": fake.catch_phrase(),
                    "sku": f"SKU-{index:04d}",
                    "price": price,
                    "cost": cost,
                    "is_active": random.choice([True, True, True, False]),
                },
            )
