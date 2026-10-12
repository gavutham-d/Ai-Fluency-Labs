"""Show the ReAct agent's Action and Observation trace."""
from agent import agent

QUESTION = "Which BLR to DEL flight on 2026-10-15 is cheapest, and does it include at least 15 kg baggage?"
print("QUESTION:", QUESTION)
print("--- REACT TRACE ---")
print("FINAL ANSWER:", agent(QUESTION, max_steps=8))
