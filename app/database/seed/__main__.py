from app.database.reset import reset_database
from app.database.seed.categories import seed_categories
from app.database.seed.customers import seed_customers
from app.database.seed.departments import seed_departments
from app.database.seed.employees import seed_employees
from app.database.seed.order_items import seed_order_items
from app.database.seed.orders import seed_orders
from app.database.seed.payments import seed_payments
from app.database.seed.products import seed_products


def main() -> None:
    reset_database()

    seed_departments()
    seed_categories()
    seed_employees()
    seed_customers()
    seed_products()
    seed_orders()
    seed_order_items()
    seed_payments()

    print("Seeded 1000 records successfully.")


if __name__ == "__main__":
    main()
