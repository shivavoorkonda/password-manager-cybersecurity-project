import time
import os
import hashlib
import matplotlib.pyplot as plt
import numpy as np
from argon2 import PasswordHasher

def benchmark_pbkdf2(iterations_list, password=b"test_password", salt=b"test_salt", runs=10):
    results = {}
    for iters in iterations_list:
        times = []
        for _ in range(runs):
            start = time.perf_counter()
            hashlib.pbkdf2_hmac('sha256', password, salt, iters)
            times.append(time.perf_counter() - start)
        results[f"PBKDF2-{iters}"] = {'mean': np.mean(times), 'std': np.std(times)}
    return results

def benchmark_argon2(configs, password="test_password", runs=10):
    results = {}
    for mem, time_cost, parallelism in configs:
        times = []
        ph = PasswordHasher(time_cost=time_cost, memory_cost=mem, parallelism=parallelism)
        for _ in range(runs):
            start = time.perf_counter()
            ph.hash(password)
            times.append(time.perf_counter() - start)
        label = f"Argon2-m{mem}-t{time_cost}-p{parallelism}"
        results[label] = {'mean': np.mean(times), 'std': np.std(times)}
    return results

def plot_benchmarks(results, output_path):
    labels = list(results.keys())
    means = [results[k]['mean'] * 1000 for k in labels] # to ms
    stds = [results[k]['std'] * 1000 for k in labels]
    
    plt.figure(figsize=(12, 6))
    plt.bar(labels, means, yerr=stds, capsize=5, color='skyblue', edgecolor='black')
    plt.ylabel('Time (ms)')
    plt.title('KDF Derivation Time Benchmark')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def plot_table(results, output_path):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.axis('off')
    
    col_labels = ['KDF Configuration', 'Mean Time (ms)', 'Std Dev (ms)']
    cell_text = []
    for k, v in results.items():
        cell_text.append([k, f"{v['mean']*1000:.2f}", f"{v['std']*1000:.2f}"])
        
    table = ax.table(cellText=cell_text, colLabels=col_labels, loc='center', cellLoc='center')
    table.scale(1, 1.5)
    plt.title('KDF Benchmark Results')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def main():
    pbkdf2_iters = [100000, 300000, 600000, 1000000]
    argon2_configs = [
        (19456, 2, 1),
        (47104, 1, 1),
        (65536, 3, 4)
    ]
    
    print("Benchmarking PBKDF2-HMAC-SHA256...")
    pbkdf2_res = benchmark_pbkdf2(pbkdf2_iters)
    
    print("Benchmarking Argon2id...")
    argon2_res = benchmark_argon2(argon2_configs)
    
    all_results = {**pbkdf2_res, **argon2_res}
    
    os.makedirs('../../report/figures', exist_ok=True)
    
    print("\nGenerating charts...")
    plot_benchmarks(all_results, '../../report/figures/kdf_benchmark_bar.png')
    plot_table(all_results, '../../report/figures/kdf_benchmark_table.png')
    
    print("\nBenchmark Results Table:")
    print("-" * 65)
    print(f"| {'Configuration':<30} | {'Mean (ms)':<12} | {'Std (ms)':<12} |")
    print("-" * 65)
    for k, v in all_results.items():
        print(f"| {k:<30} | {v['mean']*1000:<12.2f} | {v['std']*1000:<12.2f} |")
    print("-" * 65)
    
    print("\nDiscussion on GPU Resistance:")
    print("PBKDF2 is heavily CPU-bound and lacks memory-hardness. Attackers with GPUs/ASICs")
    print("can parallelize the simple operations efficiently, greatly accelerating cracking speed.")
    print("Argon2id, on the other hand, introduces memory-hardness (memory_cost). By forcing the")
    print("computation to read/write large blocks of memory pseudo-randomly, it creates a memory")
    print("bandwidth bottleneck. Since GPUs have less memory per core compared to CPUs, their")
    print("parallelization advantage is significantly reduced, offering robust GPU resistance.")

if __name__ == '__main__':
    main()
