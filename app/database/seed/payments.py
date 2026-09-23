import random

from sqlalchemy import text

from app.database.connection import engine


def seed_payments() -> None:
    methods = [
        "credit_card",
        "bank_transfer",
        "cash",
    ]

    with engine.begin() as connection:
        orders = (
            connection.execute(
                text(
                    """
                SELECT id, total_amount, ordered_at
                FROM orders
                ORDER BY id
                """
                )
            )
            .mappings()
            .all()
        )

        for order in orders:
            status = random.choices(
                ["paid", "pending", "failed"],
                weights=[80, 15, 5],
                k=1,
            )[0]

            paid_at = order["ordered_at"] if status == "paid" else None

            connection.execute(
                text(
                    """
                    INSERT INTO payments (
                        order_id,
                        amount,
                        method,
                        status,
                        paid_at
                    )
                    VALUES (
                        :order_id,
                        :amount,
                        :method,
                        :status,
                        :paid_at
                    )
                    """
                ),
                {
                    "order_id": order["id"],
                    "amount": order["total_amount"],
                    "method": random.choice(methods),
                    "status": status,
                    "paid_at": paid_at,
                },
            )
