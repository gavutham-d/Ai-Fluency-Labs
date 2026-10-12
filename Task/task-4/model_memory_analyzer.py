import os
import platform
import subprocess
import ctypes
import json
import time
import urllib.request

"""
TEXT GENERATION MODEL ANALYZER

Purpose:
1. Detect machine memory / GPU.
2. Estimate model memory before downloading.
3. Demonstrate the effect of quantization.
4. Demonstrate the effect of context length on KV cache.
5. Compare three open models and their licences.
6. Optionally run an actual model using Ollama.
7. Compare estimated vs actual memory.

The memory formula is an ESTIMATE.
Actual memory depends on the inference runtime,
activations, buffers, CUDA/driver overhead, etc.
"""


# ============================================================
# CONFIGURATION
# ============================================================

# Approximate effective bytes per parameter.
# These are suitable for rough pre-download estimation.
BYTES_PER_PARAM = {
    "FP32": 4.00,
    "FP16": 2.00,
    "Q8_0": 1.00,
    "Q6_K": 0.81,
    "Q5_K_M": 0.68,
    "Q4_K_M": 0.57,
    "Q3_K_M": 0.43,
}

# Approximate KV-cache cost:
#
#     0.02 GB / 1B parameters / 1K context
#
# This is intentionally an estimate.
# Different architectures can have significantly different
# KV-cache requirements.
KV_GB_PER_B_PER_1K = 0.02

# Runtime / activation / fragmentation allowance.
OVERHEAD = 1.10


# ============================================================
# THREE CANDIDATE MODELS
# ============================================================

MODELS = [
    {
        "name": "Qwen 2.5 1.5B",
        "short_name": "Qwen-1.5B",
        "parameters_b": 1.5,
        "context_k": 8,
        "quantization": "Q4_K_M",
        "license": "Apache-2.0",
        "commercial_use": "Yes",
        "restriction": "Standard Apache-2.0 conditions",
        "model_card": "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct",
        "ollama": "qwen2.5:1.5b",
    },
    {
        "name": "Qwen 2.5 7B",
        "short_name": "Qwen-7B",
        "parameters_b": 7.0,
        "context_k": 8,
        "quantization": "Q4_K_M",
        "license": "Apache-2.0",
        "commercial_use": "Yes",
        "restriction": "Standard Apache-2.0 conditions",
        "model_card": "https://huggingface.co/Qwen/Qwen2.5-7B-Instruct",
        "ollama": "qwen2.5:7b",
    },
    {
        "name": "Llama 3.1 8B",
        "short_name": "Llama-8B",
        "parameters_b": 8.0,
        "context_k": 8,
        "quantization": "Q4_K_M",
        "license": "Llama 3.1 Community License",
        "commercial_use": "Subject to licence terms",
        "restriction": "Additional Llama-specific terms apply",
        "model_card": "https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct",
        "ollama": "llama3.1:8b",
    },
]


# ============================================================
# HARDWARE DETECTION
# ============================================================

def get_system_memory_gb():
    """
    Detect total physical RAM on:
    - Windows
    - macOS
    - Linux
    """

    system_os = platform.system()

    # --------------------------------------------------------
    # Windows: GlobalMemoryStatusEx
    # --------------------------------------------------------

    if system_os == "Windows":

        try:
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]

            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)

            if ctypes.windll.kernel32.GlobalMemoryStatusEx(
                ctypes.byref(stat)
            ):
                return round(
                    stat.ullTotalPhys / (1024 ** 3),
                    1
                )

        except Exception:
            pass

        # Older Windows fallback
        try:
            out = subprocess.check_output(
                [
                    "wmic",
                    "computersystem",
                    "get",
                    "TotalPhysicalMemory"
                ],
                stderr=subprocess.DEVNULL
            ).decode()

            lines = [
                line.strip()
                for line in out.splitlines()
                if line.strip().isdigit()
            ]

            if lines:
                return round(
                    int(lines[0]) / (1024 ** 3),
                    1
                )

        except Exception:
            pass

    # --------------------------------------------------------
    # Linux / macOS
    # --------------------------------------------------------

    try:
        pages = os.sysconf("SC_PHYS_PAGES")
        page_size = os.sysconf("SC_PAGE_SIZE")

        return round(
            (pages * page_size) / (1024 ** 3),
            1
        )

    except (AttributeError, ValueError, OSError):
        pass

    # --------------------------------------------------------
    # macOS fallback
    # --------------------------------------------------------

    if system_os == "Darwin":

        try:
            out = subprocess.check_output(
                ["sysctl", "-n", "hw.memsize"]
            ).decode().strip()

            return round(
                int(out) / (1024 ** 3),
                1
            )

        except Exception:
            pass

    # --------------------------------------------------------
    # psutil fallback
    # --------------------------------------------------------

    try:
        import psutil

        return round(
            psutil.virtual_memory().total / (1024 ** 3),
            1
        )

    except ImportError:
        pass

    return 8.0


