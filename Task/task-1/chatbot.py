"""System 1: a plain LLM chatbot. No tools, no access to the private UPI data."""
from config import QUESTIONS, banner, client, MODEL


def chatbot(question):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful UPI support assistant. Be careful not to claim private account details unless they are provided in the conversation."},
            {"role": "user", "content": question},
        ],
        temperature=0,
    )
    return response.choices[0].message.content.strip()


if __name__ == "__main__":
    banner("SYSTEM 1: CHATBOT")
    for question in QUESTIONS:
        print("Q:", question)
        print("A:", chatbot(question))
        print("-" * 70)
