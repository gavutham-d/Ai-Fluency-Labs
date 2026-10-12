"""Ask the model directly without giving it access to tools."""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"), override=True)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "lab-1")))
from config import MODEL, banner, client

QUESTIONS = [
    "According to our private Greenfield course fee table, what is the fee for AI202?",
    "What is the difference between a course fee and a fine?",
    "Write a friendly two-line welcome message for new AI students.",
]

SYSTEM = (
    "You are a helpful assistant. Answer from your trained knowledge and the conversation only. "
    "You have no access to files, external services, or tools. If you do not know a private fact, "
    "say so rather than inventing it."
)

if __name__ == "__main__":
    banner("PLAIN LLM (no tools)")
    for question in QUESTIONS:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": SYSTEM},
                      {"role": "user", "content": question}],
            temperature=0,
        )
        print(f"Q: {question}")
        print(f"A: {response.choices[0].message.content.strip()}\n")
