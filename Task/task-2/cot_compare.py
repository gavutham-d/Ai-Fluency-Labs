"""Compare direct prompting with a step-by-step Chain-of-Thought prompt."""
from config import client, MODEL, banner

QUESTIONS = [
    "A flight costs Rs. 7,200. Add a 10% booking fee, then split the payment into 3 equal instalments. What is each instalment?",
    "I need to travel on 2026-10-15, spend less than Rs. 8,000, and have at least 15 kg baggage. Which listed flight qualifies?",
    "My flight departs at 06:30 and takes 2 hours 45 minutes. What time does it arrive?",
]

DIRECT_PROMPT = "Give only the final answer. Do not explain."
COT_PROMPT = "Solve the problem step by step, show the calculations, then write a final answer."


def ask(system_prompt, question):
    response = client.chat.completions.create(model=MODEL, messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": question}], temperature=0)
    return response.choices[0].message.content.strip()


if __name__ == "__main__":
    banner("CHAIN-OF-THOUGHT COMPARISON")
    for number, question in enumerate(QUESTIONS, start=1):
        print(f"QUESTION {number}: {question}\n")
        print("--- DIRECT ---")
        print(ask(DIRECT_PROMPT, question))
        print("--- CHAIN OF THOUGHT ---")
        print(ask(COT_PROMPT, question))
        print("-" * 70)
