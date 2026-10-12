# Task 3: Plain LLM vs. One Tool

This small experiment compares the same three questions sent to a plain language model and to a model that can use one external tool: a local lookup of Greenfield College's private course-fee table.

## Scenario

The college's fee table is application-specific information. It is stored in `course_fees.json` and is not general knowledge a model can reliably infer. The model can still answer broad questions, such as explaining the difference between a fee and a fine, or write a welcome message without any tool.

## What the comparison shows

A large language model (LLM) generates text based on patterns learned during training and the context supplied in the prompt. A plain prompt lets the model answer immediately, but does not itself give it access to current information, local files, private records, or a calculation service. It can sometimes reason or calculate in text, but those results are not an authoritative lookup or a guaranteed execution.

A **tool** is a function the application makes available to the model, together with a description of what it does and the inputs it accepts. A **tool call** is the model's structured request to run that function with particular arguments. The application executes the function and sends its result back to the model, which then produces a final answer. The model does not execute the function by itself.

Here, the single `lookup_course_fee` tool reads the local JSON file. The model is instructed to call it for a Greenfield course fee and to answer general or creative questions directly. That makes the private fee answer grounded in the fee table, while avoiding an unnecessary tool call for questions the model can reasonably answer itself. Tool access improves reliability for information that the model cannot know from its training, but it does not guarantee correctness for every part of an answer; the model still has to choose the right tool, arguments, and interpretation.

## Setup

The scripts reuse the shared OpenAI-compatible client in `lab-1/config.py`. From this directory, create/activate a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Configure the provider and model in this directory's local `.env`, following `lab-1/README.md`. Supported provider choices are Ollama, Groq, and Hugging Face. Keep API keys in `.env`; do not put them in source files or recorded reports.

## Run

Run both comparisons from `Task/task-3` so the shared config loads this directory's `.env`:

```bash
python plain_llm.py
python tool_llm.py
```

Both scripts ask the same three questions. `plain_llm.py` sends only system and user messages. `tool_llm.py` advertises only `lookup_course_fee`, prints any tool call and result, then sends the result back for the model's final answer. The expected tool use is one lookup for the AI202 fee and no lookup for the general explanation or welcome message.

## Observations

See `results.md` for the captured answers and a question-by-question assessment of the plain and tool-enabled runs. The comparison distinguishes correct answers from guesses, refusals, and confidently wrong answers, and notes whether the tool-enabled model called and used the lookup correctly.
