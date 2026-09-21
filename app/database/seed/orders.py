import random

from faker import Faker
from sqlalchemy import text

from app.database.connection import engine

fake = Faker()


def seed_orders() -> None:
    statuses = [
        "pending",
        "confirmed",
        "completed",
        "cancelled",
    ]

    with engine.begin() as connection:
        for _ in range(200):
            subtotal = round(random.uniform(100, 10000), 2)
            tax_amount = round(
                subtotal * random.uniform(0.05, 0.15),
                2,
            )
            total_amount = round(
                subtotal + tax_amount,
                2,
            )

            connection.execute(
                text(
                    """
                    INSERT INTO orders (
                        customer_id,
                        employee_id,
                        status,
                        ordered_at,
                        currency,
                        subtotal,
                        tax_amount,
                        total_amount
                    )
                    VALUES (
                        :customer_id,
                        :employee_id,
                        :status,
                        :ordered_at,
                        :currency,
                        :subtotal,
                        :tax_amount,
                        :total_amount
                    )
                    """
                ),
                {
                    "customer_id": random.randint(1, 50),
                    "employee_id": random.randint(1, 20),
                    "status": random.choice(statuses),
                    "ordered_at": fake.date_time_between(
                        start_date="-2y",
                        end_date="now",
                    ),
                    "currency": "USD",
                    "subtotal": subtotal,
                    "tax_amount": tax_amount,
                    "total_amount": total_amount,
                },
            )
