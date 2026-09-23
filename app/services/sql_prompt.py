from app.database.database import get_database_adapter
from app.database.semantics import BUSINESS_DEFINITIONS


def build_sql_prompt(
    question: str,
    schema: str,
    database_type: str = "postgresql",
) -> str:
    adapter = get_database_adapter(database_type)

    business_semantics = "\n".join(
        (
            f"- {name}: {details['definition']}\n"
            f"  Tables: {', '.join(details['tables'])}\n"
            f"  Columns: {', '.join(details['columns'])}\n"
            f"  Rule: {details['rule']}"
        )
        for name, details in BUSINESS_DEFINITIONS.items()
    )

    return f"""
You are a SQL generation assistant.

Convert the user's natural language question into
a SQL SELECT query for {database_type}.

Rules:
- Generate only SELECT statements.
- Never generate INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, or CREATE.
- Use only tables and columns provided in the schema.
- Do not invent tables or columns.
- Use the minimum number of tables required to answer the question.
- Do not add JOINs unless they are necessary to answer the question.
- Carefully verify that every column belongs to the table or alias used.
- Use the database-specific SQL syntax for {database_type}.
- Use {adapter.placeholder()} as the parameter placeholder when parameters are required.
- When a business semantic matches the user's question, its definition and rule are mandatory.
- Follow the business semantic rules exactly.
- Do not use tables or columns that are not necessary to answer the question.
- Return only the SQL query.
- Do not use markdown.
- Do not explain the query.

Database schema:
{schema}

Business semantics:
{business_semantics}

User question:
{question}

SQL query:
""".strip()
