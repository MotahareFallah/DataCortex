EXECUTE_SQL_TOOL = {
    "type": "function",
    "function": {
        "name": "execute_sql",
        "description": "Execute a read-only SQL query against the database.",
        "parameters": {
            "type": "object",
            "properties": {
                "sql": {
                    "type": "string",
                    "description": "A valid PostgreSQL SELECT query.",
                }
            },
            "required": ["sql"],
        },
    },
}
