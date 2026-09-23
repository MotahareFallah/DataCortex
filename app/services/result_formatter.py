def format_result(
    columns: list[str],
    rows: list[dict],
) -> str:
    if not rows:
        return "No results found."

    lines = []

    for index, row in enumerate(rows, start=1):
        values = [str(row.get(column, "")) for column in columns]

        lines.append(f"{index}. " + " — ".join(values))

    return "\n".join(lines)