def get_gpu_vram_gb():
    """
    Detect NVIDIA GPU VRAM where nvidia-smi is available.
    """

    try:

        out = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=memory.total",
                "--format=csv,noheader,nounits"
            ],
            stderr=subprocess.DEVNULL
        ).decode().strip()

        if out:

            first_gpu_mb = float(
                out.splitlines()[0]
            )

            return (
                round(first_gpu_mb / 1024, 1),
                "NVIDIA GPU"
            )

    except Exception:
        pass

    # Windows fallback
    if platform.system() == "Windows":

        try:

            out = subprocess.check_output(
                [
                    "wmic",
                    "path",
                    "Win32_VideoController",
                    "get",
                    "AdapterRAM,Name"
                ],
                stderr=subprocess.DEVNULL
            ).decode()

            for line in out.splitlines()[1:]:

                parts = line.strip().split()

                if parts and parts[0].isdigit():

                    bytes_val = int(parts[0])

                    if bytes_val > 512 * 1024 * 1024:

                        return (
                            round(
                                bytes_val / (1024 ** 3),
                                1
                            ),
                            "Dedicated GPU"
                        )

        except Exception:
            pass

    return None, None


def get_chip_info():

    system_os = platform.system()

    if system_os == "Darwin":

        try:
            return subprocess.check_output(
                [
                    "sysctl",
                    "-n",
                    "machdep.cpu.brand_string"
                ]
            ).decode().strip()

        except Exception:
            pass

    elif system_os == "Windows":

        return os.environ.get(
            "PROCESSOR_IDENTIFIER",
            platform.processor() or "Windows PC"
        )

    return (
        platform.processor()
        or platform.machine()
    )


# ============================================================
# MEMORY ESTIMATION
# ============================================================

def estimate_memory(
    params_b,
    precision="Q4_K_M",
    context_k=8
):
    """
    Estimate:

        Total =
        (weights + KV cache) * runtime overhead
    """

    if precision not in BYTES_PER_PARAM:

        raise ValueError(
            f"Unknown precision: {precision}"
        )

    # --------------------------------------------------------
    # Weight memory
    # --------------------------------------------------------

    weights_gb = (
        params_b *
        BYTES_PER_PARAM[precision]
    )

    # --------------------------------------------------------
    # KV cache
    # --------------------------------------------------------

    kv_gb = (
        params_b *
        context_k *
        KV_GB_PER_B_PER_1K
    )

    # --------------------------------------------------------
    # Runtime overhead
    # --------------------------------------------------------

    total_gb = (
        weights_gb +
        kv_gb
    ) * OVERHEAD

    return (
        weights_gb,
        kv_gb,
        total_gb
    )


# ============================================================
# FIT VERDICT
# ============================================================

def verdict(
    total_gb,
    available_gb
):

    if total_gb <= available_gb * 0.70:
        return "FITS"

    if total_gb <= available_gb:
        return "FITS, BUT TIGHT"

    return "DOES NOT FIT"


# ============================================================
# PRINT MODEL ESTIMATE
# ============================================================

def print_model_estimate(
    model,
    available_gb
):

    weights, kv, total = estimate_memory(
        model["parameters_b"],
        model["quantization"],
        model["context_k"]
    )

    status = verdict(
        total,
        available_gb
    )

    print(
        f"{model['short_name']:<18}"
        f"{model['quantization']:<10}"
        f"{model['parameters_b']:>6.1f}B  "
        f"{model['context_k']:>5}K  "
        f"{weights:>8.2f} GB  "
        f"{kv:>8.2f} GB  "
        f"{total:>8.2f} GB  "
        f"{status}"
    )

    return total, status


