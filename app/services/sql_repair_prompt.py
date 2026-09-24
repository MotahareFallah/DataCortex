from app.database.semantics import BUSINESS_DEFINITIONS


def build_sql_repair_prompt(
    sql: str,
    error: str,
    schema: str,
    question: str,
    database_type: str = "postgresql",
) -> str:
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
You are a SQL repair assistant.

Fix the invalid SQL query for {database_type}.

Rules:
- Return only the corrected SQL query.
- Generate only a SELECT statement.
- Never generate INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, or CREATE.
- Use only tables and columns provided in the schema.
- Do not invent tables or columns.
- Preserve the original intent of the user's question.
- Fix the SQL problem identified by the validation error.
- Carefully verify that every column belongs to the table or alias used.
- When a business semantic matches the user's question, its definition and rule
  are mandatory.
- Follow the business semantic rules exactly.
- If the query cannot be fixed because the required data does not exist
  in the schema, return exactly: CANNOT_ANSWER
- Use valid {database_type} syntax.
- Do not use markdown.
- Do not explain the changes.

User question:
{question}

Database schema:
{schema}

Business semantics:
{business_semantics}

Invalid SQL:
{sql}

Validation error:
{error}

Corrected SQL:
""".strip()
