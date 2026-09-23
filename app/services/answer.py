from app.services.result_formatter import format_result


class AnswerService:
    def generate_answer(
        self,
        question: str,
        columns: list[str],
        rows: list[dict],
    ) -> str:
        if not rows:
            return "No results found."

        if len(rows) == 1 and len(columns) == 1:
            column = columns[0]
            value = rows[0][column]
            return f"{column}: {value}"

        return format_result(
            columns=columns,
            rows=rows,
        )
