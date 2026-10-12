"""Ask the same reasoning question several times and compare final answers."""
from collections import Counter
from config import client, MODEL, banner
from cot_compare import COT_PROMPT

QUESTION = "A flight costs Rs. 7,200. Add a 10% booking fee and divide the total into 3 equal payments. What is each payment?"


def final_answer(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[-1] if lines else "(empty)"


def run_many(question, runs=5):
    answers = []
    for attempt in range(1, runs + 1):
        response = client.chat.completions.create(model=MODEL, messages=[{"role": "system", "content": COT_PROMPT}, {"role": "user", "content": question}], temperature=0.8)
        answer = final_answer(response.choices[0].message.content)
        print(f"run {attempt}: {answer}")
        answers.append(answer)
    return answers


if __name__ == "__main__":
    banner("SELF-CONSISTENCY")
    answers = run_many(QUESTION)
    winner, count = Counter(answers).most_common(1)[0]
    print(f"Majority answer ({count} of {len(answers)}): {winner}")
