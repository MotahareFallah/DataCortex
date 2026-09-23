def build_sql_repair_prompt(
    sql: str,
    error: str,
    schema: str,
    database_type: str = "postgresql",
) -> str:
    return f"""
You are a SQL repair assistant.

Fix the invalid SQL query for {database_type}.

Rules:
- Return only the corrected SQL query.
- Generate only a SELECT statement.
- Never generate INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, or CREATE.
- Use only tables and columns provided in the schema.
- Do not invent tables or columns.
- Preserve the original intent of the user's query.
- Fix only the SQL problems necessary to make the query valid.
- Use valid {database_type} syntax.
- Do not use markdown.
- Do not explain the changes.

Database schema:
{schema}

Invalid SQL:
{sql}

Validation error:
{error}

Corrected SQL:
""".strip()