# ============================================================
# CONTEXT LENGTH EXPERIMENT
# ============================================================

def context_experiment(
    params_b,
    precision,
    available_gb
):

    print()
    print("=" * 82)
    print("CONTEXT LENGTH EXPERIMENT")
    print("=" * 82)

    print(
        f"\n{params_b}B model / {precision}\n"
    )

    print(
        f"{'Context':<12}"
        f"{'Weights':<15}"
        f"{'KV Cache':<15}"
        f"{'Total':<15}"
        f"Result"
    )

    print("-" * 82)

    for context_k in [4, 8, 16, 32, 64, 128]:

        weights, kv, total = estimate_memory(
            params_b,
            precision,
            context_k
        )

        status = verdict(
            total,
            available_gb
        )

        print(
            f"{str(context_k) + 'K':<12}"
            f"{weights:<15.2f}"
            f"{kv:<15.2f}"
            f"{total:<15.2f}"
            f"{status}"
        )

    print(
        "\nObservation:"
    )

    print(
        "Weights remain approximately constant while "
        "KV-cache memory increases with context length."
    )


# ============================================================
# QUANTIZATION EXPERIMENT
# ============================================================

def quantization_experiment(
    params_b,
    context_k,
    available_gb
):

    print()
    print("=" * 82)
    print("QUANTIZATION EXPERIMENT")
    print("=" * 82)

    print(
        f"\n{params_b}B model / {context_k}K context\n"
    )

    print(
        f"{'Precision':<15}"
        f"{'Bytes/Param':<15}"
        f"{'Weights':<15}"
        f"{'Total':<15}"
        f"Result"
    )

    print("-" * 82)

    for precision, bytes_per_param in BYTES_PER_PARAM.items():

        weights, kv, total = estimate_memory(
            params_b,
            precision,
            context_k
        )

        status = verdict(
            total,
            available_gb
        )

        print(
            f"{precision:<15}"
            f"{bytes_per_param:<15.2f}"
            f"{weights:<15.2f}"
            f"{total:<15.2f}"
            f"{status}"
        )

    print(
        "\nObservation:"
    )

    print(
        "Lower-bit quantization reduces weight memory, "
        "which can allow larger models to fit on the same machine."
    )


# ============================================================
# LICENCE COMPARISON
# ============================================================

def licence_comparison():

    print()
    print("=" * 100)
    print("LICENCE COMPARISON")
    print("=" * 100)

    print()

    print(
        f"{'Model':<20}"
        f"{'Licence':<32}"
        f"{'Commercial Use':<28}"
    )

    print("-" * 100)

    for model in MODELS:

        print(
            f"{model['short_name']:<20}"
            f"{model['license']:<32}"
            f"{model['commercial_use']:<28}"
        )

    print()

    for model in MODELS:

        print(f"MODEL: {model['name']}")
        print(f"Licence       : {model['license']}")
        print(f"Commercial    : {model['commercial_use']}")
        print(f"Restrictions  : {model['restriction']}")
        print(f"Model card    : {model['model_card']}")
        print()


# ============================================================
# OLLAMA CHECK
# ============================================================

def check_ollama():

    try:

        subprocess.check_output(
            ["ollama", "--version"],
            stderr=subprocess.DEVNULL
        )

        return True

    except Exception:
        return False


# ============================================================
# GET OLLAMA MEMORY
# ============================================================

def get_ollama_memory():

    """
    Query Ollama's running model endpoint.

    Returns memory information if available.
    """

    try:

        url = "http://localhost:11434/api/ps"

        with urllib.request.urlopen(
            url,
            timeout=3
        ) as response:

            data = json.loads(
                response.read().decode()
            )

        if not data.get("models"):
            return None

        model = data["models"][0]

        size = model.get(
            "size",
            0
        )

        return size / (1024 ** 3)

    except Exception:

        return None


# ============================================================
# ACTUAL MODEL BENCHMARK
# ============================================================

