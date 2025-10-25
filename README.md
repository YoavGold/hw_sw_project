# Hardware/Software Co-Design Benchmark Suite

## Overview
This repository captures a reproducible workflow for profiling Python benchmark variants under a hardware/software co-design study. It couples curated benchmark runners, automated reporting utilities, and archived performance artifacts so results can be regenerated or extended with minimal manual setup.

The project currently focuses on the `crypto_pyaes` and `mdp` workloads from [`pyperformance`](https://github.com/python/pyperformance) and is structured to make it easy to plug in additional benchmarks, prompts, and reports as the project grows.

## Repository Structure
```
.
├── LICENSE                      # Project license (MIT)
├── README.md                    # You are here
├── pyperformance/               # Git submodule snapshot of pyperformance (benchmark sources)
├── reports/                     # HTML reports built from captured benchmark runs
│   ├── aes_results_...          # Timestamped AES benchmark reports
│   ├── mdp_results_...          # Timestamped MDP benchmark reports
│   └── report_<benchmark>.txt   # (Pattern) Text summary saved per benchmark run
├── results/                     # Raw profiling outputs (perf, py-spy, metadata) per benchmark variant
│   ├── aes/
│   └── mdp/
├── benchmark_reports/           # (Planned) Deep-dive PDF reports per benchmark
├── prompts/                     # (Planned) Prompt engineering PDF documentation
├── scripts/                     # Python utilities that orchestrate benchmark execution & reporting
│   ├── run_benchmarks.py
│   └── build_html_report.py
├── script_crypto_pyaes.sh       # Shell wrapper for AES benchmark suite
├── script_mdp.sh                # Shell wrapper for MDP benchmark suite
└── .gitignore                   # VCS hygiene for generated artifacts
```

> **Note:** The `benchmark_reports/` and `prompts/` directories are reserved for upcoming PDF artifacts. Populate them as new reports and prompt documentation become available.

## Prerequisites
- Python 3.10 debug build (`python3-dbg`) to unlock fine-grained profiling symbols.
- `python3 -m venv` module (ships with standard Python installations).
- Linux system with access to `perf` for hardware counters.
- Optional but recommended: ability to install system packages (e.g., `sudo apt install linux-tools-common linux-tools-$(uname -r)`).

Each shell script provisions an isolated virtual environment (`.venv_dbg`) and installs the required Python dependencies:

- `pyperformance`, `pyperf`, and `pyinstrument` for benchmark orchestration and analysis.
- `py-spy` for statistical profiling.
- `numba`, `numpy`, and `plotly` to support benchmark workloads and visualization.

## Getting Started
1. **Clone the repository**
   ```bash
   git clone <your_fork_url>
   cd hw_sw_project
   git submodule update --init --recursive  # ensure pyperformance assets are available
   ```

2. **Review existing reports**
   - HTML outputs live under `reports/<benchmark>_results_<timestamp>/`.
   - Text summaries follow the `reports/report_<benchmark>.txt` naming convention (e.g., `reports/report_crypto_pyaes.txt`).
   - Future PDF deep dives will reside in `benchmark_reports/`.

3. **Inspect scripts**
   - `script_crypto_pyaes.sh` and `script_mdp.sh` expose the complete workflow for running a benchmark family end-to-end.
   - `scripts/run_benchmarks.py` accepts custom variants via `--variant label:path[:pyperf_wrapper]` arguments, ensuring the runner is not hardcoded to specific files.
   - `scripts/build_html_report.py` converts raw results into a rich HTML dashboard.

## Running Benchmarks
Use the provided shell scripts to orchestrate reproducible runs.

### AES (crypto_pyaes)
```bash
./script_crypto_pyaes.sh
```
Key actions:
- Creates (or reuses) `.venv_dbg` with `python3-dbg`.
- Installs/update dependencies.
- Executes `scripts/run_benchmarks.py` against the AES variants (`pyaes_clean`, `pyaes_opt`, `pyaes_opt2`).
- Stores raw data under `results/aes/` and logs to `results/aes/python_script_log.log`.
- Parses the auto-generated timestamp from the log and builds an HTML report into `reports/aes_results_<timestamp>/`.

### Markov Decision Process (mdp)
```bash
./script_mdp.sh
```
Pipeline mirrors the AES workflow but targets the MDP benchmark variants (`mdp_clean`, `mdp_opt2`, `mdp_opt3`, `mdp_opt4`). Output lands in `results/mdp/` with reports under `reports/mdp_results_<timestamp>/`.

### Custom Benchmarks
To add a new benchmark:
1. Copy one of the shell scripts and adjust the variant list to point to the desired `pyperformance` workload.
2. Save the shell script following the `script_<benchmark>.sh` convention and commit it under version control.
3. Run the script to populate `results/<benchmark>/` and generate a new HTML report directory.
4. Capture a text summary as `reports/report_<benchmark>.txt` and, optionally, place an in-depth PDF in `benchmark_reports/<benchmark>.pdf`.
5. Document any prompt engineering context in `prompts/<benchmark>_prompt.pdf`.

## Generating Reports Manually
You can invoke the reporting utility directly if you already know the timestamp of a run:
```bash
source .venv_dbg/bin/activate
python scripts/build_html_report.py \
  --results-dir results/aes \
  --timestamp 20251025_220832 \
  --transpose \
  --report-dir reports
```
Replace the `--results-dir` and `--timestamp` values as needed. The script assembles charts, tables, and summaries from the raw `perf` and `py-spy` outputs.

## Benchmark Artifacts
- **Raw data** (`results/<benchmark>/<variant>/`): includes CSV/JSON metrics, py-spy flames, and perf statistics.
- **Text reports** (`reports/report_<benchmark>.txt`): concise summaries with command history and high-level findings.
- **HTML reports** (`reports/<benchmark>_results_<timestamp>/`): interactive visualization built via Plotly.
- **PDF deep dives** (`benchmark_reports/<benchmark>.pdf`, planned): polished narratives for distribution.
- **Prompts** (`prompts/<benchmark>_prompt.pdf`, planned): documentation of LLM prompt engineering relevant to the benchmark setup.

Maintain a consistent naming convention across these assets to simplify automation and traceability.

## Version Control Workflow
- Commit frequently with descriptive messages that capture *what* changed and *why* (e.g., `Add py-spy flamegraph export for mdp_opt3`).
- Group related modifications together (scripts, configuration, documentation) to keep history reviewable.
- Reference benchmark names in commit messages when updating results or reports.
- Tag milestone commits (e.g., `v1.0-benchmarks`) after significant reporting cycles.

Following these practices ensures the repository remains audit-friendly and demonstrates a clear development narrative, which also contributes to the bonus credit criteria.

## Troubleshooting
- **Missing `python3-dbg`:** Install via `sudo apt install python3.10-dbg` (adjust the version to match your distribution).
- **`perf` permissions:** On some systems you may need to adjust kernel settings (`sudo sysctl kernel.perf_event_paranoid=1`) or run under `sudo`.
- **Dependency conflicts:** Recreate the virtual environment by removing `.venv_dbg` and rerunning the desired script.
- **Log parsing errors:** Verify that `results/<benchmark>/python_script_log.log` contains the `time stamp for this run:` line. If not, inspect `scripts/run_benchmarks.py` output for earlier failures.

## Contributing & Next Steps
1. Flesh out the `benchmark_reports/` directory with PDF analyses summarizing key findings per benchmark.
2. Document your prompt engineering workflow inside `prompts/` to capture the experimentation history.
3. Extend coverage to additional `pyperformance` benchmarks by adding new shell scripts and variants.
4. Consider integrating continuous benchmarking (e.g., GitHub Actions) to monitor performance regressions automatically.

Pull requests are welcome—ensure all scripts remain executable (`chmod +x`) and provide clear README updates when altering repository structure.

## License
This project is distributed under the terms of the MIT License. See [LICENSE](LICENSE) for details.
