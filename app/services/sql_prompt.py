def build_sql_prompt(question: str, schema: str) -> str:
    return f"""
You are a SQL generation assistant.

Convert the user's natural language question into
a PostgreSQL SELECT query.

Rules:
- Generate only SELECT statements.
- Never generate INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, or CREATE.
- Use only tables and columns provided in the schema.
- Do not invent tables or columns.
- Use the minimum number of tables required to answer the question.
- Do not add JOINs unless they are necessary to answer the question.
- If the requested column exists directly in a table that can answer the question,
  use that table directly.
- Carefully verify that every column belongs to the table or alias used.
- Return only the SQL query.
- Do not use markdown.
- Do not explain the query.

Database schema:
{schema}

User question:
{question}

SQL query:
""".strip()
