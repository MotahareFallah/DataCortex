from app.services.result_formatter import format_result


def test_format_result_formats_rows():
    result = format_result(
        columns=["name", "total_sales"],
        rows=[
            {
                "name": "Product A",
                "total_sales": "31642.81",
            },
            {
                "name": "Product B",
                "total_sales": "24842.32",
            },
        ],
    )

    assert result == ("1. Product A — 31642.81\n2. Product B — 24842.32")


def test_format_result_handles_empty_rows():
    result = format_result(
        columns=["name", "total_sales"],
        rows=[],
    )

    assert result == "No results found."
