#!/usr/bin/env python
"""
Simple script to generate flame graphs using py-spy for all clean benchmarks.
Creates organized directory structure with timestamps.
"""

import os
import subprocess
import sys
import time
from datetime import datetime

def run_pyspy_flamegraph(benchmark_name, script_name):
    """Run py-spy to generate flame graph for a benchmark."""
    
    # Create timestamp for this run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create directory structure: flamegraphs/benchmark_name/timestamp/
    output_dir = os.path.join("flamegraphs", benchmark_name, timestamp)
    os.makedirs(output_dir, exist_ok=True)
    
    # Flame graph output file
    flamegraph_file = os.path.join(output_dir, f"flamegraph_pyspy_{benchmark_name}.svg")
    
    # py-spy command using venv_dbg
    venv_python = '/csl/yoav.gold/hw_sw_project/.venv_dbg/bin/python'
    cmd = [
        '/csl/yoav.gold/hw_sw_project/.venv_dbg/bin/py-spy', 'record',
        '-o', flamegraph_file,
        '-d', '20',  # Duration: 20 seconds
        '-r', '100', # Sample rate: 100 Hz
        '--',
        venv_python, script_name
    ]
    
    print(f"\n{'='*50}")
    print(f"Benchmark: {benchmark_name}")
    print(f"Script: {script_name}")
    print(f"Output: {flamegraph_file}")
    print(f"{'='*50}")
    
    try:
        # Check if script exists
        if not os.path.exists(script_name):
            print(f"❌ Script {script_name} not found!")
            return False
        
        print(f"🔥 Running py-spy: {' '.join(cmd)}")
        
        # Run py-spy
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        end_time = time.time()
        
        if result.returncode == 0:
            if os.path.exists(flamegraph_file):
                file_size = os.path.getsize(flamegraph_file)
                print(f"✅ Success! Flame graph generated ({file_size:,} bytes)")
                print(f"⏱️  Duration: {end_time - start_time:.2f}s")
                return True
            else:
                print(f"❌ py-spy completed but no output file created")
                return False
        else:
            print(f"❌ py-spy failed (exit code: {result.returncode})")
            if result.stderr:
                print(f"Error output: {result.stderr}")
            if result.stdout:
                print(f"Standard output: {result.stdout}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ Timeout after 60 seconds")
        return False
    except FileNotFoundError:
        print(f"❌ py-spy not found in venv_dbg! Check if py-spy is installed in the virtual environment")
        print("   Try: /csl/yoav.gold/hw_sw_project/.venv_dbg/bin/pip install py-spy")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Generate flame graphs for all benchmarks."""
    
    # Benchmark list
    benchmarks = [
        ("crypto_pyaes", "crypto_pyaes_clean.py"),
        ("deepcopy", "deepcopy_clean.py"), 
        ("logging", "logging_clean.py"),
        ("mdp", "mdp_clean.py"),
        ("pathlib", "pathlib_clean.py"),
        ("pickle", "pickle_clean.py"),
        ("pyflate", "pyflate_clean.py"),
        ("unpack_sequence", "unpack_sequence_clean.py"),
        ("json_dumps", "json_dumps_clean.py"),
        ("gc_collect", "gc_collect_clean.py")
    ]
    
    print("🔥 Py-Spy Flame Graph Generator for Clean Benchmarks")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    successful = 0
    total = len(benchmarks)
    
    for benchmark_name, script_name in benchmarks:
        success = run_pyspy_flamegraph(benchmark_name, script_name)
        if success:
            successful += 1
        
        # Brief pause between benchmarks
        time.sleep(2)
    
    # Final summary
    print(f"\n🎯 SUMMARY")
    print(f"{'='*50}")
    print(f"✅ Successful: {successful}/{total}")
    print(f"📁 Output directory: {os.path.abspath('flamegraphs')}")
    print(f"📅 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # List all generated flame graphs
    if os.path.exists("flamegraphs"):
        print(f"\n📊 Generated flame graphs:")
        for root, dirs, files in os.walk("flamegraphs"):
            for file in files:
                if file.endswith('.svg'):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path)
                    file_size = os.path.getsize(full_path)
                    print(f"  📈 {rel_path} ({file_size:,} bytes)")

if __name__ == "__main__":
    # Verify we're in the correct directory
    if not os.path.exists("run_all_benchmarks.py"):
        print("❌ Error: Please run this script from the clean_benchmarks directory")
        print("   Current directory:", os.getcwd())
        sys.exit(1)
    
    main()
