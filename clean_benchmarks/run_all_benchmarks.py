#!/usr/bin/env python
"""
Master script to run all clean benchmarks without pyperformance overhead.
"""

import time
import sys
import os

# Add the clean_benchmarks directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_benchmark(benchmark_name, module_name):
    """Run a single benchmark and measure execution time"""
    print(f"\n{'='*60}")
    print(f"Running {benchmark_name} benchmark...")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        # Import and run the benchmark
        module = __import__(module_name)
        module.main()
        
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"\n✓ {benchmark_name} completed in {execution_time:.3f} seconds")
        return True, execution_time
        
    except ImportError as e:
        print(f"✗ Failed to import {module_name}: {e}")
        return False, 0
    except Exception as e:
        print(f"✗ Error running {benchmark_name}: {e}")
        return False, 0


def main():
    """Run all benchmarks"""
    benchmarks = [
        ("Crypto PyAES", "crypto_pyaes_clean"),
        ("Deepcopy", "deepcopy_clean"),
        ("Logging", "logging_clean"),
        ("MDP (Markov Decision Process)", "mdp_clean"),
        ("Pathlib", "pathlib_clean"),
        ("Pickle", "pickle_clean"),
        ("Pyflate (Compression)", "pyflate_clean"),
        ("Unpack Sequence", "unpack_sequence_clean"),
        ("JSON Dumps", "json_dumps_clean"),
        ("GC Collect", "gc_collect_clean")
    ]
    
    print("Clean Benchmark Suite")
    print("Running benchmarks without pyperformance overhead...")
    
    total_start_time = time.time()
    successful_benchmarks = 0
    total_benchmark_time = 0
    
    for benchmark_name, module_name in benchmarks:
        success, exec_time = run_benchmark(benchmark_name, module_name)
        if success:
            successful_benchmarks += 1
            total_benchmark_time += exec_time
    
    total_end_time = time.time()
    total_runtime = total_end_time - total_start_time
    
    print(f"\n{'='*60}")
    print("BENCHMARK SUMMARY")
    print(f"{'='*60}")
    print(f"Successful benchmarks: {successful_benchmarks}/{len(benchmarks)}")
    print(f"Total benchmark execution time: {total_benchmark_time:.3f} seconds")
    print(f"Total runtime (including overhead): {total_runtime:.3f} seconds")
    print(f"Overhead: {total_runtime - total_benchmark_time:.3f} seconds")


if __name__ == "__main__":
    main()
