Analysis of Model Selection Concepts

The scenario is local text generation on a machine with limited GPU
memory. The goal is to choose an open model that can generate text
locally while fitting the available memory and being permitted for the
intended use.

The analysis compares three candidate models:
Model             Parameters Quantization     Context Licence

Qwen 2.5 1.5B           1.5B Q4_K_M                8K Apache-2.0
Qwen 2.5 7B               7B Q4_K_M                8K Apache-2.0
Llama 3.1 8B              8B Q4_K_M                8K Llama 3.1 Community License

The Python program estimates memory before downloading a model and then
allows an actual local inference test.

1. Model Weights
What it is: Model weights are the learned numerical values stored in
the model. Their memory requirement is primarily determined by the
number of parameters and the precision used to represent each parameter.

Fit or permission: Weights control fit. They do not determine
whether the model is legally permitted for a particular use.
How it was used: The program estimates weight memory as:
weight memory ≈ parameter count × bytes per parameter
For example, an 8B model at FP16 uses approximately:
8B × 2 bytes ≈ 16 GB
With Q4_K_M, the program uses an effective rate of about 0.57
bytes/parameter:
8B × 0.57 ≈ 4.56 GB

Therefore, the same model has approximately the same number of
parameters but requires much less memory after quantization.

If ignored: A model may be downloaded successfully but fail during
inference because there is not enough RAM or VRAM to load its weights.

Limitation in this scenario: The estimate does not include every
implementation-specific allocation. The actual loaded model can use more
memory because of runtime buffers, activations, allocator behaviour and
other overhead.

2. Quantization
What it is: Quantization represents model weights with fewer bits.
Examples include FP16, Q8_0, Q6_K, Q5_K_M and Q4_K_M.
Fit or permission: Quantization primarily affects fit. It does
not grant additional licence rights.
How it was used: The program compares different effective
bytes-per-parameter values. For the 8B model, approximately:

FP16: 8 × 2.00 = 16.00 GB of weights
Q8_0: 8 × 1.00 = 8.00 GB
Q5_K_M: 8 × 0.68 = 5.44 GB
Q4_K_M: 8 × 0.57 = 4.56 GB
Q3_K_M: 8 × 0.43 = 3.44 GB

This demonstrates that quantization can make a model that is too large
at FP16 usable at a lower precision.

If ignored: A model can appear impossible to run when a suitable
quantized version would fit. Conversely, using very aggressive
quantization without considering quality can reduce output quality or
task performance.

Limitation in this scenario: Quantization does not remove the
model's computational requirements and does not guarantee the same
quality as the original precision. The effective bytes-per-parameter
values are also estimates because quantization formats contain metadata
and implementation-specific overhead.

3. KV Cache and Context Length
What it is: The KV cache stores intermediate attention information
from previous tokens so an autoregressive model does not have to
recompute the entire previous conversation for every new token.

Fit or permission: KV cache and context length affect fit.

How it was used: The program estimates KV-cache memory using a rough
architecture-dependent heuristic:

KV cache ≈ parameters × context(K) × 0.02 GB per 1B parameters per 1K tokens

For an 8B model:
4K context → approximately 0.64 GB
8K context → approximately 1.28 GB
32K context → approximately 5.12 GB
128K context → approximately 20.48 GB

The important observation is that the weights do not increase when
context length increases, but the KV cache does.

This matters for an agent that continually adds conversation history and
tool results. A model that fits at 4K or 8K can stop fitting when the
active context becomes 32K or 128K.

If ignored: A model may load successfully but run out of memory as
the conversation grows.

Limitation in this scenario: The KV-cache formula is only a rough
estimate. Actual KV memory depends on architecture, number of layers, KV
heads, head dimension, cache datatype and inference runtime. Therefore,
the calculated number should be used to decide whether a model is likely
to fit, not as a megabyte-accurate prediction.

4. Model Card
What it is: A model card documents important information about a
model, including its intended use, architecture, parameters, context
information, limitations, and licensing information or links to the
applicable licence.

Fit or permission: A model card supports decisions about both fit
and permission. Technical information helps estimate memory, while the
licence information helps determine whether the intended use is allowed.

How it was used: The model cards were used to identify the candidate
models, their parameter sizes, context capabilities and applicable
licence names. The exact licence was then included in the comparison
table rather than assuming that every "open" model has the same
permissions.

If ignored: A technically suitable model could be selected without
understanding its restrictions, intended-use limitations or licence
obligations.

Limitation in this scenario: A model card is documentation, not a
guarantee that every possible use is permitted. The actual licence text
and its conditions control the legal terms.

5. Open-Weight vs Open-Source Licensing
What it is: An open-weight model makes its trained weights
available, but that does not automatically mean its software, training
data, or usage rights satisfy the usual definition of open source.
Different models can impose different licence conditions.

Fit or permission: Licensing controls permission, not hardware
fit.

How it was used: The comparison distinguishes:
Qwen 2.5: Apache-2.0
Llama 3.1: Llama 3.1 Community License

Apache-2.0 is a standard permissive open-source licence with conditions
such as retaining copyright and licence notices. The Llama 3.1 Community
License contains additional model-specific terms, so it must be checked
separately rather than treating it as identical to Apache-2.0.

Therefore, model size alone cannot determine the final choice. A model
can fit the machine but still require licence review before commercial
use or redistribution.

If ignored: A developer could deploy or redistribute a model without
satisfying its licence conditions.

Limitation in this scenario: Licence suitability depends on the
actual intended use. The licence comparison in this analysis is
therefore scenario-specific and should not be treated as general legal
advice.

3.6 Suitability Analysis

For the stated scenario, **Qwen 2.5 1.5B Q4_K_M with 8K context** is selected under the **Apache-2.0 licence**.

Its estimated memory usage is:

* **Parameters:** 1.5B
* **Weight estimate:** 1.5 × 0.57 ≈ **0.86 GB**
* **KV-cache:** 1.5 × 8 × 0.02 ≈ **0.24 GB**
* **Estimated total with 10% overhead:** **≈ 1.21 GB**

This provides more memory headroom than the larger candidates.

**Runner-up:** Qwen 2.5 7B Q4_K_M with 8K context. It offers greater capacity but requires significantly more memory, making it less suitable for the constrained hardware. Llama 3.1 8B has a similar memory requirement and uses the Llama 3.1 Community License, so its permissions must be reviewed separately.

The recommendation could change if:

* **More memory** is available → 7B/8B models become practical.
* **Commercial or public release** is required → licence terms become more important.
* **Longer context** is required → KV-cache growth becomes significant.
* **Advanced tool-calling/agent tasks** are required → a larger model may be preferred.

Therefore, the final choice depends on **hardware fit, context needs, model capability, and licence permissions**.


3.6 Conclusion

Model selection depends on the situation:

* **Size:** Most important when hardware memory is limited.
* **Quantization:** Useful when a model is too large; lower precision reduces memory with possible quality trade-offs.
* **Context length:** Important for long conversations or agents, because KV-cache memory grows with context.
* **Licence:** Decisive when commercial use, redistribution, or deployment restrictions matter.

Overall:

**Hardware fit → quantization → context/KV cache → runtime validation → licence compatibility**

Memory calculations are estimates, not exact predictions, since actual usage depends on the model architecture and runtime. Also, **open-weight does not automatically mean open-source or unrestricted**; the exact licence must always be checked.