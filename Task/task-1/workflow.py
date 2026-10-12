"""System 2: a rule-based workflow. Fixed if/else rules, no LLM at all."""
import re

from config import QUESTIONS, UPI_ACCOUNTS


def workflow(question):
    text = question.lower()

    if "upi id" in text or "upi" in text and "which" in text:
        for name, data in UPI_ACCOUNTS.items():
            if name in text:
                return f"{name.title()}'s UPI ID is {data['upi_id']}."
        return "I can only answer for known UPI users in this dataset."

    match = re.search(r"([a-z]+)\s*[@]", question.lower())
    if match:
        upi_id = match.group(0).strip()
        for data in UPI_ACCOUNTS.values():
            if data["upi_id"].lower() == upi_id.lower():
                return f"The bank linked to {upi_id} is {data['bank']}."

    for name, data in UPI_ACCOUNTS.items():
        if name in text:
            amount_match = re.search(r"rs\.?\s*(\d+(?:,\d{3})*(?:\.\d+)?)", question, flags=re.IGNORECASE)
            if amount_match:
                amount = float(amount_match.group(1).replace(",", ""))
                if data["status"] != "active":
                    return f"{name.title()}'s UPI account is {data['status']} and cannot send payments right now."
                if amount > data["daily_limit"]:
                    return f"{name.title()} cannot send Rs. {amount:,.0f} because the daily UPI limit is Rs. {data['daily_limit']:,}."
                return f"{name.title()} can send Rs. {amount:,.0f} using the active UPI setup."

            return f"{name.title()}'s UPI details: {data['upi_id']} | {data['bank']} | daily limit Rs. {data['daily_limit']:,} | status: {data['status']}."

    if "pay" in text or "payment" in text:
        return "Sorry, I can only validate UPI accounts that are stored in the private setup list."

    return "Sorry, I do not have a rule for this type of UPI setup question."


if __name__ == "__main__":
    print("\n=== SYSTEM 2: RULE-BASED WORKFLOW (no LLM) ===\n")
    for question in QUESTIONS:
        print("Q:", question)
        print("A:", workflow(question))
        print("-" * 70)
