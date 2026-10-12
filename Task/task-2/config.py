"""Shared configuration and flight-booking data for Task 2."""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

PROVIDER = os.getenv("PROVIDER", "ollama").strip().lower()

if PROVIDER == "ollama":
    BASE_URL = "http://localhost:11434/v1"
    API_KEY = "ollama"
    MODEL = os.getenv("MODEL", "qwen2.5:1.5b")
elif PROVIDER == "groq":
    BASE_URL = "https://api.groq.com/openai/v1"
    API_KEY = os.getenv("GROQ_API_KEY")
    MODEL = os.getenv("MODEL", "openai/gpt-oss-20b")
elif PROVIDER == "huggingface":
    BASE_URL = "https://router.huggingface.co/v1"
    API_KEY = os.getenv("HF_TOKEN")
    MODEL = os.getenv("MODEL", "openai/gpt-oss-20b")
else:
    raise SystemExit("Unknown PROVIDER. Use ollama, groq, or huggingface.")

if not API_KEY:
    raise SystemExit(f"No API key found for PROVIDER={PROVIDER}. Check your .env file.")

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

QUESTIONS = [
    "Which flight from Bengaluru to Delhi is cheapest on 2026-10-15?",
    "Can I book a flight from Bengaluru to Delhi on 2026-10-15 for less than Rs. 8,000?",
    "If I choose the cheapest flight and pay a 10% booking fee, what is the total?",
    "Can I take a 20 kg checked bag if my ticket includes 15 kg baggage?",
]


def banner(name):
    print(f"\n=== {name} | provider: {PROVIDER} | model: {MODEL} ===\n")
