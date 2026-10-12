"""Ask the same questions with one course-fee lookup tool available."""
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"), override=True)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "lab-1")))
from config import MODEL, banner, client

FEES_PATH = Path(__file__).with_name("course_fees.json")
QUESTIONS = [
    "According to our private Greenfield course fee table, what is the fee for AI202?",
    "What is the difference between a course fee and a fine?",
    "Write a friendly two-line welcome message for new AI students.",
]

SYSTEM = (
    "You are a helpful Greenfield College assistant. For an exact course fee from the private "
    "Greenfield fee table, you MUST call lookup_course_fee. For general explanations or creative "
    "writing, answer directly without calling the tool. Use a tool result as the authority; do not "
    "guess private fees."
)

TOOL = {
    "type": "function",
    "function": {
        "name": "lookup_course_fee",
        "description": "Look up the official private Greenfield College fee for a course code.",
        "parameters": {
            "type": "object",
            "properties": {
                "course_code": {
                    "type": "string",
                    "description": "Course code, for example AI202",
                }
            },
            "required": ["course_code"],
            "additionalProperties": False,
        },
    },
}


def lookup_course_fee(course_code: str) -> str:
    """Read and return one course's fee from the local private fee table."""
    fees = json.loads(FEES_PATH.read_text(encoding="utf-8"))
    code = course_code.strip().upper()
    amount = fees.get(code)
    return f"{code} fee is Rs. {amount}." if amount is not None else f"No fee is listed for {code}."


if __name__ == "__main__":
    banner("LLM WITH ONE LOOKUP TOOL")
    for question in QUESTIONS:
        messages = [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": question},
        ]
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=[TOOL], temperature=0
        )
        message = response.choices[0].message
        print(f"Q: {question}")

        if not message.tool_calls:
            print("Tool call: none")
            print(f"A: {message.content.strip()}\n")
            continue

        call = message.tool_calls[0]
        arguments = json.loads(call.function.arguments)
        result = lookup_course_fee(**arguments)
        print(f"Tool call: {call.function.name}({arguments})")
        print(f"Tool result: {result}")
        messages.append({
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": [{
                "id": call.id,
                "type": "function",
                "function": {
                    "name": call.function.name,
                    "arguments": call.function.arguments,
                },
            }],
        })
        messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
        final_response = client.chat.completions.create(
            model=MODEL, messages=messages, temperature=0
        )
        print(f"A: {final_response.choices[0].message.content.strip()}\n")
