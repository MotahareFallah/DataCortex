def build_answer_prompt(
    question: str,
    columns: list[str],
    rows: list[dict],
) -> str:
    return f"""
You are a data analysis assistant.

Answer the user's question using only the database result provided.

Rules:
- Do not invent information.
- Do not perform additional calculations unless they are directly supported by the result.
- Keep the answer concise and clear.
- Return only the natural-language answer.
- Do not mention SQL, database, tables, or internal processing.

User question:
{question}

Result columns:
{columns}

Result rows:
{rows}

Answer:
""".strip()
