from sqlalchemy import text

from app.database.connection import engine


def reset_database() -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                TRUNCATE TABLE
                    payments,
                    order_items,
                    orders,
                    employees,
                    customers,
                    products,
                    categories,
                    departments
                RESTART IDENTITY CASCADE
                """
            )
        )

    print("Database reset successfully.")
