# Hardware/Software Co-Design Benchmark Suite

## Overview
This repository captures a reproducible workflow for profiling Python benchmark variants under a hardware/software co-design study. It couples curated benchmark runners, automated reporting utilities, and archived performance artifacts so results can be regenerated or extended with minimal manual setup.

The project currently focuses on the `crypto_pyaes` and `mdp` workloads from [`pyperformance`](https://github.com/python/pyperformance) and is structured to make it easy to plug in additional benchmarks, prompts, and reports as the project grows.

## Repository Structure
```
.
├── LICENSE                      # Project license (MIT)
├── README.md
├── pyperformance/               # Git submodule snapshot of pyperformance (benchmark sources)
├── reports/                     # HTML and Excel reports for each benchmark
│   ├── aes_results_...          # Timestamped AES benchmark reports
│   └── mdp_results_...          # Timestamped MDP benchmark reports
├── results/                     # Raw profiling outputs (perf, py-spy, metadata) per benchmark variant
│   ├── aes/
│   └── mdp/
├── benchmark_reports/           # Deep-dive PDF reports and hardware diagrams per benchmark
│   ├── AES report.pdf           # Detailed AES benchmark analysis
│   ├── mdp report.pdf           # Detailed MDP benchmark analysis
│   ├── results_for_reports/     # Results and flamegraphs used in the PDF reports
│   │   ├── aes/                 # AES flamegraphs and data
│   │   └── mdp/                 # MDP flamegraphs and data
│   └── hardware_drawings/       # Hardware accelerator block diagrams (PNG, viewable in draw.io)
│       ├── AES.png              # AES hardware accelerator design
│       └── mdp.png              # MDP hardware accelerator design
├── prompts/                     # Prompt engineering documentation
│   └── prompts.txt              # Prompt documentation file
├── presentation/                # PowerPoint presentations of the work
│   └── final_presentation.pptx  # Final presentation of the project
├── scripts/                     # Python utilities that orchestrate benchmark execution & reporting
│   ├── run_benchmarks.py
│   └── build_html_report.py
├── script_crypto_pyaes.sh       # Shell wrapper for AES benchmark suite
├── script_mdp.sh                # Shell wrapper for MDP benchmark suite
└── .gitignore                   # VCS hygiene for generated artifacts
```

> **Note:** The `results_for_reports/` directory contains the flame graphs and data used in the PDF report documents. Updated (and slightly different) results reside under the `results/` & `reports/` directories.

## Prerequisites
- Python 3.10 debug build (`python3-dbg`) to unlock fine-grained profiling symbols.
- `python3 -m venv` module (ships with standard Python installations).
- Linux system with access to `perf` for hardware counters.

Each shell script provisions an isolated virtual environment (`.venv_dbg`) and installs the required Python dependencies:

- `pyperformance`, `pyperf`, and `pyinstrument` for benchmark orchestration and analysis.
- `py-spy` for statistical profiling.
- `numba`, `numpy`, and `plotly` to support benchmark workloads and visualization.

## Getting Started
1. **Clone the repository**
   ```bash
   git clone <your_fork_url>
   cd hw_sw_project
   ```

2. **Review existing reports**
   - HTML outputs live under `reports/<benchmark>_results_<timestamp>/`.
   - PDF deep-dive reports reside in `benchmark_reports/`.
   - Hardware accelerator block diagrams are available in `benchmark_reports/hardware_drawings/` as PNG files (viewable in draw.io).
   - Final presentation is available as `presentation/final_presentation.pptx`.

3. **Inspect scripts**
   - `script_crypto_pyaes.sh` and `script_mdp.sh` expose the complete workflow for running a benchmark family end-to-end.
   - `scripts/run_benchmarks.py` accepts custom variants via `--variant label:path[:pyperf_wrapper]` arguments, ensuring the runner is not hardcoded to specific files.
   - `scripts/build_html_report.py` converts raw results into a rich HTML dashboard.

## Running Benchmarks
Use the provided shell scripts to orchestrate reproducible runs.

### AES (crypto_pyaes)
```bash
chmod +x ./script_crypto_pyaes.sh
./script_crypto_pyaes.sh
```
Key actions:
- Creates (or reuses) `.venv_dbg` with `python3-dbg`.
- Installs/updates dependencies.
- Executes `scripts/run_benchmarks.py` against the AES variants (`pyaes_clean`, `pyaes_opt`, `pyaes_opt2`).
- Stores raw data under `results/aes/` and logs to `results/aes/python_script_log.log`.
- Parses the auto-generated timestamp from the log and builds an HTML report into `reports/aes_results_<timestamp>/`.

### Markov Decision Process (mdp)
```bash
chmod +x ./script_mdp.sh
./script_mdp.sh
```
The pipeline mirrors the AES workflow but targets the MDP benchmark variants (`mdp_clean`, `mdp_opt2`, `mdp_opt3`, `mdp_opt4`). Output lands in `results/mdp/` with reports under `reports/mdp_results_<timestamp>/`.



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

## Repository Artifacts
- **Raw data** (`results/<benchmark>/<variant>/`): includes CSV/JSON metrics, py-spy flames, and perf statistics.
- **HTML reports** (`reports/<benchmark>_results_<timestamp>/`): interactive visualizations built via Plotly.
- **Excel reports** (`reports/<benchmark>_results_<timestamp>/`): Excel files with perf data - aggregated and averaged among x runs (default is 5).
- **PDF reports** (`benchmark_reports/`): comprehensive analysis documents with detailed findings and recommendations.
- **Report data** (`benchmark_reports/results_for_reports/`): flame graphs and data specifically used in the PDF reports.
- **Hardware diagrams** (`benchmark_reports/hardware_drawings/`): PNG block diagrams of custom hardware accelerators (viewable in draw.io).
- **Prompts** (`prompts/`): documentation of LLM prompt engineering relevant to benchmark setup.
- **Presentations** (`presentation/`): PowerPoint presentation summarizing the hardware/software project.


## License
This project is distributed under the terms of the MIT License. See [LICENSE](LICENSE) for details.
