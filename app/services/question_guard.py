import re

# Matches imperative write requests such as "Delete all orders" or
# "Please drop the products table". Anchored at the start on purpose so that
# questions like "Which products had the biggest price drop?" are not blocked.
_WRITE_REQUEST = re.compile(
    r"^\s*(?:please\s+|can you\s+|could you\s+|i want to\s+|i need to\s+)?"
    r"(?:delete|drop|truncate|insert|update|alter|remove|erase|wipe|create)\b",
    re.IGNORECASE,
)


def is_write_request(question: str) -> bool:
    return bool(_WRITE_REQUEST.match(question))
