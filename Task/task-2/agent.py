"""ReAct agent: interleaves model reasoning, tool actions, and observations."""
import json
from config import client, MODEL, banner
from tools import TOOLS, TOOL_FUNCTIONS

SYSTEM_PROMPT = ("You are a flight-booking assistant. Use search_flights for current flight facts; never guess prices or schedules. "
                 "Use calculator for arithmetic. Airport codes are used by the search tool.")


def agent(question, max_steps=6, verbose=True):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": question}]
    for step in range(1, max_steps + 1):
        response = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS, temperature=0)
        message = response.choices[0].message
        if not message.tool_calls:
            return message.content.strip()
        messages.append({"role": "assistant", "content": message.content or "", "tool_calls": [{"id": call.id, "type": "function", "function": {"name": call.function.name, "arguments": call.function.arguments}} for call in message.tool_calls]})
        for call in message.tool_calls:
            name = call.function.name
            arguments = json.loads(call.function.arguments or "{}")
            function = TOOL_FUNCTIONS.get(name)
            result = function(**arguments) if function else f"Unknown tool: {name}"
            if verbose:
                print(f"step {step}: Action {name}({arguments}) -> Observation {result}")
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
    return "Stopped: maximum steps reached without a final answer."


if __name__ == "__main__":
    banner("REACT AGENT")
    print(agent("Find the cheapest BLR to DEL flight on 2026-10-15 and calculate its price after a 10% booking fee."))
