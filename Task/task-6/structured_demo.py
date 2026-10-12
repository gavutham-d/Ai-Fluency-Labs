"""Compare unconstrained, JSON-mode, and JSON-Schema extraction on the same query."""
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

TASK_DIR = Path(__file__).resolve().parent
load_dotenv(TASK_DIR / ".env", override=True)
sys.path.append(str(TASK_DIR.parent.parent / "lab-1"))
from config import MODEL, PROVIDER, banner, client

QUESTION = "I am growing basil in a 5-liter pot this summer. Extract the plant name, season, and pot size in liters."
SYSTEM = "Extract only the requested fields: plant, season, and pot_size_liters. When JSON mode is requested, return a JSON object."
EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "plant": {"type": "string", "enum": ["basil", "tomato", "mint"]},
        "season": {"type": "string", "enum": ["spring", "summer", "autumn", "winter"]},
        "pot_size_liters": {"type": "number", "minimum": 0.1, "maximum": 100},
    },
    "required": ["plant", "season", "pot_size_liters"],
    "additionalProperties": False,
}


def run_case(label, response_format=None):
    print(f"\n--- {label} ---")
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": QUESTION}],
            temperature=0,
            response_format=response_format,
        )
        raw = response.choices[0].message.content or ""
        print("Raw reply:", raw)
        try:
            print("Parsed result:", json.loads(raw))
        except json.JSONDecodeError as error:
            print(f"Parsed result: not valid JSON ({error})")
    except Exception as error:
        print(f"Not supported or request failed: {type(error).__name__}: {error}")


if __name__ == "__main__":
    banner("STRUCTURED OUTPUTS: GARDEN PLANT EXTRACTION")
    if PROVIDER == "groq" and not os.getenv("GROQ_API_KEY"):
        raise SystemExit("GROQ_API_KEY is missing from Task/task-6/.env")
    run_case("No response constraint", None)
    run_case("JSON mode", {"type": "json_object"})
    run_case("Strict JSON Schema mode", {
        "type": "json_schema",
        "json_schema": {
            "name": "plant_details",
            "strict": True,
            "schema": EXTRACTION_SCHEMA,
        },
    })
