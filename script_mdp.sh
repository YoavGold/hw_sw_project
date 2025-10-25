#!/usr/bin/env bash
set -euo pipefail

VENV_DIR=".venv_dbg"
PYDBG="/usr/bin/python3-dbg"

# Check and create debug venv if not exists
if [ ! -d "$VENV_DIR" ]; then
    echo "[INFO] Creating $VENV_DIR using $PYDBG..."
    if [ ! -x "$PYDBG" ]; then
        echo "[ERROR] $PYDBG not found or not executable!"
        echo "Install it with: sudo apt install python3.10-dbg"
        exit 1
    fi
    "$PYDBG" -m venv "$VENV_DIR"

else
    echo "[INFO] Using existing $VENV_DIR environment."
fi

# Activate venv
source "$VENV_DIR/bin/activate"

# Install dependencies
echo "[INFO] Installing required packages..."
pip install -U pip
pip install numba numpy plotly pyinstrument pyperf pyperformance py-spy

# Run benchmarks
LOG_DIR="results/mdp"
LOG_FILE="$LOG_DIR/python_script_log.log"
echo "[INFO] Logging run_benchmarks.py output to $LOG_FILE"
echo "[INFO] Running MDP benchmarks..."
"$VENV_DIR/bin/python3" -u scripts/run_benchmarks.py \
  --perf-runs 5 \
  --flush-bytes 1GiB \
  --python "$VENV_DIR/bin/python3" \
  --pyspy "$VENV_DIR/bin/py-spy" \
  --variant mdp_opt3:pyperformance/pyperformance/data-files/benchmarks/bm_mdp/no_pyperf_versions/mdp_opt3.py:pyperformance/pyperformance/data-files/benchmarks/bm_mdp/run_benchmark3.py \
  --variant mdp_opt4:pyperformance/pyperformance/data-files/benchmarks/bm_mdp/no_pyperf_versions/mdp_opt4.py:pyperformance/pyperformance/data-files/benchmarks/bm_mdp/run_benchmark4.py \
  --variant mdp_opt2:pyperformance/pyperformance/data-files/benchmarks/bm_mdp/no_pyperf_versions/mdp_opt2.py:pyperformance/pyperformance/data-files/benchmarks/bm_mdp/run_benchmark2.py \
  --variant mdp_clean:pyperformance/pyperformance/data-files/benchmarks/bm_mdp/no_pyperf_versions/mdp_clean.py:pyperformance/pyperformance/data-files/benchmarks/bm_mdp/run_benchmark.py \
  --outdir results/mdp/ | tee "$LOG_FILE"

# Extract timestamp from log
timestamp=$(grep -oP 'time stamp for this run:\s*\K[0-9_]+' "$LOG_FILE")

if [ -z "$timestamp" ]; then
    echo "[ERROR] Failed to extract timestamp from $LOG_FILE"
    exit 1
fi
echo "[INFO] Parsed timestamp: $timestamp"

# Generate report
REPORT_DIR="reports"
REPORT_LOG="$REPORT_DIR/python_script_log.log"
echo "[INFO] Logging build_html_report.py output to $REPORT_LOG"
"$VENV_DIR/bin/python3" -u scripts/build_html_report.py \
  --results-dir results/mdp \
  --timestamp "$timestamp" \
  --transpose \
  --report-dir "$REPORT_DIR" | tee "$REPORT_LOG"

echo "[DONE] Report built successfully for timestamp: $timestamp"
