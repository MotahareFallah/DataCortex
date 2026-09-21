import random
from decimal import Decimal

from sqlalchemy import text

from app.database.connection import engine


def seed_order_items() -> None:
    with engine.begin() as connection:
        orders = (
            connection.execute(
                text(
                    """
                SELECT id, subtotal
                FROM orders
                ORDER BY id
                """
                )
            )
            .mappings()
            .all()
        )

        products = (
            connection.execute(
                text(
                    """
                SELECT id, price
                FROM products
                ORDER BY id
                """
                )
            )
            .mappings()
            .all()
        )

        for order in orders:
            subtotal = Decimal(str(order["subtotal"]))
            first_line_total = (subtotal * Decimal("0.4")).quantize(Decimal("0.01"))
            second_line_total = subtotal - first_line_total

            selected_products = random.sample(products, 2)

            line_totals = [
                first_line_total,
                second_line_total,
            ]

            for product, line_total in zip(
                selected_products,
                line_totals,
                strict=True,
            ):
                quantity = random.randint(1, 5)
                unit_price = Decimal(str(product["price"]))

                gross_amount = (unit_price * quantity).quantize(Decimal("0.01"))

                discount_amount = max(
                    Decimal("0"),
                    gross_amount - line_total,
                ).quantize(Decimal("0.01"))

                connection.execute(
                    text(
                        """
                        INSERT INTO order_items (
                            order_id,
                            product_id,
                            quantity,
                            unit_price,
                            discount_amount,
                            line_total
                        )
                        VALUES (
                            :order_id,
                            :product_id,
                            :quantity,
                            :unit_price,
                            :discount_amount,
                            :line_total
                        )
                        """
                    ),
                    {
                        "order_id": order["id"],
                        "product_id": product["id"],
                        "quantity": quantity,
                        "unit_price": unit_price,
                        "discount_amount": discount_amount,
                        "line_total": line_total,
                    },
                )
