def clean_sql(sql: str) -> str:
    cleaned_sql = sql.strip()

    if cleaned_sql.startswith("```sql"):
        cleaned_sql = cleaned_sql[len("```sql") :].strip()

    elif cleaned_sql.startswith("```"):
        cleaned_sql = cleaned_sql[3:].strip()

    if cleaned_sql.endswith("```"):
        cleaned_sql = cleaned_sql[:-3].strip()

    return cleaned_sql
