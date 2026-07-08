"""
utils.py
Shared helper functions: logging setup, directory creation, console reporting.
"""

import logging
import os
import sys
from typing import Optional, Tuple

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
) -> None:
    """
    Configure the root logger.

    Args:
        level   : Minimum log level (e.g. logging.DEBUG).
        log_file: Optional path; if given, messages are also appended there.
    """
    fmt     = "%(asctime)s  %(levelname)-8s  %(name)s – %(message)s"
    datefmt = "%H:%M:%S"

    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)
        handlers.append(logging.FileHandler(log_file, mode="a"))

    logging.basicConfig(level=level, format=fmt, datefmt=datefmt,
                        handlers=handlers, force=True)


# ---------------------------------------------------------------------------
# Filesystem
# ---------------------------------------------------------------------------

def ensure_output_dir(path: str) -> str:
    """Create *path* (and parents) if absent; return the absolute path."""
    abs_path = os.path.abspath(path)
    os.makedirs(abs_path, exist_ok=True)
    return abs_path


# ---------------------------------------------------------------------------
# Console reporting
# ---------------------------------------------------------------------------

def print_summary_table(summary: pd.DataFrame) -> None:
    """Print a formatted ASCII summary table to stdout."""
    col_map = {
        "load":                   "Load",
        "avg_delay_mean":         "Delay (s)",
        "avg_delay_std":          "±Delay",
        "loss_ratio_mean":        "Loss Ratio",
        "loss_ratio_std":         "±Loss",
        "throughput_mean":        "Tput (pkt/s)",
        "throughput_std":         "±Tput",
        "avg_queue_length_mean":  "Queue Len",
        "avg_queue_length_std":   "±Queue",
    }
    display = summary[[c for c in col_map if c in summary.columns]].copy()
    display = display.rename(columns=col_map)

    for col in display.columns:
        if col != "Load":
            display[col] = display[col].apply(
                lambda v: f"{v:.4f}" if pd.notna(v) else "N/A"
            )

    sep = "=" * 90
    print(f"\n{sep}")
    print("EXPERIMENT RESULTS SUMMARY")
    print(sep)
    print(display.to_string(index=False))
    print(f"{sep}\n")


def print_validation_report(val_result: dict) -> None:
    """Print a human-readable M/M/1 validation report."""
    theory = val_result["theoretical"]
    sim    = val_result["simulated"]
    errs   = val_result["relative_errors"]
    status = "PASSED" if val_result["passed"] else "FAILED"

    sep = "=" * 62
    print(f"\n{sep}")
    print(f"  M/M/1 VALIDATION REPORT  [{status}]")
    print(sep)
    print(f"  λ = 0.80  μ = 1.00  ρ_theory = {theory['rho']:.4f}")
    print()
    hdr = f"  {'Metric':<30} {'Theory':>10} {'Simulation':>12} {'Rel. Error':>12}"
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))
    print(
        f"  {'Mean sojourn time E[T] (s)':<30} "
        f"{theory['E_T']:>10.4f} {sim['E_T']:>12.4f} "
        f"{errs['E_T']:>11.2%}"
    )
    print(
        f"  {'Server utilisation ρ':<30} "
        f"{theory['rho']:>10.4f} {sim['rho']:>12.4f} "
        f"{errs['rho']:>11.2%}"
    )
    print(f"{sep}\n")


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

def confidence_interval_95(values: list) -> Tuple[float, float]:
    """
    Compute the 95 % confidence interval half-width (t-distribution).

    Args:
        values: Numeric observations.

    Returns:
        (mean, half_width) – use as mean ± half_width.
    """
    from scipy import stats as sp_stats
    arr = np.asarray(values, dtype=float)
    n   = len(arr)
    if n < 2:
        return float(np.mean(arr)), 0.0
    mean = float(np.mean(arr))
    hw   = float(sp_stats.sem(arr) * sp_stats.t.ppf(0.975, df=n - 1))
    return mean, hw