def run_actual_model(model):

    if not check_ollama():

        print(
            "\nOllama is not installed or not available."
        )

        print(
            "Skipping actual inference benchmark."
        )

        return None

    ollama_model = model["ollama"]

    print()
    print("=" * 82)
    print("ACTUAL INFERENCE TEST")
    print("=" * 82)

    print(
        f"\nModel: {model['name']}"
    )

    print(
        f"Ollama model: {ollama_model}"
    )

    print(
        "\nStarting model..."
    )

    try:

        start_time = time.time()

        subprocess.run(
            [
                "ollama",
                "run",
                ollama_model,
                "Explain what a computer network is in one sentence."
            ],
            check=True
        )

        elapsed = time.time() - start_time

        print(
            f"\nInference completed in {elapsed:.2f} seconds."
        )

    except subprocess.CalledProcessError:

        print(
            "\nCould not run the model."
        )

        return None

    # --------------------------------------------------------
    # Check memory after model is loaded
    # --------------------------------------------------------

    memory_gb = get_ollama_memory()

    if memory_gb is not None:

        print(
            f"Ollama reported loaded model size: "
            f"{memory_gb:.2f} GB"
        )

    else:

        print(
            "Could not obtain Ollama memory information."
        )

    return memory_gb


# ============================================================
# ESTIMATE VS ACTUAL
# ============================================================

def compare_estimate_actual(
    estimated_gb,
    actual_gb
):

    print()
    print("=" * 82)
    print("ESTIMATE VS ACTUAL MEMORY")
    print("=" * 82)

    print()

    print(
        f"{'Metric':<25}"
        f"{'Memory':<20}"
    )

    print("-" * 50)

    print(
        f"{'Estimated':<25}"
        f"{estimated_gb:.2f} GB"
    )

    if actual_gb is not None:

        print(
            f"{'Actual':<25}"
            f"{actual_gb:.2f} GB"
        )

        difference = (
            actual_gb -
            estimated_gb
        )

        print(
            f"{'Difference':<25}"
            f"{difference:+.2f} GB"
        )

        percentage = (
            abs(difference) /
            estimated_gb
        ) * 100

        print(
            f"{'Difference %':<25}"
            f"{percentage:.1f}%"
        )

    print()

    print(
        "The estimate is an approximation."
    )

    print(
        "Actual memory can differ because of runtime allocations, "
        "activations, buffers, drivers and implementation details."
    )


# ============================================================
# FINAL DECISION
# ============================================================

