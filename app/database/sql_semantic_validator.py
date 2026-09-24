import sqlglot
from sqlglot import exp


class SemanticSQLValidationError(ValueError):
    pass


def validate_sql_semantics(
    sql: str,
    question: str,
) -> None:
    tree = sqlglot.parse_one(sql, read="postgres")

    question_lower = question.lower()

    category_terms = (
        "category",
        "categories",
        "category name",
        "electronics",
    )

    asks_about_category = any(term in question_lower for term in category_terms)

    if not asks_about_category:
        return

    for condition in tree.find_all(exp.EQ):
        left = condition.left
        right = condition.right

        if not isinstance(left, exp.Column):
            continue

        if not isinstance(right, exp.Literal):
            continue

        if not right.is_string:
            continue

        if left.name.lower() != "name":
            continue

        if left.table.lower() not in {"p", "products"}:
            continue

        raise SemanticSQLValidationError(
            "Category name must be resolved through "
            "categories.name and products.category_id, "
            "not products.name."
        )
