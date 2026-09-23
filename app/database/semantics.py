BUSINESS_DEFINITIONS = {
    "total_sales": {
        "definition": "The sum of order_items.line_total.",
        "tables": ["order_items"],
        "columns": ["order_items.line_total"],
        "rule": "Never use orders.total_amount or products.price for total sales.",
    },
    "product_sales": {
        "definition": "The sum of order_items.line_total grouped by product.",
        "tables": ["products", "order_items"],
        "columns": [
            "products.id",
            "products.name",
            "order_items.product_id",
            "order_items.line_total",
        ],
        "rule": (
            "Join products to order_items using products.id = order_items.product_id "
            "and calculate sales using SUM(order_items.line_total)."
        ),
    },
    "order_subtotal": {
        "definition": "The value of orders.subtotal before tax.",
        "tables": ["orders"],
        "columns": ["orders.subtotal"],
        "rule": "Do not use orders.total_amount for order subtotal.",
    },
    "order_total": {
        "definition": "The value of orders.total_amount including tax.",
        "tables": ["orders"],
        "columns": ["orders.total_amount"],
        "rule": "Use orders.total_amount when the question explicitly asks for order total.",
    },
}
