"""
main.py
Entry point for the Network Congestion Simulation System.

Usage:
    python main.py                   # full pipeline (validation + experiments)
    python main.py --validate-only   # M/M/1 validation only
    python main.py --experiment-only # skip validation; run experiments only
    python main.py --debug           # verbose DEBUG-level logging
    python main.py --seed 123        # override master random seed
    python main.py --output-dir out  # write results to a custom directory

Project: Design and Implementation of a Network Congestion Simulation
         System for Nigerian Urban Telecommunications Networks
Dept   : Computer Science, Caleb University, Lagos
"""

import argparse
import logging
import os
import sys


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Network Congestion Simulation System\n"
            "Caleb University, Dept. of Computer Science"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--validate-only",   action="store_true",
                   help="Run the M/M/1 validation check only.")
    p.add_argument("--experiment-only", action="store_true",
                   help="Skip validation; run load-level experiments only.")
    p.add_argument("--debug",           action="store_true",
                   help="Enable DEBUG-level logging (verbose).")
    p.add_argument("--seed",            type=int, default=42,
                   help="Master random seed (default: 42).")
    p.add_argument("--output-dir",      type=str, default="outputs",
                   help="Directory for plots and CSV files (default: outputs/).")
    return p.parse_args()


# ---------------------------------------------------------------------------
# Pipeline stages
# ---------------------------------------------------------------------------

def stage_validation(seed: int, output_dir: str) -> dict:
    from validation import run_validation
    from visualisation import plot_validation
    from utils import print_validation_report

    print("\n" + "=" * 62)
    print("  STAGE 1 – M/M/1 VALIDATION")
    print("=" * 62)
    val_result = run_validation(seed=seed)
    print_validation_report(val_result)
    plot_validation(val_result, output_dir=output_dir)
    return val_result


def stage_experiments(seed: int, output_dir: str) -> None:
    from config import default_config
    from experiments import run_experiments, summarise_experiments, save_results
    from visualisation import (
        plot_performance_summary,
        plot_replication_distributions,
        plot_throughput_line,
    )
    from utils import print_summary_table

    print("\n" + "=" * 62)
    print("  STAGE 2 – LOAD-LEVEL EXPERIMENTS")
    print("=" * 62)

    cfg = default_config()
    cfg.output_dir = output_dir

    print(
        f"\n  Configuration:\n"
        f"    Nodes        : {cfg.num_nodes}\n"
        f"    Service rate : μ = {cfg.service_rate} pkt/s\n"
        f"    Buffer size  : {cfg.buffer_size} packets\n"
        f"    Duration     : {cfg.duration} s / replication\n"
        f"    Replications : {cfg.num_replications}\n"
        f"    Load levels  : {[f'{l:.0%}' for l in cfg.load_levels]}\n"
    )

    raw_df  = run_experiments(cfg, base_seed=seed)
    summary = summarise_experiments(raw_df)

    print_summary_table(summary)
    save_results(raw_df, summary, output_dir=output_dir)

    plot_performance_summary(summary, output_dir=output_dir)
    plot_replication_distributions(raw_df, output_dir=output_dir)
    plot_throughput_line(summary, output_dir=output_dir)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    args = _parse_args()

    # Imports deferred so --help works without all dependencies installed
    from utils import setup_logging, ensure_output_dir

    log_level = logging.DEBUG if args.debug else logging.INFO
    ensure_output_dir(args.output_dir)
    setup_logging(
        level=log_level,
        log_file=os.path.join(args.output_dir, "simulation.log"),
    )

    logger = logging.getLogger(__name__)
    logger.info(
        "Network Congestion Simulation System starting "
        "(seed=%d, output=%s)", args.seed, args.output_dir
    )

    print(
        "\n╔══════════════════════════════════════════════════════════╗\n"
        "║   Network Congestion Simulation System                  ║\n"
        "║   Caleb University, Dept. of Computer Science, Lagos    ║\n"
        "╚══════════════════════════════════════════════════════════╝"
    )

    try:
        if args.validate_only:
            stage_validation(args.seed, args.output_dir)

        elif args.experiment_only:
            stage_experiments(args.seed, args.output_dir)

        else:
            stage_validation(args.seed, args.output_dir)
            stage_experiments(args.seed, args.output_dir)

        abs_out = os.path.abspath(args.output_dir)
        print(f"\n[DONE]  All outputs written to: {abs_out}\n")
        logger.info("All stages complete.  Output directory: %s", abs_out)

    except AssertionError as exc:
        logger.error("Validation assertion failed: %s", exc)
        print(f"\n[ERROR] {exc}\n")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[INTERRUPTED]")
        sys.exit(0)
    except Exception as exc:
        logger.exception("Unexpected error: %s", exc)
        print(f"\n[ERROR] {exc}\n")
        sys.exit(2)


if __name__ == "__main__":
    main()
