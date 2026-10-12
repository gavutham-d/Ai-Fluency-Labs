# AI Fluency - Task 1: UPI Payment Setup Assistant

This project demonstrates the same three approaches as the day-1 lab, but applied to a small private-data scenario:

- A plain chatbot that responds using an LLM without direct access to private UPI information.
- A rule-based workflow that checks hard-coded setup rules and private account data.
- A tool-using AI agent that reasons, calls the right tools, and continues until the task is complete.

The chosen scenario is a private UPI payment setup assistant. The system must help a user determine whether a UPI ID is valid, whether the account is active, whether a payment fits within the daily limit, and whether a transfer amount is allowed before payment is attempted.

## Scenario

A mobile banking app stores a small private dataset:

- user name
- UPI ID
- linked bank
- daily transfer limit
- account status (active / pending / blocked)

This information is private and should not be guessed by a public LLM. The assistant may need to answer questions such as:

- What is the UPI ID for Alice?
- Which bank is linked to alice@okaxis?
- Can Alice pay Rs. 12,000 today?
- What is the total payable amount after a 1.5% fee on Rs. 5,000?

## Requirements

- Python 3.9 or newer
- An OpenAI-compatible model provider:
  - Ollama running locally, or
  - A Groq API key, or
  - A Hugging Face access token

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```dotenv
PROVIDER=ollama
MODEL=qwen2.5:1.5b
```

Then run:

```bash
ollama serve
ollama pull qwen2.5:1.5b
```

## Verify the setup

```bash
python check_setup.py
```

## Run the examples

```bash
python chatbot.py
python workflow.py
python agent.py
python challenge.py
```

You can inspect the tools directly:

```bash
python tools.py
```

## Private data used in the example

The private dataset is stored in `config.py` and is intentionally not available to a plain public chatbot:

```python
UPI_ACCOUNTS = {
    "alice": {"upi_id": "alice@okaxis", "bank": "Axis Bank", "daily_limit": 25000, "status": "active"},
    "bob": {"upi_id": "bob@paytm", "bank": "Paytm Payments Bank", "daily_limit": 10000, "status": "active"},
    "charlie": {"upi_id": "charlie@icici", "bank": "ICICI Bank", "daily_limit": 50000, "status": "pending"},
}
```

## How each approach works

### 1. Plain chatbot
A plain chatbot sends the user question to the model, which responds based on its general language understanding. It does not directly query the private UPI database unless the data has been injected into the prompt.

It requires:
- an LLM provider
- a prompt
- optional system instructions

It handles the request by generating text. It can answer in a natural style, but it cannot safely or reliably access hidden account data. In a real system, this would be a security risk.

Limitations:
- no guaranteed access to private UPI records
- can hallucinate a UPI ID, bank, or payment rule
- cannot verify real limits or account status

### 2. Rule-based workflow
A rule-based workflow checks the user request using fixed rules and private data stored in code. It reads the user input, extracts names or UPI IDs, looks up data from the secret dictionary, and follows a sequence of if/else conditions.

It requires:
- a private lookup dataset
- regex or string parsing
- fixed business rules

It handles the request by following predetermined logic such as:
- if account is inactive, reject the payment
- if amount exceeds limit, deny the transaction
- if a valid UPI ID is found, return the linked bank and limit

Limitations:
- only handles known patterns
- breaks down for unanticipated questions
- does not improvise or reason beyond the rules

### 3. AI agent with tools and a loop
An AI agent uses an LLM to decide what to do, but it is not limited to guessing. It can call tools such as `get_upi_profile`, `get_daily_limit`, and `calculator`, inspect the returned results, and continue looping until the task is complete.

It requires:
- an LLM model
- tool schemas
- private lookup functions
- an execution loop

It handles the request by reasoning step-by-step:
1. identify the needed fact
2. call the correct tool
3. look at the returned result
4. combine results with arithmetic or logic
5. continue until a final answer is produced

Limitations:
- depends on tool design and call quality
- may loop if the task is poorly specified
- still needs careful prompt design and safe tools

## Comparison of the three approaches

| Dimension | Plain chatbot | Rule-based workflow | AI agent |
| --- | --- | --- | --- |
| Flexibility | High language flexibility | Low; depends on known patterns | High, but bounded by tools |
| Decision-making | LLM reasoning only | Fixed if/else logic | LLM + tools + loop |
| Tool usage | Usually none | None or very limited | Uses explicit tools for data and math |
| Private-data access | Unsafe unless provided explicitly | Direct, controlled access to private data | Direct, controlled access via tools |
| Multi-step task handling | Weak unless prompted carefully | Limited to predefined paths | Strong: tool loop continues until task is done |
| Automation | Low to medium | High for repetitive known tasks | High for dynamic tasks |
| Reliability | Lower, can hallucinate | High for expected patterns | High when tools are correct and prompts are clear |

## Why the AI agent is best for this scenario

This scenario needs both private-data access and decisions based on real values. The plain chatbot cannot be trusted with hidden UPI records. The workflow is reliable for known requests, but it fails when the user asks something more natural or slightly different. The AI agent is the best choice because it combines the best parts of both:

- it uses an LLM to understand the question
- it uses safe tools to read account data and perform arithmetic
- it observes the results and continues until the task is finished

For example, if the user asks: "Alice wants to pay Rs. 15,000; can she send it from her active UPI setup, and what is the total after a 1.5% payment fee?" the agent can:

1. call `get_upi_profile("alice")`
2. read the daily limit and account status
3. compare the amount with the limit
4. call `calculator("15000 * 1.015")`
5. produce the final answer with logic and evidence

This is exactly the kind of task where the agent does better than both a plain chatbot and a fixed workflow.

## When to choose each approach

- Use a chatbot when the task is mostly conversational, does not require private data, and can tolerate general knowledge answers.
- Use a rule-based workflow when the problem has fixed steps, known inputs, and highly predictable output.
- Use an AI agent when the task requires reasoning, private data access, multi-step actions, arithmetic, and tool-driven execution.

## Project structure

| File | Purpose |
| --- | --- |
| `config.py` | Loads provider settings and private UPI account data |
| `check_setup.py` | Verifies the model is reachable |
| `chatbot.py` | Plain LLM chatbot |
| `workflow.py` | Rule-based UPI validation workflow |
| `agent.py` | AI agent with tool-calling loop |
| `tools.py` | Private lookup and calculator tools |
| `challenge.py` | Harder UPI question for comparison |
| `requirements.txt` | Python dependencies |

## Conclusion

A plain chatbot mainly provides responses using an LLM. A rule-based workflow follows predefined steps and conditions. An AI agent combines an LLM + Tools + Loop to reason about the task, choose the relevant tools, observe the result, and continue taking actions until the task is done.

For the UPI payment setup scenario, the AI agent is the most suitable choice because it handles private data, arithmetic, and task completion reliably, while the chatbot and workflow each have clear limitations.
