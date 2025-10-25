#!/usr/bin/env python3
"""
Robust benchmark profiling runner.

Key features:
- Variants provided via CLI (no hardcoded list).
- No emojis or machine-specific paths.
- Tool locations are discovered from PATH by default; can be overridden.
- Optional sudo-free cache flush before each perf run.
- Clean, timestamped output layout.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple, List


@dataclass
class Variant:
    label: str
    bench_script: Path
    pyperf_wrapper: Optional[Path] = None  # optional


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Run profiling (py-spy + perf stat) on one or more benchmark scripts."
    )
    p.add_argument(
        "--python",
        dest="python",
        default=os.environ.get("VENV_PYTHON", sys.executable),
        help="Python interpreter to run benchmarks (default: env VENV_PYTHON or current interpreter)",
    )
    p.add_argument(
        "--pyspy",
        dest="pyspy",
        default=os.environ.get("PYSPY", shutil.which("py-spy") or ""),
        help="py-spy executable (default: env PYSPY or discovered in PATH)",
    )
    p.add_argument(
        "--perf",
        dest="perf",
        default=shutil.which("perf") or "",
        help="perf executable (default: discovered in PATH)",
    )
    p.add_argument(
        "--variant",
        action="append",
        required=True,
        metavar="LABEL:BENCH[:PYPERF_WRAPPER]",
        help=(
            "Add a variant. BENCH and optional PYPERF_WRAPPER are file paths.\n"
            "Example: --variant pyaes_clean:./pyaes_clean.py:../pyperformance/run_benchmark.py\n"
            "         --variant pyaes_opt:./pyaes_opt.py"
        ),
    )
    p.add_argument(
        "--outdir",
        default="results",
        help="Root directory for outputs (default: results)",
    )
    p.add_argument(
        "--perf-runs",
        type=int,
        default=5,
        help="Number of perf stat runs per variant (default: 5)",
    )
    p.add_argument(
        "--perf-use-internal-repeats",
        action="store_true",
        help="Use 'perf stat -r N' instead of launching N separate runs.",
    )
    p.add_argument(
        "--pyspy-rate",
        type=int,
        default=100,
        help="py-spy sampling rate in Hz (default: 100)",
    )
    p.add_argument(
        "--pyspy-duration",
        type=float,
        default=None,
        help="py-spy duration in seconds (default: run for full program duration)",
    )
    p.add_argument(
        "--bench-args",
        default="",
        help="Extra arguments to append to each benchmark invocation (quoted string).",
    )
    p.add_argument(
        "--flush-bytes",
        type=str,
        default="1GiB",
        help="Sudo-free cache flush working set size (e.g., 0, 512MiB, 1GiB). 0 disables. Default: 1GiB",
    )
    p.add_argument(
        "--sleep-between-runs",
        type=float,
        default=1.0,
        help="Sleep seconds between perf runs (default: 1.0)",
    )
    p.add_argument(
        "--sleep-between-variants",
        type=float,
        default=2.0,
        help="Sleep seconds between variants (default: 2.0)",
    )
    return p.parse_args()


def parse_size(s: str) -> int:
    """Parse sizes like '0', '4096', '512MiB', '1GiB' into bytes."""
    s = s.strip().lower()
    if s == "0":
        return 0
    mult = 1
    if s.endswith("kib"):
        mult, s = 1024, s[:-3]
    elif s.endswith("kb"):
        mult, s = 1000, s[:-2]
    elif s.endswith("mib"):
        mult, s = 1024**2, s[:-3]
    elif s.endswith("mb"):
        mult, s = 1000**2, s[:-2]
    elif s.endswith("gib"):
        mult, s = 1024**3, s[:-3]
    elif s.endswith("gb"):
        mult, s = 1000**3, s[:-2]
    return int(float(s) * mult)


def ensure_paths(python_path: str, pyspy_path: str, perf_path: str) -> None:
    missing = []
    if not shutil.which(python_path) and not Path(python_path).exists():
        missing.append(f"python: {python_path}")
    if not shutil.which(pyspy_path) and not Path(pyspy_path).exists():
        missing.append(f"py-spy: {pyspy_path or '(not set)'}")
    if not shutil.which(perf_path) and not Path(perf_path).exists():
        missing.append(f"perf: {perf_path or '(not set)'}")
    if missing:
        raise FileNotFoundError("Required tool(s) not found -> " + ", ".join(missing))


def ts() -> str:
    return time.strftime("%Y%m%d_%H%M%S")


def flush_caches(flush_bytes: int) -> bool:
    """Sudo-free cache thrash: allocate N bytes and touch each 4 KiB page once."""
    if flush_bytes <= 0:
        return False
    try:
        step = 4096
        import gc as _gc

        _gc.collect()
        b = bytearray(flush_bytes)
        for i in range(0, flush_bytes, step):
            b[i] = (b[i] + 1) & 0xFF
        del b
        _gc.collect()
        time.sleep(0.2)
        return True
    except MemoryError:
        print("Cache flush skipped (MemoryError).")
        return False
    except Exception as e:
        print(f"Cache flush failed: {e}")
        return False


def run_pyspy_flamegraph(pyspy: str, python: str, script_path: Path, out_svg: Path,
                         rate: int, duration: Optional[float], bench_args: str) -> Tuple[bool, float]:
    out_svg.parent.mkdir(parents=True, exist_ok=True)
    cmd = [pyspy, "record", "-o", str(out_svg), "-r", str(rate)]
    if duration is not None and duration > 0:
        cmd += ["-d", str(duration)]
    cmd += ["--", python, str(script_path)]
    if bench_args:
        cmd += bench_args.split()

    print("py-spy:", " ".join(cmd))
    start = time.time()
    res = subprocess.run(cmd, capture_output=True, text=True)
    dur = time.time() - start

    # Determine if py-spy result is acceptable
    svg_exists = out_svg.exists() and out_svg.stat().st_size > 0
    stderr = (res.stderr or "").strip()
    stdout = (res.stdout or "").strip()
    nonfatal_errors = (
        "No child process" in stderr
        or "No such process" in stderr
        or "process exited" in stdout
    )

    if (res.returncode == 0 and svg_exists) or (svg_exists and nonfatal_errors):
        size = out_svg.stat().st_size
        print(f"py-spy SVG generated: {out_svg} ({size} bytes) in {dur:.2f}s")
        return True, dur

    # Otherwise treat as real failure
    print(f"py-spy failed (exit={res.returncode})")
    if stderr:
        print(stderr)
    if stdout:
        print(stdout)
    return False, dur



def run_perf_stat(perf: str, python: str, script_path: Path, out_txt: Path, run_idx: int,
                  bench_args: str, flush_bytes: int) -> Tuple[bool, float]:
    out_txt.parent.mkdir(parents=True, exist_ok=True)

    if flush_bytes > 0:
        print(f"Flushing caches before perf run {run_idx} ...")
        flushed = flush_caches(flush_bytes)
        print(f"Cache flush: {'OK' if flushed else 'skipped'}")

    cmd = [perf, "stat", "-d", "-d", "-d", "-o", str(out_txt), "--", python, str(script_path)]
    if bench_args:
        cmd += bench_args.split()

    print(f"perf run {run_idx}:", " ".join(cmd))
    start = time.time()
    res = subprocess.run(cmd, capture_output=True, text=True)
    dur = time.time() - start

    if res.stdout:
        with open(out_txt.with_suffix(".program_stdout.txt"), "w") as f:
            f.write(res.stdout)
    if res.stderr:
        with open(out_txt.with_suffix(".stderr.txt"), "w") as f:
            f.write(res.stderr)

    ok = (res.returncode == 0)
    print(f"{'OK' if ok else 'FAIL'} perf run {run_idx} finished in {dur:.2f}s -> {out_txt.name}")
    return ok, dur


def run_perf_stat_internal_repeats(perf: str, python: str, script_path: Path, out_txt: Path,
                                   repeats: int, bench_args: str, flush_bytes: int) -> Tuple[bool, float]:
    out_txt.parent.mkdir(parents=True, exist_ok=True)

    if flush_bytes > 0:
        print("Flushing caches before perf stat ...")
        flushed = flush_caches(flush_bytes)
        print(f"Cache flush: {'OK' if flushed else 'skipped'}")

    cmd = [perf, "stat", "-r", str(repeats), "-d", "-d", "-d", "-o", str(out_txt), "--", python, str(script_path)]
    if bench_args:
        cmd += bench_args.split()

    print("perf stat:", " ".join(cmd))
    start = time.time()
    res = subprocess.run(cmd, capture_output=True, text=True)
    dur = time.time() - start

    # perf outputs to the file; but still capture stderr for issues
    if res.stderr:
        with open(out_txt.with_suffix(".stderr.txt"), "w") as f:
            f.write(res.stderr)

    ok = (res.returncode == 0) and out_txt.exists()
    print(f"{'OK' if ok else 'FAIL'} perf stat finished in {dur:.2f}s -> {out_txt.name}")
    return ok, dur


def run_pyperf_wrapper(python: str, wrapper_script: Path, out_dir: Path, bench_args: str) -> Tuple[bool, float]:
    out_dir.mkdir(parents=True, exist_ok=True)
    log_out = out_dir / "run_benchmark_stdout.txt"
    log_err = out_dir / "run_benchmark_stderr.txt"
    cmd = [python, str(wrapper_script)]

    print("pyperformance wrapper:", " ".join(cmd))
    start = time.time()
    with open(log_out, "w") as fo, open(log_err, "w") as fe:
        res = subprocess.run(cmd, stdout=fo, stderr=fe, text=True)
    dur = time.time() - start
    ok = (res.returncode == 0)
    print(f"{'OK' if ok else 'FAIL'} pyperformance wrapper finished in {dur:.2f}s -> logs in {out_dir}")
    return ok, dur


def parse_variant_spec(spec: str) -> Variant:
    # LABEL:BENCH[:WRAPPER]
    parts = spec.split(":")
    if len(parts) < 2:
        raise ValueError(f"Invalid --variant spec '{spec}'. Expected LABEL:BENCH[:PYPERF_WRAPPER]")
    label = parts[0].strip()
    bench = Path(parts[1].strip())
    wrapper = Path(parts[2].strip()) if len(parts) >= 3 and parts[2].strip() else None
    return Variant(label=label, bench_script=bench, pyperf_wrapper=wrapper)


def run_variant(v: Variant, python: str, pyspy: str, perf: str, out_root: Path,
                perf_runs: int, internal_repeats: bool,
                pyspy_rate: int, pyspy_duration: Optional[float],
                bench_args: str, flush_bytes: int,
                sleep_between_runs: float,
                run_stamp: str) -> bool:
    print("\n" + "=" * 70)
    print(f"Variant: {v.label}")
    print("=" * 70)

    if not v.bench_script.exists():
        print(f"Benchmark script not found: {v.bench_script}")
        return False
    if v.pyperf_wrapper and not v.pyperf_wrapper.exists():
        print(f"pyperformance wrapper not found: {v.pyperf_wrapper}")
        return False

    stamp = run_stamp
    base_dir = out_root / v.label / stamp
    flame_dir = base_dir / "flamegraph"
    perf_dir = base_dir / "perf"
    logs_dir = base_dir / "logs"

    # py-spy
    svg = flame_dir / f"flamegraph_pyspy_{v.label}.svg"
    ok1, _ = run_pyspy_flamegraph(pyspy, python, v.bench_script, svg, pyspy_rate, pyspy_duration, bench_args)

    # perf stat
    ok2_all = True
    if internal_repeats:
        out_txt = perf_dir / "perf_stat.txt"
        ok2, _ = run_perf_stat_internal_repeats(
            perf, python, v.bench_script, out_txt, perf_runs, bench_args, flush_bytes
        )
        ok2_all = ok2_all and ok2
    else:
        for i in range(1, perf_runs + 1):
            out_txt = perf_dir / f"perf_run_{i}.txt"
            ok2, _ = run_perf_stat(perf, python, v.bench_script, out_txt, i, bench_args, flush_bytes)
            ok2_all = ok2_all and ok2
            time.sleep(sleep_between_runs)

    # pyperformance wrapper (optional)
    ok3 = True
    if v.pyperf_wrapper:
        ok3, _ = run_pyperf_wrapper(python, v.pyperf_wrapper, logs_dir, bench_args)

    print(f"\nOutputs for {v.label}: {base_dir.resolve()}")
    return ok1 and ok2_all and ok3


def main():
    args = parse_args()
    run_stamp = ts()
    # Resolve tools
    python = args.python
    pyspy = args.pyspy
    perf = args.perf
    ensure_paths(python, pyspy, perf)

    # Parse variants
    variants: List[Variant] = [parse_variant_spec(s) for s in args.variant]

    # Output root
    out_root = Path(args.outdir)

    # Flush size
    flush_bytes = parse_size(args.flush_bytes)

    print("Profiling Suite")
    print(f"Using python: {python}")
    print(f"Using py-spy:  {pyspy}")
    print(f"Using perf:    {perf}")
    print(f"Output root:   {out_root.resolve()}")
    print(f"Perf runs:     {args.perf_runs} ({'perf -r' if args.perf_use_internal_repeats else 'separate launches'})")
    print(f"py-spy rate:   {args.pyspy_rate} Hz")
    print(f"py-spy dur:    {args.pyspy_duration if args.pyspy_duration else 'program duration'}")
    print(f"Cache flush:   {args.flush_bytes} ({flush_bytes} bytes)")
    if args.bench_args:
        print(f"Extra bench args: {args.bench_args}")

    successes = 0
    for v in variants:
        ok = run_variant(
            v=v,
            python=python,
            pyspy=pyspy,
            perf=perf,
            out_root=out_root,
            perf_runs=args.perf_runs,
            internal_repeats=args.perf_use_internal_repeats,
            pyspy_rate=args.pyspy_rate,
            pyspy_duration=args.pyspy_duration,
            bench_args=args.bench_args,
            flush_bytes=flush_bytes,
            sleep_between_runs=args.sleep_between_runs,
            run_stamp=run_stamp,
        )
        if ok:
            successes += 1
        time.sleep(args.sleep_between_variants)

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Successful variants: {successes}/{len(variants)}")
    print(f"Results root: {out_root.resolve()}")
    if out_root.exists():
        print("\nGenerated flamegraphs:")
        for p in out_root.rglob("flamegraph_pyspy_*.svg"):
            try:
                size = p.stat().st_size
                print(f"  - {p} ({size} bytes)")
            except FileNotFoundError:
                pass
    print("time stamp for this run:", run_stamp)


if __name__ == "__main__":
    main()
