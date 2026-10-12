"""Simulated external flight-search service and a safe calculator."""
import ast
import operator

FLIGHTS = [
    {"flight": "SK101", "airline": "SkyLink", "origin": "BLR", "destination": "DEL", "date": "2026-10-15", "departure": "06:30", "arrival": "09:15", "price": 7200, "baggage_kg": 15},
    {"flight": "AI204", "airline": "Air India", "origin": "BLR", "destination": "DEL", "date": "2026-10-15", "departure": "10:00", "arrival": "12:50", "price": 8100, "baggage_kg": 15},
    {"flight": "6E305", "airline": "IndiGo", "origin": "BLR", "destination": "DEL", "date": "2026-10-15", "departure": "18:20", "arrival": "21:05", "price": 7600, "baggage_kg": 15},
    {"flight": "SK220", "airline": "SkyLink", "origin": "BLR", "destination": "BOM", "date": "2026-10-15", "departure": "08:15", "arrival": "10:00", "price": 5400, "baggage_kg": 15},
]


def search_flights(origin: str, destination: str, date: str) -> str:
    """Look up flights in the simulated external booking service."""
    matches = [flight for flight in FLIGHTS if flight["origin"] == origin.upper() and flight["destination"] == destination.upper() and flight["date"] == date]
    if not matches:
        return "No flights found for those search details."
    return "\n".join(str(flight) for flight in matches)


_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv, ast.USub: operator.neg}


def _evaluate(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_evaluate(node.left), _evaluate(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_evaluate(node.operand))
    raise ValueError("Unsupported expression")


def calculator(expression: str) -> str:
    try:
        return str(_evaluate(ast.parse(expression, mode="eval").body))
    except Exception as error:
        return f"Calculator error: {error}"


TOOL_FUNCTIONS = {"search_flights": search_flights, "calculator": calculator}
TOOLS = [
    {"type": "function", "function": {"name": "search_flights", "description": "Search the external flight service by airport codes and date.", "parameters": {"type": "object", "properties": {"origin": {"type": "string"}, "destination": {"type": "string"}, "date": {"type": "string"}}, "required": ["origin", "destination", "date"]}}},
    {"type": "function", "function": {"name": "calculator", "description": "Evaluate arithmetic using numbers and + - * / brackets.", "parameters": {"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]}}},
]

if __name__ == "__main__":
    print(search_flights("BLR", "DEL", "2026-10-15"))
