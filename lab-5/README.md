# AI Fluency Lab 5

This directory is a small LLM experimentation workspace focused on model access, benchmarking, and prompt testing using both local Ollama-style patterns and the Groq OpenAI-compatible API.

## What is in this lab?

- `api_demo.py` — a simple API demo that calls a Groq model and prints the response.
- `bench_models.py` — compares multiple models on the same prompts and reports timing and token output.
- `Modelfile` — a custom local model profile for a college fee-assistant persona.
- `Modelfile.creative` — a second custom profile for a more enthusiastic event announcer persona.
- `requirements.txt` — Python dependencies for the scripts.

## Purpose

The lab demonstrates:

- calling a hosted LLM API using an OpenAI-compatible endpoint
- benchmarking model behavior across multiple prompts
- comparing model personalities using custom `Modelfile` definitions
- keeping the local Ollama examples available as commented code for optional offline testing

## Prerequisites

Before running the scripts, make sure you have:

- Python 3.10+
- A Groq API key
- Optional: Ollama installed locally if you want to use the commented local examples

## Setup

1. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in this folder with your Groq settings:

```env
GROQ_API_KEY=your_groq_api_key_here
MODEL=llama3-8b-8192
MODEL2=qwen/qwen3.8-27b
MODEL3=llama-3.3-70b-versatile
MODEL4=openai/gpt-oss-120b
```

> The scripts read `GROQ_API_KEY` and optionally use `MODEL`, `MODEL2`, `MODEL3`, and `MODEL4` values from the environment.

## Run the API demo

```bash
python api_demo.py
```

This script sends a prompt to the Groq API and prints the generated response.

## Run the model benchmark

```bash
python bench_models.py
```

This script runs a few prompts against several configured models and prints timing information such as:

- elapsed time
- token count
- token-per-second rate
- response text preview

## Local Ollama usage

The scripts include commented-out local Ollama examples. If you want to use them instead:

1. Start Ollama locally.
2. Pull a model such as `qwen2.5:1.5b`.
3. Uncomment the relevant section in the script.

Example local model creation from the `Modelfile`:

```bash
ollama create fee-assistant -f Modelfile
ollama run fee-assistant
```

Example for the creative profile:

```bash
ollama create creative-bot -f Modelfile.creative
ollama run creative-bot
```

## Notes

- The main active code path uses Groq's OpenAI-compatible endpoint.
- The local Ollama code is intentionally left commented so the directory remains easy to run against the hosted API.
- The benchmark file is useful for testing prompt robustness and comparing model response styles under the same conditions.

## Troubleshooting

If the scripts fail:

- check that your `.env` file exists and contains a valid `GROQ_API_KEY`
- confirm your Python environment has installed the dependencies from `requirements.txt`
- verify the model names in `MODEL`, `MODEL2`, `MODEL3`, and `MODEL4` are valid for Groq
- if using Ollama locally, ensure the service is running on `http://localhost:11434`

## Summary

This lab is a lightweight introduction to model APIs and model comparison. It is designed for hands-on experimentation with prompt testing, quick benchmarking, and simple custom persona configuration.
