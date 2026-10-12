"""Tools the agent is allowed to use, plus their JSON Schema descriptions."""
import ast
import operator

from config import UPI_ACCOUNTS


def get_upi_profile(identifier: str) -> str:
    """Return the private UPI setup record for a user name or UPI ID."""
    key = identifier.strip().lower()

    for name, data in UPI_ACCOUNTS.items():
        if name == key or data["upi_id"].lower() == key:
            return str({"user": name, **data})

    return f"Unknown UPI profile: {identifier}"


def get_daily_limit(upi_id: str) -> str:
    """Return the daily payment limit for a given UPI ID."""
    key = upi_id.strip().lower()
    for data in UPI_ACCOUNTS.values():
        if data["upi_id"].lower() == key:
            return str(data["daily_limit"])
    return f"Unknown UPI ID: {upi_id}"


_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
}


def _evaluate(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_evaluate(node.left), _evaluate(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_evaluate(node.operand))
    raise ValueError("Unsupported expression")


def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression such as 5000 * 1.015."""
    try:
        return str(_evaluate(ast.parse(expression, mode="eval").body))
    except Exception as error:
        return f"Calculator error: {error}"


TOOL_FUNCTIONS = {"get_upi_profile": get_upi_profile, "get_daily_limit": get_daily_limit, "calculator": calculator}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_upi_profile",
            "description": "Get the private UPI record for a user name or UPI ID.",
            "parameters": {
                "type": "object",
                "properties": {"identifier": {"type": "string"}},
                "required": ["identifier"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_daily_limit",
            "description": "Return the daily payment limit for a UPI ID.",
            "parameters": {
                "type": "object",
                "properties": {"upi_id": {"type": "string"}},
                "required": ["upi_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluate arithmetic using + - * / and brackets.",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"],
            },
        },
    },
]


if __name__ == "__main__":
    print("get_upi_profile('alice') ->", get_upi_profile("alice"))
    print("get_daily_limit('bob@paytm') ->", get_daily_limit("bob@paytm"))
    print("calculator('5000 * 1.015') ->", calculator("5000 * 1.015"))
