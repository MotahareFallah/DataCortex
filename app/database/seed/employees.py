import random

from faker import Faker
from sqlalchemy import text

from app.database.connection import engine

fake = Faker()


def seed_employees() -> None:
    roles = [
        "Manager",
        "Senior Analyst",
        "Analyst",
        "Sales Representative",
        "Accountant",
        "Engineer",
        "Specialist",
    ]

    with engine.begin() as connection:
        employee_ids = []

        for _ in range(20):
            result = connection.execute(
                text(
                    """
                    INSERT INTO employees (
                        department_id,
                        name,
                        role,
                        hired_at
                    )
                    VALUES (
                        :department_id,
                        :name,
                        :role,
                        :hired_at
                    )
                    RETURNING id
                    """
                ),
                {
                    "department_id": random.randint(1, 10),
                    "name": fake.name(),
                    "role": random.choice(roles),
                    "hired_at": fake.date_between(
                        start_date="-8y",
                        end_date="-1y",
                    ),
                },
            )

            employee_ids.append(result.scalar_one())

        for employee_id in employee_ids[1:]:
            manager_id = random.choice(employee_ids[: employee_ids.index(employee_id)])

            connection.execute(
                text(
                    """
                    UPDATE employees
                    SET manager_id = :manager_id
                    WHERE id = :employee_id
                    """
                ),
                {
                    "manager_id": manager_id,
                    "employee_id": employee_id,
                },
            )
