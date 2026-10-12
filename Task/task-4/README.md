# Task 4: Model Memory Analyzer

This folder contains a practical Python project for estimating whether a local language model can run on the current machine. The script checks available RAM and GPU VRAM, compares model candidates, and estimates the memory footprint of weights, quantization, and KV-cache usage at different context lengths. In other words, it helps answer the question: “Will this model fit my hardware before I download it?”

The project focuses on real-world decision-making rather than abstract theory. It looks at Qwen 2.5 and Llama models, compares relevant licensing terms, and highlights that technical fit and legal permission are separate concerns. A model may be perfectly usable on hardware but still not be compliant for a targeted deployment, especially when licensing conditions differ across model families.

The analyzer also demonstrates why quantization matters. Moving from higher-precision formats to smaller effective byte-per-parameter representations can dramatically reduce memory use. At the same time, increasing the context window raises KV-cache demand, which can make a model that fits at 8K context fail at 32K or 128K. This is especially important for agents that maintain long histories or accumulate tool outputs and chat context over time.

For the scenario in this task, the recommended choice is Qwen 2.5 1.5B at Q4_K_M with an 8K context. It offers a strong balance between usable memory, manageable context overhead, and a permissive Apache-2.0 licence. Larger models may provide more capability, but they consume much more memory and are less comfortable on constrained devices.

## Run the analyzer
```bash
python3 model_memory_analyzer.py
```

## Files in this folder
- model_memory_analyzer.py — main script that detects hardware and estimates model fit
- analysis.md — short summary of the decision process and findings
