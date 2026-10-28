"""
experiments/run_real_benchmarks.py
Executes the empirical benchmark across the 4 curated Kaggle benchmark suites:
1. Suite 1: darkmatternet/open-source-supply-chain-risk-graph (274 trials)
2. Suite 2: namethename/fastflux-dataset (100 trials)
3. Suite 3: japkeeratsingh/oss-vulnerabilities (300 trials)
4. Suite 4: cyberprince/lotl-apt-red-team-dataset (701 trials)
Total: 1,375 trials.
Outputs raw execution records to results/raw/real_benchmark_eval.jsonl.
"""

import os
import sys
import json
import time

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)
benchmark_prototype_dir = os.path.join(base_dir, "benchmark_prototype")
if benchmark_prototype_dir not in sys.path:
    sys.path.insert(0, benchmark_prototype_dir)

from benchmark_prototype.evaluate_real_datasets import RealKaggleEvaluator

def main():
    print("[*] Initializing Real Kaggle Benchmark Evaluation (1,375 trials)...")
    t0 = time.time()
    evaluator = RealKaggleEvaluator(benchmark_prototype_dir)
    summary = evaluator.run_all()
    total_time = time.time() - t0
    print(f"\n[+] Successfully executed 1,375 Kaggle trials across 4 suites in {total_time:.2f}s")

if __name__ == "__main__":
    main()
