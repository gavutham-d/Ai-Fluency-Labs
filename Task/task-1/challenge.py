"""A question none of the three systems was designed for."""
from agent import agent
from workflow import workflow

QUESTION = "Alice wants to transfer Rs. 22,000. Is her UPI setup sufficient, and what will the total be after a 1.5% fee?"

print("Q:", QUESTION)
print("\nWorkflow :", workflow(QUESTION))
print("\nAgent    :", agent(QUESTION))
