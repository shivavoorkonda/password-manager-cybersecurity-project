"""Compare local PBKDF2 and Argon2id derivation latency.

This is a CPU timing exercise for fixed parameters, not a password-cracking or
GPU-resistance benchmark. Results are machine-dependent and are written with
platform metadata for reproducibility.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import statistics
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from argon2.low_level import Type, hash_secret_raw


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "report" / "figures"
PASSWORD = b"benchmark-only-not-a-real-password"
SALT = b"project-benchmark-salt-v1"
RUNS = 10


def measure(label: str, operation, runs: int = RUNS) -> dict[str, float | int | str]:
    operation()  # warm-up; excluded from the measurements
    samples = []
    for _ in range(runs):
        start = time.perf_counter()
        operation()
        samples.append(time.perf_counter() - start)
    return {
        "configuration": label,
        "runs": runs,
        "mean_ms": statistics.mean(samples) * 1000,
        "median_ms": statistics.median(samples) * 1000,
        "stdev_ms": statistics.stdev(samples) * 1000 if len(samples) > 1 else 0.0,
    }


def main() -> None:
    cases = []
    for iterations in (100_000, 300_000, 600_000, 1_000_000):
        cases.append(measure(
            f"PBKDF2-HMAC-SHA256, {iterations:,} iterations",
            lambda it=iterations: hashlib.pbkdf2_hmac("sha256", PASSWORD, SALT, it, dklen=32),
        ))

    # Memory is in KiB as required by argon2-cffi. These are separate parameter
    # choices, not equivalent-work settings against PBKDF2.
    for memory_kib, time_cost, parallelism in (
        (19_456, 2, 1),
        (47_104, 1, 1),
        (65_536, 3, 1),
    ):
        cases.append(measure(
            f"Argon2id, m={memory_kib} KiB, t={time_cost}, p={parallelism}",
            lambda m=memory_kib, t=time_cost, p=parallelism: hash_secret_raw(
                PASSWORD, SALT, time_cost=t, memory_cost=m, parallelism=p,
                hash_len=32, type=Type.ID, version=19,
            ),
        ))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "purpose": "Local CPU derivation-latency comparison; not a cracking/GPU benchmark",
        "runs_per_configuration": RUNS,
        "warmup_runs": 1,
        "output_length_bytes": 32,
        "platform": platform.platform(),
        "processor": platform.processor() or "unspecified",
        "python": sys.version,
        "cpu_count": os.cpu_count(),
        "results": cases,
    }
    json_path = OUTPUT_DIR / "kdf_benchmark_results.json"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    labels = [case["configuration"].replace(", ", "\n") for case in cases]
    medians = [case["median_ms"] for case in cases]
    deviations = [case["stdev_ms"] for case in cases]
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.bar(range(len(cases)), medians, yerr=deviations, capsize=4, color="#3973ac")
    ax.set_xticks(range(len(cases)), labels, rotation=20, ha="right")
    ax.set_ylabel("Median derivation time (ms)")
    ax.set_title("Local PBKDF2 and Argon2id CPU timing (error bars: standard deviation)")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "kdf_benchmark_bar.png", dpi=160)
    plt.close(fig)

    print(f"Results: {json_path}")
    print(f"Platform: {report['platform']}; processor: {report['processor']}")
    print("This measures local derivation latency only; it does not measure GPU cracking resistance.")
    for case in cases:
        print(f"{case['configuration']}: median {case['median_ms']:.2f} ms, "
              f"mean {case['mean_ms']:.2f} ms, SD {case['stdev_ms']:.2f} ms")


if __name__ == "__main__":
    main()