def final_decision(
    model,
    estimated_gb,
    status,
    actual_gb=None
):

    print()
    print("=" * 82)
    print("MODEL SELECTION FOR THE STATED SCENARIO")
    print("=" * 82)

    print()

    print(
        f"Selected model : {model['name']}"
    )

    print(
        f"Parameters     : {model['parameters_b']}B"
    )

    print(
        f"Quantization   : {model['quantization']}"
    )

    print(
        f"Context        : {model['context_k']}K"
    )

    print(
        f"Licence        : {model['license']}"
    )

    print(
        f"Estimated      : {estimated_gb:.2f} GB"
    )

    print(
        f"Hardware fit   : {status}"
    )

    if actual_gb is not None:

        print(
            f"Actual         : {actual_gb:.2f} GB"
        )

    print()

    print("Reasons:")

    print(
        "1. The estimated memory requirement is within the "
        "available hardware budget."
    )

    print(
        "2. Quantization reduces the memory required by the weights."
    )

    print(
        "3. The selected context length keeps KV-cache growth "
        "within the available memory."
    )

    print(
        "4. Actual inference can be used to validate the estimate."
    )

    print(
        "5. The licence must be checked against the intended use "
        "before deployment."
    )


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    # --------------------------------------------------------
    # Detect machine
    # --------------------------------------------------------

    system_os = platform.system()

    total_ram_gb = get_system_memory_gb()

    chip_name = get_chip_info()

    gpu_vram_gb, gpu_name = get_gpu_vram_gb()

    os_name = (
        f"{system_os} "
        f"{platform.release()} "
        f"({platform.machine()})"
    )

    # --------------------------------------------------------
    # Determine usable memory budget
    # --------------------------------------------------------

    if gpu_vram_gb:

        memory_type = (
            f"Dedicated GPU: "
            f"{gpu_name} "
            f"({gpu_vram_gb} GB VRAM)"
        )

        usable_gb = round(
            gpu_vram_gb * 0.90,
            1
        )

        budget_explanation = (
            f"{usable_gb} GB "
            "(90% of dedicated VRAM)"
        )

    elif system_os == "Darwin":

        memory_type = (
            "Apple Silicon Unified Memory"
        )

        usable_gb = round(
            total_ram_gb * 0.75,
            1
        )

        budget_explanation = (
            f"{usable_gb} GB "
            "(75% of unified memory)"
        )

    else:

        memory_type = (
            "System RAM / CPU inference"
        )

        usable_gb = round(
            total_ram_gb * 0.70,
            1
        )

        budget_explanation = (
            f"{usable_gb} GB "
            "(70% of system RAM)"
        )

    # --------------------------------------------------------
    # Hardware report
    # --------------------------------------------------------

    print("=" * 82)
    print("TEXT GENERATION MODEL ANALYZER")
    print("=" * 82)

    print()

    print("SYSTEM HARDWARE")
    print("-" * 82)

    print(
        f"OS              : {os_name}"
    )

    print(
        f"Processor       : {chip_name}"
    )

    print(
        f"System RAM      : {total_ram_gb} GB"
    )

    if gpu_vram_gb:

        print(
            f"GPU VRAM        : {gpu_vram_gb} GB"
        )

    else:

        print(
            "GPU VRAM        : Not detected"
        )

    print(
        f"Memory Type     : {memory_type}"
    )

    print(
        f"Usable Budget   : {budget_explanation}"
    )

    # --------------------------------------------------------
    # Model compatibility
    # --------------------------------------------------------

    print()
    print("=" * 82)
    print("PRE-DOWNLOAD MODEL COMPATIBILITY ANALYSIS")
    print("=" * 82)

    print()

    print(
        f"{'Model':<18}"
        f"{'Quant':<10}"
        f"{'Params':>8}"
        f"{'Context':>9}"
        f"{'Weights':>12}"
        f"{'KV Cache':>12}"
        f"{'Total':>12}"
        f"  Result"
    )

    print("-" * 100)

    fit_models = []

    for model in MODELS:

        total, status = print_model_estimate(
            model,
            usable_gb
        )

        if status in (
            "FITS",
            "FITS, BUT TIGHT"
        ):

            fit_models.append(
                (model, total, status)
            )

    # --------------------------------------------------------
    # Context experiment
    # --------------------------------------------------------

    context_experiment(
        params_b=8.0,
        precision="Q4_K_M",
        available_gb=usable_gb
    )

    # --------------------------------------------------------
    # Quantization experiment
    # --------------------------------------------------------

    quantization_experiment(
        params_b=8.0,
        context_k=8,
        available_gb=usable_gb
    )

    # --------------------------------------------------------
    # Licence comparison
    # --------------------------------------------------------

    licence_comparison()

    # --------------------------------------------------------
    # Select a model for actual test
    # --------------------------------------------------------

    if not fit_models:

        print()
        print(
            "No candidate model fits the estimated memory budget."
        )

        print(
            "Consider a smaller model or stronger quantization."
        )

        return

    # Choose the smallest fitting candidate for the practical
    # benchmark rather than claiming it is universally "best".

    fit_models.sort(
        key=lambda x: x[1]
    )

    selected_model = fit_models[0][0]

    estimated_memory, status = (
        fit_models[0][1],
        fit_models[0][2]
    )

    # --------------------------------------------------------
    # Actual benchmark
    # --------------------------------------------------------

    print()
    print(
        f"Selected for practical benchmark: "
        f"{selected_model['name']}"
    )

    actual_memory = run_actual_model(
        selected_model
    )

    # --------------------------------------------------------
    # Compare estimate vs actual
    # --------------------------------------------------------

    compare_estimate_actual(
        estimated_memory,
        actual_memory
    )

    # --------------------------------------------------------
    # Final recommendation
    # --------------------------------------------------------

    final_decision(
        selected_model,
        estimated_memory,
        status,
        actual_memory
    )


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
