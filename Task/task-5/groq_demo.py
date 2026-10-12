"""Run the TrailMate behavior experiment through the Groq chat-completions API."""
import json
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"), override=True)

BASE_URL = "https://api.groq.com/openai/v1/chat/completions"
API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("MODEL", "qwen/qwen3.8-27b")

DEFAULT_SYSTEM = (
    "You are TrailMate, a calm and practical overnight camping assistant. "
    "Keep replies to 3-5 concise bullet points. For any forecast at or below 0 degrees "
    "Celsius, explicitly recommend a sleeping bag rated for that temperature or colder, "
    "an insulated sleeping pad, and warm base layers. Do not claim to know live weather; "
    "use only details given by the user. If key conditions are missing, ask one short question."
)
OVERRIDE_SYSTEM = (
    "You are a formal public weather-service bulletin writer. Respond in one formal paragraph, "
    "with no bullets, and do not use the TrailMate camping-assistant voice."
)
PROMPTS = [
    "I'm camping overnight and the forecast is -3 degrees Celsius. What should I pack?",
    "What is one practical way to reduce condensation inside a tent?",
    "What is 2 + 2?",
]


def completion_request(prompt, system, stream):
    if not API_KEY:
        raise SystemExit("GROQ_API_KEY is missing from Task/task-5/.env")

    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "stream": stream,
    }
    if stream:
        body["stream_options"] = {"include_usage": True}

    start = time.perf_counter()
    response = requests.post(
        BASE_URL,
        headers={"Authorization": f"Bearer {API_KEY}"},
        json=body,
        stream=stream,
        timeout=180,
    )
    response.raise_for_status()

    first_piece_at = None
    pieces = []
    usage = {}
    if stream:
        for line in response.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data: "):
                continue
            data = line[6:]
            if data == "[DONE]":
                continue
            chunk = json.loads(data)
            if chunk.get("usage"):
                usage = chunk["usage"]
            choices = chunk.get("choices", [])
            if not choices:
                continue
            piece = choices[0].get("delta", {}).get("content") or ""
            if piece and first_piece_at is None:
                first_piece_at = time.perf_counter() - start
            pieces.append(piece)
    else:
        payload = response.json()
        pieces.append(payload["choices"][0]["message"]["content"] or "")
        usage = payload.get("usage", {})

    total_seconds = time.perf_counter() - start
    ttft_seconds = first_piece_at
    generated_tokens = usage.get("completion_tokens")
    generation_seconds = (
        total_seconds - ttft_seconds if ttft_seconds is not None else total_seconds
    )
    tokens_per_second = (
        generated_tokens / generation_seconds
        if generated_tokens is not None and generation_seconds > 0
        else None
    )
    return {
        "answer": "".join(pieces).strip(),
        "tokens": generated_tokens,
        "tokens_per_second": tokens_per_second,
        "ttft_seconds": ttft_seconds,
        "total_seconds": total_seconds,
    }


def run_case(number, prompt, stream, system=DEFAULT_SYSTEM, label=None):
    result = completion_request(prompt, system, stream)
    ttft = "N/A (non-streaming)" if result["ttft_seconds"] is None else f"{result['ttft_seconds']:.3f} s"
    rate = "N/A" if result["tokens_per_second"] is None else f"{result['tokens_per_second']:.2f} tokens/s"
    print(f"\nRun {number}: {label or prompt}")
    print(f"Mode: {'streaming' if stream else 'non-streaming'}")
    print(f"Model: {MODEL}")
    print(f"Completion tokens: {result['tokens'] if result['tokens'] is not None else 'not provided'}")
    print(f"Tokens per second: {rate}")
    print(f"TTFT: {ttft}")
    print(f"Total time: {result['total_seconds']:.3f} s")
    print(f"Answer: {result['answer']}")
    return result


if __name__ == "__main__":
    print(f"Provider: Groq | model: {MODEL}")
    print("Behavior default: TrailMate system prompt in this client (Groq does not load Modelfiles).")

    run_case(1, PROMPTS[0], stream=False, label="Cold-weather rules test")
    run_case(2, PROMPTS[1], stream=True, label="Tent condensation, first run")
    run_case(3, PROMPTS[2], stream=True, label="Simple arithmetic")
    run_case(4, PROMPTS[1], stream=True, label="Tent condensation, repeated run")
    run_case(5, PROMPTS[0], stream=True, system=OVERRIDE_SYSTEM,
             label="Cold-weather prompt with program system-prompt override")

    print("\nResidency/load note: Groq's public chat API does not expose Ollama /api/ps or per-model load_duration.")