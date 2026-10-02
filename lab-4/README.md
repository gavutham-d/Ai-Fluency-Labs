# Lab 4: VRAM and Model Memory Estimation

This folder contains a small utility for estimating how much memory a local language model will use and whether it is realistic to run on the current machine.

## What it does

The script evaluates:

- total system RAM
- available GPU VRAM when present
- CPU/GPU characteristics
- approximate memory usage for different model sizes and quantization levels
- a simple fit verdict such as:
  - fits comfortably
  - fits, but tight
  - does NOT fit

It is designed to help answer questions like:

- Can my machine run an 8B model locally?
- How much memory does a 30B model need?
- Does a quantized model fit better than FP16?
- How does context length affect memory use?

## Files

- `vram_estimate.py` — main script that detects hardware and estimates model compatibility

## Run it

From this folder, run:

```bash
python vram_estimate.py
```

## Example output

The script prints hardware detection and a compatibility benchmark for several model sizes, including different context lengths and precision settings.

It reports data such as:

- model name
- precision
- parameter count
- context length
- weights memory
- KV-cache memory
- total estimated memory usage
- fit recommendation

## Memory model assumptions

The script uses approximate rules based on common model formats:

- FP16 is roughly 2 bytes per parameter
- quantized formats such as Q4_K_M are much smaller
- KV-cache grows with model size and context window
- a small runtime overhead is added for activations and fragmentation

These are practical estimates rather than exact model-specific measurements.

## Notes

- This is intended for quick planning and rough feasibility checks.
- Actual runtime memory can vary by framework, backend, and batching behavior.
- For real workloads, benchmark with the exact runtime you plan to use.

## Use case

This lab is useful for understanding the memory budget needed for local inference and for comparing model choices before running heavier workloads.
