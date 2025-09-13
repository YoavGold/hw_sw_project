#!/usr/bin/env python
"""
Complete perf-based flame graph generator for all clean benchmarks.
Uses Linux perf tool with FlameGraph scripts to generate flame graphs.

This script follows the workflow:
1. perf record -F 99 --call-graph fp -- python benchmark.py
2. perf script > out.perf  
3. stackcollapse-perf.pl out.perf > out.folded
4. flamegraph.pl out.folded > flamegraph.svg

Directory structure: flamegraphs/benchmark_name/timestamp/
"""

import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

class PerfFlameGraphGenerator:
    def __init__(self):
        # Use local FlameGraph copy in hw_sw_project
        self.flamegraph_dir = '/csl/yoav.gold/hw_sw_project/FlameGraph'
        self.stackcollapse_script = os.path.join(self.flamegraph_dir, 'stackcollapse-perf.pl')
        self.flamegraph_script = os.path.join(self.flamegraph_dir, 'flamegraph.pl')
        self.venv_python = '/csl/yoav.gold/hw_sw_project/.venv_dbg/bin/python'
        
    def check_dependencies(self):
        """Check if required tools are available."""
        print("🔍 Checking dependencies...")
        
        # Check perf
        try:
            result = subprocess.run(['perf', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ perf available: {result.stdout.strip()}")
            else:
                print("❌ perf not working properly")
                return False
        except FileNotFoundError:
            print("❌ perf not found! Install with: sudo apt-get install linux-tools-generic")
            return False
        
        # Check FlameGraph scripts
        if not os.path.exists(self.flamegraph_dir):
            print(f"❌ FlameGraph directory not found: {self.flamegraph_dir}")
            return False
        
        if not os.path.exists(self.stackcollapse_script):
            print(f"❌ stackcollapse-perf.pl not found: {self.stackcollapse_script}")
            return False
            
        if not os.path.exists(self.flamegraph_script):
            print(f"❌ flamegraph.pl not found: {self.flamegraph_script}")
            return False
        
        print(f"✅ FlameGraph scripts found at: {self.flamegraph_dir}")
        return True
    
    def create_benchmark_dir(self, benchmark_name):
        """Create directory structure for benchmark."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        benchmark_dir = Path("flamegraphs_perf") / benchmark_name / timestamp
        benchmark_dir.mkdir(parents=True, exist_ok=True)
        return benchmark_dir, timestamp
    
    def generate_flamegraph(self, benchmark_name, script_name):
        """Generate complete flame graph for a benchmark."""
        print(f"\n{'='*60}")
        print(f"🎯 Benchmark: {benchmark_name}")
        print(f"📝 Script: {script_name}")
        print(f"{'='*60}")
        
        # Check if script exists
        if not Path(script_name).exists():
            print(f"❌ Script {script_name} not found!")
            return False, None
        
        # Create output directory
        output_dir, timestamp = self.create_benchmark_dir(benchmark_name)
        print(f"📁 Output: {output_dir}")
        
        # Define all file paths
        perf_data_file = output_dir / "perf.data"
        perf_script_file = output_dir / "out.perf"
        folded_file = output_dir / "out.folded"
        flamegraph_file = output_dir / f"flamegraph_perf_{benchmark_name}.svg"
        
        # Step 1: perf record
        print(f"🔴 Step 1: perf record")
        cmd = [
            'perf', 'record',
            '-F', '99',  # 99 Hz frequency (good balance of detail vs overhead)
            '--call-graph', 'fp',  # Frame pointers (faster than dwarf)
            '-o', str(perf_data_file),
            '--',
            self.venv_python, script_name
        ]
        
        try:
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            duration = time.time() - start_time
            
            if result.returncode == 0 and perf_data_file.exists():
                file_size = perf_data_file.stat().st_size
                print(f"   ✅ Success: {file_size:,} bytes in {duration:.2f}s")
            else:
                print(f"   ❌ Failed (code: {result.returncode})")
                if result.stderr:
                    print(f"   Error: {result.stderr[:300]}")
                return False, None
                
        except subprocess.TimeoutExpired:
            print("   ❌ Timeout (60s)")
            return False, None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False, None
        
        # Step 2: perf script
        print(f"📊 Step 2: perf script")
        try:
            start_time = time.time()
            with open(perf_script_file, 'w') as f:
                result = subprocess.run([
                    'perf', 'script',
                    '-i', str(perf_data_file)
                ], stdout=f, stderr=subprocess.PIPE, text=True, timeout=120)
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                script_size = perf_script_file.stat().st_size
                print(f"   ✅ Success: {script_size:,} bytes in {duration:.2f}s")
            else:
                print(f"   ❌ Failed: {result.stderr}")
                return False, None
                
        except subprocess.TimeoutExpired:
            print("   ❌ Timeout (120s)")
            return False, None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False, None
        
        # Step 3: stackcollapse
        print(f"📚 Step 3: stackcollapse")
        try:
            start_time = time.time()
            with open(perf_script_file, 'r') as input_f, open(folded_file, 'w') as output_f:
                result = subprocess.run([
                    'perl', self.stackcollapse_script
                ], stdin=input_f, stdout=output_f, stderr=subprocess.PIPE, text=True, timeout=60)
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                folded_size = folded_file.stat().st_size
                print(f"   ✅ Success: {folded_size:,} bytes in {duration:.2f}s")
            else:
                print(f"   ❌ Failed: {result.stderr}")
                return False, None
                
        except subprocess.TimeoutExpired:
            print("   ❌ Timeout (60s)")
            return False, None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False, None
        
        # Step 4: flamegraph
        print(f"🔥 Step 4: flamegraph")
        try:
            start_time = time.time()
            with open(folded_file, 'r') as input_f, open(flamegraph_file, 'w') as output_f:
                result = subprocess.run([
                    'perl', self.flamegraph_script,
                    '--title', f'Flame Graph: {benchmark_name}',
                    '--subtitle', f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
                ], stdin=input_f, stdout=output_f, stderr=subprocess.PIPE, text=True, timeout=30)
            
            duration = time.time() - start_time
            
            if result.returncode == 0 and flamegraph_file.exists():
                svg_size = flamegraph_file.stat().st_size
                print(f"   ✅ Success: {svg_size:,} bytes in {duration:.2f}s")
                print(f"🎉 COMPLETE: {flamegraph_file}")
                return True, str(flamegraph_file)
            else:
                print(f"   ❌ Failed: {result.stderr}")
                return False, None
                
        except subprocess.TimeoutExpired:
            print("   ❌ Timeout (30s)")
            return False, None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False, None
    
    def run_all_benchmarks(self):
        """Generate flame graphs for all benchmarks."""
        benchmarks = [
            ("deepcopy", "deepcopy_clean.py"),
            ("logging", "logging_clean.py"),
            ("pickle", "pickle_clean.py"),
            ("unpack_sequence", "unpack_sequence_clean.py"),
            ("json_dumps", "json_dumps_clean.py"),
            ("gc_collect", "gc_collect_clean.py"),
            ("pyflate", "pyflate_clean.py"),
            ("pathlib", "pathlib_clean.py"),
            ("mdp", "mdp_clean.py"),
            # Note: crypto_pyaes skipped since pyaes isn't in venv_dbg
        ]
        
        print("🔥 Perf-based Flame Graph Generator for Clean Benchmarks")
        print(f"📅 Session: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🐍 Python: {self.venv_python}")
        print(f"📊 FlameGraph: {self.flamegraph_dir}")
        print("=" * 60)
        
        if not self.check_dependencies():
            print("❌ Dependencies not satisfied!")
            return
        
        successful = 0
        total = len(benchmarks)
        results = []
        
        start_time = time.time()
        
        for i, (benchmark_name, script_name) in enumerate(benchmarks, 1):
            print(f"\n[{i}/{total}] Processing {benchmark_name}...")
            success, flamegraph_file = self.generate_flamegraph(benchmark_name, script_name)
            results.append((benchmark_name, success, flamegraph_file))
            
            if success:
                successful += 1
            
            # Brief pause between benchmarks
            time.sleep(2)
        
        total_time = time.time() - start_time
        
        # Final summary
        print(f"\n🎯 FINAL SUMMARY")
        print("=" * 60)
        print(f"✅ Successful: {successful}/{total}")
        print(f"⏱️  Total time: {total_time:.1f}s")
        print(f"📁 Base directory: {Path('flamegraphs').absolute()}")
        
        print(f"\n📊 Detailed Results:")
        for benchmark_name, success, flamegraph_file in results:
            status = "✅" if success else "❌"
            print(f"  {status} {benchmark_name:<15}", end="")
            if flamegraph_file:
                file_size = Path(flamegraph_file).stat().st_size
                print(f" → {Path(flamegraph_file).name} ({file_size:,} bytes)")
            else:
                print(" → Failed")
        
        # List all generated files
        print(f"\n📈 All flame graphs in flamegraphs/ directory:")
        svg_files = list(Path("flamegraphs").rglob("*.svg"))
        svg_files.sort()
        for svg_file in svg_files:
            if "perf" in svg_file.name:  # Only show perf-generated ones from this run
                rel_path = svg_file.relative_to("flamegraphs")
                file_size = svg_file.stat().st_size
                print(f"  🔥 {rel_path} ({file_size:,} bytes)")

def main():
    """Main entry point."""
    # Verify we're in the correct directory
    if not Path("run_all_benchmarks.py").exists():
        print("❌ Error: Please run this script from the clean_benchmarks directory")
        print(f"   Current directory: {os.getcwd()}")
        sys.exit(1)
    
    # Check perf permissions
    try:
        result = subprocess.run(['perf', 'list'], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            print("⚠️  Warning: perf may need elevated permissions")
            print("   You might need to run: sudo sysctl kernel.perf_event_paranoid=1")
            print("   Or run this script with appropriate permissions")
    except:
        pass
    
    generator = PerfFlameGraphGenerator()
    generator.run_all_benchmarks()

if __name__ == "__main__":
    main()
