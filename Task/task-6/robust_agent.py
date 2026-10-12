"""Minimal defensive tool-calling loop for a small gardening helper."""
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

TASK_DIR = Path(__file__).resolve().parent
load_dotenv(TASK_DIR / ".env", override=True)
sys.path.append(str(TASK_DIR.parent.parent / "lab-1"))
from config import MODEL, PROVIDER, banner, client
from tools import SCHEMAS, TOOLS, TOOL_FUNCTIONS
from validate import validate_arguments

SYSTEM_PROMPT = (
    "You are a practical home-gardening helper. Use lookup_plant_care for seasonal care "
    "facts about supported plants. Use calculate_watering_volume for watering estimates "
    "when a pot size is given. Treat estimates as guidance and remind users to check soil "
    "moisture. For general gardening explanations, answer directly. Supported plants are basil, tomato, and mint."
)
INITIAL_MAX_TOKENS = 400
MAX_TOKEN_RETRIES = 2
REPEAT_LIMIT = 2


def handle_tool_call(call, log=True):
    """Parse, look up, validate, execute; always return a string, never leak errors."""
    tool_name = getattr(getattr(call, "function", None), "name", "")
    raw_arguments = getattr(getattr(call, "function", None), "arguments", "") or "{}"

    try:
        arguments = json.loads(raw_arguments)
    except (json.JSONDecodeError, TypeError) as error:
        return f"Argument error: invalid JSON ({error}). Expected a JSON object matching the schema for '{tool_name}'."

    function = TOOL_FUNCTIONS.get(tool_name)
    if function is None:
        return f"Unknown tool '{tool_name}'. Expected one of: {', '.join(TOOL_FUNCTIONS)}."

    problem = validate_arguments(arguments, SCHEMAS[tool_name])
    if problem:
        return f"Validation error: {problem}"

    try:
        result = str(function(**arguments))
    except Exception as error:
        result = f"Tool error: {type(error).__name__}: {error}. Check the arguments and try again."

    if log:
        print(f"      {tool_name}({arguments}) -> {result}")
    return result


def agent(question, max_steps=6, verbose=True):
    """Run bounded model/tool turns, returning each tool result by its call ID."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    seen_calls = {}
    max_tokens = INITIAL_MAX_TOKENS
    token_retries = 0

    for step in range(1, max_steps + 1):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            temperature=0,
            max_tokens=max_tokens,
        )
        choice = response.choices[0]
        message = choice.message

        if choice.finish_reason == "length":
            if token_retries >= MAX_TOKEN_RETRIES:
                return f"Stopped: reply remained truncated after {token_retries} larger-token retries."
            token_retries += 1
            max_tokens *= 2
            if verbose:
                print(f"   step {step}: reply truncated; retrying with max_tokens={max_tokens}")
            continue

        token_retries = 0
        if not message.tool_calls:
            return (message.content or "").strip()

        assistant_calls = []
        for call in message.tool_calls:
            assistant_calls.append({
                "id": call.id,
                "type": "function",
                "function": {
                    "name": call.function.name,
                    "arguments": call.function.arguments,
                },
            })
        messages.append({"role": "assistant", "content": message.content or "", "tool_calls": assistant_calls})

        if verbose:
            print(f"   step {step}: processing {len(message.tool_calls)} tool call(s)")

        repeated_call_seen = False
        for call in message.tool_calls:
            signature = (call.function.name, call.function.arguments)
            seen_calls[signature] = seen_calls.get(signature, 0) + 1
            if seen_calls[signature] >= REPEAT_LIMIT:
                result = (
                    f"Repeated call stopped: '{call.function.name}' with the same arguments "
                    f"was requested {seen_calls[signature]} times. Try a different valid call or answer from the available result."
                )
                repeated_call_seen = True
            else:
                result = handle_tool_call(call, log=verbose)

            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

        if repeated_call_seen:
            return "Stopped: the model repeated an identical tool call; its tool-result error was recorded."

    return "Stopped: maximum agent steps reached without a final answer."


if __name__ == "__main__":
    banner("GARDENING AGENT")
    if PROVIDER == "groq" and not os.getenv("GROQ_API_KEY"):
        raise SystemExit("GROQ_API_KEY is missing from Task/task-6/.env")
    questions = [
        "What care does basil need in summer?",
        "I have a 2-liter tomato pot. How much water should I use per watering?",
        "Why do plants need sunlight?",
    ]
    for question in questions:
        print(f"\nQ: {question}")
        print("A:", agent(question))
