"""
experiments.py
Runs the load-level experiment suite and aggregates results.

For each load level in cfg.load_levels the arrival rate is set to:
    λ = load_level × μ   (so utilisation ρ = load_level)

cfg.num_replications independent runs are executed per load level; each run
uses a unique seed derived from a master seed to ensure reproducibility while
keeping replications statistically independent.
"""

import logging
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from config import SimConfig, default_config
from simulation_engine import SimulationEngine

logger = logging.getLogger(__name__)


def run_single_replication(
    cfg: SimConfig,
    load_multiplier: float,
    rep_index: int,
    base_seed: int = 100,
) -> Dict[str, Any]:
    """
    Execute one simulation replication at a specified traffic-load level.

    Args:
        cfg             : Base simulation configuration.
        load_multiplier : Fraction of service capacity to offer (e.g. 0.8 → 80 %).
        rep_index       : Zero-based replication index; varies the random seed.
        base_seed       : Root seed; actual seed = base_seed + rep_index * 1000.

    Returns:
        Dict with keys: load, replication, avg_delay, loss_ratio,
        throughput, avg_queue_length, total_received, total_dropped,
        total_forwarded.
    """
    effective_lambda = load_multiplier * cfg.service_rate

    run_cfg = SimConfig(
        arrival_rate=effective_lambda,
        service_rate=cfg.service_rate,
        num_nodes=cfg.num_nodes,
        buffer_size=cfg.buffer_size,
        duration=cfg.duration,
        packet_size_range=cfg.packet_size_range,
    )

    seed = base_seed + rep_index * 1000
    engine = SimulationEngine(run_cfg, seed=seed)
    engine.run()
    stats = engine.get_statistics()

    result: Dict[str, Any] = {
        "load":             load_multiplier,
        "replication":      rep_index + 1,
        "avg_delay":        stats["avg_delay"],
        "loss_ratio":       stats["loss_ratio"],
        "throughput":       stats["throughput"],
        "avg_queue_length": stats["avg_queue_length"],
        "total_received":   stats["total_received"],
        "total_dropped":    stats["total_dropped"],
        "total_forwarded":  stats["total_forwarded"],
    }
    logger.info(
        "Load=%.2f rep=%d  delay=%.4f s  loss=%.4f  tput=%.2f pkt/s",
        load_multiplier, rep_index + 1,
        result["avg_delay"], result["loss_ratio"], result["throughput"],
    )
    return result


def run_experiments(
    cfg: Optional[SimConfig] = None,
    base_seed: int = 100,
) -> pd.DataFrame:
    """
    Run the full experiment matrix (all load levels × all replications).

    Args:
        cfg      : Simulation configuration; defaults to default_config().
        base_seed: Root random seed.

    Returns:
        DataFrame with one row per (load_level, replication).
    """
    if cfg is None:
        cfg = default_config()

    rows: List[Dict[str, Any]] = []
    total = len(cfg.load_levels) * cfg.num_replications
    done  = 0

    for load in cfg.load_levels:
        logger.info("=== Load level %.2f ===", load)
        for rep in range(cfg.num_replications):
            rows.append(run_single_replication(cfg, load, rep, base_seed))
            done += 1
            print(f"  Progress: {done}/{total} runs complete", end="\r", flush=True)

    print()   # newline after progress line
    df = pd.DataFrame(rows)
    logger.info("Experiment matrix complete (%d rows).", len(df))
    return df


def summarise_experiments(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate replication-level results into a per-load-level summary.

    Computes mean and standard deviation for avg_delay, loss_ratio,
    throughput, and avg_queue_length at each load level.

    Args:
        df: Raw DataFrame from run_experiments().

    Returns:
        Summary DataFrame with columns: load, <metric>_mean, <metric>_std.
    """
    metrics = ["avg_delay", "loss_ratio", "throughput", "avg_queue_length"]
    agg = df.groupby("load")[metrics].agg(["mean", "std"]).reset_index()

    # Flatten MultiIndex columns: (metric, stat) → "metric_stat"
    agg.columns = (
        ["load"] + [f"{m}_{s}" for m, s in agg.columns[1:]]
    )

    logger.info("Summary:\n%s", agg.to_string(index=False))
    return agg


def save_results(
    df: pd.DataFrame,
    summary: pd.DataFrame,
    output_dir: str = "outputs",
) -> None:
    """
    Write raw and summary DataFrames to CSV files.

    Args:
        df        : Raw replication-level results.
        summary   : Aggregated summary table.
        output_dir: Output directory (created if absent).
    """
    import os
    os.makedirs(output_dir, exist_ok=True)

    raw_path     = os.path.join(output_dir, "results_raw.csv")
    summary_path = os.path.join(output_dir, "results_summary.csv")

    df.to_csv(raw_path, index=False)
    summary.to_csv(summary_path, index=False)

    print(f"  Saved: {raw_path}")
    print(f"  Saved: {summary_path}")
    logger.info("Results written to %s and %s", raw_path, summary_path)
