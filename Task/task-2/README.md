# Task 2: Flight Booking and AI Reasoning

This mini-project demonstrates three ways to handle flight-booking questions:

1. **Direct prompting**: ask the language model for an answer immediately.
2. **Chain-of-Thought prompting**: ask the model to work through the problem step by step.
3. **ReAct**: let the model alternate between reasoning, calling tools, reading observations, and producing a final answer.

The example uses flights from Bengaluru (`BLR`) to Delhi (`DEL`) on `2026-10-15`. The flight search is a **simulated external service** in `tools.py`, so the project can run without a real airline API. In a production application, that function would call a live flight provider.

## Setup

From this directory, install the dependencies:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your provider settings. You can use Groq, Hugging Face, or a local Ollama model. Do not commit real API keys.

## Run the Examples

```bash
python cot_compare.py
python react_trace.py
python self_consistency.py
```

## What Each Approach Does

### Direct prompting

`cot_compare.py` includes a direct prompt that sends one request and returns the answer. There is no visible reasoning and no tool call. It is fast and simple, but it cannot look up a current flight price or schedule. If the model was not given the flight facts, it may guess or invent them.

### Chain-of-Thought prompting

`cot_compare.py` asks the model to break a reasoning problem into steps before giving a final answer. This can help with arithmetic, constraints, and time calculations. However, step-by-step instructions do not give the model new information. It still cannot fetch an unknown flight price or schedule without a tool.

The file compares a direct prompt and a step-by-step prompt on the same questions, making the difference visible.

### ReAct agent

`agent.py` follows the ReAct pattern:

1. **Thought**: decide what information or calculation is needed.
2. **Action**: call `search_flights` or `calculator`.
3. **Observation**: receive the tool result.
4. Repeat if needed, then give a final answer.

`react_trace.py` prints the tool actions and observations. ReAct is the only approach here that can use external flight facts before answering.

## Comparison

| Measure | Direct prompting | Chain-of-Thought | ReAct agent |
| --- | --- | --- | --- |
| Reasoning depth | Low; asks for an answer immediately | Higher for multi-step problems | High when several actions are needed |
| Tool use | None | None in this example | Searches flights and calculates totals |
| Reliability | Depends strongly on model knowledge | Better arithmetic, but can still invent missing facts | Better for facts when the tool is accurate |
| Transparency | Final answer only | Visible written steps in this exercise | Action and observation trace is visible |
| Cost and speed | Usually lowest and fastest | More output tokens and slower | Highest cost and latency when tools are called |
| Repeated-run consistency | Often consistent at temperature 0 | Can vary when sampling is enabled | Can vary in tool choice and wording |

## Limitations Shown by the Scenario

- Direct prompting may answer a flight-search question confidently without knowing the real schedule.
- Chain-of-Thought can calculate a booking fee correctly, but it cannot discover a flight that was not included in its prompt.
- ReAct depends on the tool returning correct, current data. It can also fail if it chooses the wrong tool, sends invalid arguments, or reaches its step limit.
- Self-consistency in `self_consistency.py` selects the most common answer across runs. A majority answer can still be wrong if the model repeatedly makes the same mistake.
- The simulated data is not a real booking inventory. Never use this example to purchase a ticket.

## Which Approach Should Be Used?

- Use **direct prompting** for simple writing, summaries, or questions where all required facts are already in the prompt.
- Use **Chain-of-Thought-style prompting** for careful arithmetic, comparisons, and logic when the facts are already available. In real applications, it is usually better to request a concise explanation or structured result rather than expose private internal reasoning.
- Use **ReAct** for tasks that need external information, calculations, database access, or multiple steps. Flight search is a good example because prices and schedules must come from a booking source.

The main lesson is that better prompting can improve reasoning, but only tools can provide information the model does not have.

## File Guide

| File | Purpose |
| --- | --- |
| `config.py` | Provider settings and shared questions. |
| `tools.py` | Simulated flight search, calculator, and tool schemas. |
| `cot_compare.py` | Direct versus Chain-of-Thought comparison. |
| `agent.py` | ReAct agent implementation. |
| `react_trace.py` | Prints the agent's actions and observations. |
| `self_consistency.py` | Repeats a reasoning prompt and compares answers. |
