import sqlglot
from sqlglot import exp


def repair_column_table_reference(
    sql: str,
    schema: dict[str, set[str]],
) -> str:
    tree = sqlglot.parse_one(sql, read="postgres")

    table_aliases: dict[str, str] = {}

    for table in tree.find_all(exp.Table):
        table_name = table.name
        alias = table.alias

        if alias:
            table_aliases[alias] = table_name
        else:
            table_aliases[table_name] = table_name

    for column in tree.find_all(exp.Column):
        if not column.table:
            continue

        table_reference = column.table
        column_name = column.name

        table_name = table_aliases.get(table_reference)

        if table_name is None:
            continue

        if column_name in schema.get(table_name, set()):
            continue

        matching_tables = [
            candidate_table
            for candidate_table, columns in schema.items()
            if column_name in columns
        ]

        if len(matching_tables) != 1:
            continue

        target_table = matching_tables[0]

        target_aliases = [
            alias
            for alias, candidate_table in table_aliases.items()
            if candidate_table == target_table
        ]

        if len(target_aliases) != 1:
            continue

        column.set("table", exp.to_identifier(target_aliases[0]))

    return tree.sql(dialect="postgres")
