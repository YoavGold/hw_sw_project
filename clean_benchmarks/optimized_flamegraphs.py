#!/usr/bin/env python
"""
Optimized py-spy flame graph generator for clean benchmarks using venv_dbg.
Creates the directory structure: flamegraphs/benchmark_name/timestamp/
"""

import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

def create_benchmark_dir(benchmark_name):
    """Create directory structure for benchmark."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    benchmark_dir = Path("flamegraphs") / benchmark_name / timestamp
    benchmark_dir.mkdir(parents=True, exist_ok=True)
    return benchmark_dir, timestamp

def run_pyspy_flamegraph(benchmark_name, script_name, duration=15):
    """Run py-spy to generate flame graph for a benchmark."""
    
    # Check if script exists
    if not Path(script_name).exists():
        print(f"❌ Script {script_name} not found!")
        return False
    
    # Create directory structure
    output_dir, timestamp = create_benchmark_dir(benchmark_name)
    flamegraph_file = output_dir / f"flamegraph_pyspy_{benchmark_name}.svg"
    
    # py-spy command using venv_dbg
    venv_pyspy = '/csl/yoav.gold/hw_sw_project/.venv_dbg/bin/py-spy'
    venv_python = '/csl/yoav.gold/hw_sw_project/.venv_dbg/bin/python'
    
    cmd = [
        venv_pyspy, 'record',
        '-o', str(flamegraph_file),
        '-d', str(duration),
        '-r', '100',  # 100 Hz sampling
        '--',
        venv_python, script_name
    ]
    
    print(f"\n{'='*60}")
    print(f"🔥 Benchmark: {benchmark_name}")
    print(f"📁 Output: {flamegraph_file}")
    print(f"⏱️  Duration: {duration}s")
    print(f"{'='*60}")
    
    try:
        print(f"🚀 Running py-spy...")
        start_time = time.time()
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration + 10)
        
        end_time = time.time()
        actual_duration = end_time - start_time
        
        if result.returncode == 0:
            if flamegraph_file.exists():
                file_size = flamegraph_file.stat().st_size
                print(f"✅ SUCCESS!")
                print(f"   📈 File: {file_size:,} bytes")
                print(f"   ⏱️  Time: {actual_duration:.2f}s")
                
                # Print py-spy output for samples info
                if result.stderr:
                    lines = result.stderr.strip().split('\n')
                    for line in lines:
                        if 'Samples:' in line or 'Wrote flamegraph' in line:
                            print(f"   📊 {line}")
                
                return True, str(flamegraph_file)
            else:
                print(f"❌ FAILED: No output file created")
                return False, None
        else:
            print(f"❌ FAILED: py-spy exit code {result.returncode}")
            if result.stderr:
                print(f"   Error: {result.stderr[:300]}")
            return False, None
            
    except subprocess.TimeoutExpired:
        print(f"❌ TIMEOUT after {duration + 10}s")
        return False, None
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False, None

def main():
    """Generate flame graphs for selected benchmarks."""
    
    # Benchmarks with appropriate durations (some need more time for good sampling)
    benchmarks = [
        ("json_dumps", "json_dumps_clean.py", 10),
        ("deepcopy", "deepcopy_clean.py", 15),
        ("logging", "logging_clean.py", 10),
        ("pickle", "pickle_clean.py", 15),
        ("unpack_sequence", "unpack_sequence_clean.py", 10),
        ("gc_collect", "gc_collect_clean.py", 15),
        ("pyflate", "pyflate_clean.py", 20),
        ("pathlib", "pathlib_clean.py", 20),
        ("mdp", "mdp_clean.py", 30),  # This one is slow, needs more time
        # Skip crypto_pyaes for now since pyaes isn't in venv_dbg
    ]
    
    print("🔥 Py-Spy Flame Graph Generator for Clean Benchmarks")
    print(f"📅 Session: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Using: /csl/yoav.gold/hw_sw_project/.venv_dbg/bin/python")
    print("=" * 60)
    
    successful = 0
    total = len(benchmarks)
    results = []
    
    for benchmark_name, script_name, duration in benchmarks:
        success, output_file = run_pyspy_flamegraph(benchmark_name, script_name, duration)
        results.append((benchmark_name, success, output_file))
        
        if success:
            successful += 1
        
        # Brief pause between benchmarks
        time.sleep(2)
    
    # Final summary
    print(f"\n🎯 FINAL SUMMARY")
    print("=" * 60)
    print(f"✅ Successful: {successful}/{total}")
    print(f"📁 Base directory: {Path('flamegraphs').absolute()}")
    
    print(f"\n📊 Results:")
    for benchmark_name, success, output_file in results:
        status = "✅" if success else "❌"
        print(f"  {status} {benchmark_name}")
        if output_file:
            file_size = Path(output_file).stat().st_size
            print(f"      📈 {output_file} ({file_size:,} bytes)")

if __name__ == "__main__":
    # Verify we're in the correct directory
    if not Path("run_all_benchmarks.py").exists():
        print("❌ Error: Please run this script from the clean_benchmarks directory")
        print(f"   Current directory: {os.getcwd()}")
        sys.exit(1)
    
    main()
