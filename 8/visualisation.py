"""
visualisation.py
Publication-quality plots for the network congestion simulation results.
"""

import logging
import os
from typing import Optional

import matplotlib
matplotlib.use("Agg")   # non-interactive backend; safe in headless environments
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

FIGURE_DPI  = 150
LOAD_LABELS = {0.5: "50%", 0.8: "80%", 1.0: "100%", 1.2: "120%"}
COLORS      = ["#2196F3", "#F44336", "#4CAF50", "#FF9800"]


def _style() -> None:
    plt.rcParams.update({
        "font.family":    "DejaVu Sans",
        "font.size":      10,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "axes.grid":      True,
        "grid.linestyle": "--",
        "grid.alpha":     0.45,
        "legend.fontsize": 9,
    })


# ---------------------------------------------------------------------------
# 2 × 2 summary figure
# ---------------------------------------------------------------------------

def plot_performance_summary(
    summary: pd.DataFrame,
    output_dir: str = "outputs",
    filename: str = "performance_summary.png",
) -> str:
    """
    2×2 subplot: Delay, Loss Ratio, Throughput, Queue Length vs. Load.

    Error bars show ±1 standard deviation across replications.

    Args:
        summary   : Aggregated DataFrame from experiments.summarise_experiments().
        output_dir: Directory where the PNG is written.
        filename  : Output file name.

    Returns:
        Absolute path to the saved file.
    """
    _style()
    os.makedirs(output_dir, exist_ok=True)

    loads       = summary["load"].values
    x           = np.arange(len(loads))
    tick_labels = [LOAD_LABELS.get(float(l), f"{l:.1f}") for l in loads]

    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    fig.suptitle(
        "Network Congestion Simulation – Performance vs. Traffic Load\n"
        "Nigerian Urban Telecommunications Network Model",
        fontsize=12, fontweight="bold",
    )

    def _panel(ax, mean_col, std_col, title, ylabel, color):
        means = summary[mean_col].values.astype(float)
        stds  = summary[std_col].fillna(0).values.astype(float)
        bars  = ax.bar(
            x, means, yerr=stds, capsize=5,
            color=color, alpha=0.82, edgecolor="black", linewidth=0.6,
            error_kw={"elinewidth": 1.3, "ecolor": "#333333"},
        )
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.set_xlabel("Traffic Load (% of capacity)")
        ax.set_xticks(x)
        ax.set_xticklabels(tick_labels)
        # Annotate bar tops
        y_range = max(means) - min(means) if max(means) != min(means) else max(means)
        for bar, m, s in zip(bars, means, stds):
            lbl = f"{m:.3f}" if m < 10 else f"{m:.1f}"
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                bar.get_height() + s + 0.02 * (y_range or 1),
                lbl, ha="center", va="bottom", fontsize=8,
            )

    _panel(axes[0, 0],
           "avg_delay_mean",        "avg_delay_std",
           "Average End-to-End Delay",     "Delay (seconds)",          COLORS[0])

    _panel(axes[0, 1],
           "loss_ratio_mean",       "loss_ratio_std",
           "Packet Loss Ratio",             "Loss Ratio (fraction)",    COLORS[1])

    _panel(axes[1, 0],
           "throughput_mean",       "throughput_std",
           "Network Throughput",            "Throughput (packets/s)",   COLORS[2])

    _panel(axes[1, 1],
           "avg_queue_length_mean", "avg_queue_length_std",
           "Average Queue Length",          "Mean Queue Occupancy (pkts)", COLORS[3])

    fig.tight_layout()
    path = os.path.join(output_dir, filename)
    fig.savefig(path, dpi=FIGURE_DPI, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved: %s", path)
    print(f"  Saved: {path}")
    return os.path.abspath(path)


# ---------------------------------------------------------------------------
# M/M/1 validation chart
# ---------------------------------------------------------------------------

def plot_validation(
    val_result: dict,
    output_dir: str = "outputs",
    filename: str = "mm1_validation.png",
) -> str:
    """
    Grouped bar chart comparing M/M/1 theory vs. simulation for E[T] and ρ.

    Args:
        val_result: Dict returned by validation.run_validation().
        output_dir: Output directory.
        filename  : Output file name.

    Returns:
        Absolute path to the saved file.
    """
    _style()
    os.makedirs(output_dir, exist_ok=True)

    theory = val_result["theoretical"]
    sim    = val_result["simulated"]

    labels      = ["E[T] – Mean Sojourn Time (s)", "ρ – Server Utilisation"]
    theory_vals = [theory["E_T"], theory["rho"]]
    sim_vals    = [sim["E_T"],    sim["rho"]]

    x     = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(7, 4.5))
    b1 = ax.bar(x - width / 2, theory_vals, width, label="M/M/1 Theory",
                color="#2196F3", alpha=0.85, edgecolor="black")
    b2 = ax.bar(x + width / 2, sim_vals,    width, label="Simulation",
                color="#4CAF50", alpha=0.85, edgecolor="black")

    errs = val_result["relative_errors"]
    for i, (tv, sv, err) in enumerate(
        zip(theory_vals, sim_vals, [errs["E_T"], errs["rho"]])
    ):
        ax.text(i, max(tv, sv) * 1.05, f"err = {err:.1%}",
                ha="center", fontsize=9, color="darkred", fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Value")
    ax.set_title(
        "M/M/1 Validation: Theory vs. Simulation\n"
        "λ=0.8 pkt/s,  μ=1.0 pkt/s,  T=1000 s"
    )
    ax.legend()
    fig.tight_layout()

    path = os.path.join(output_dir, filename)
    fig.savefig(path, dpi=FIGURE_DPI, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved: %s", path)
    print(f"  Saved: {path}")
    return os.path.abspath(path)


# ---------------------------------------------------------------------------
# Per-load-level replication distribution (box plots)
# ---------------------------------------------------------------------------

def plot_replication_distributions(
    raw_df: pd.DataFrame,
    output_dir: str = "outputs",
    filename: str = "replication_distributions.png",
) -> str:
    """
    Box plots showing delay and loss-ratio distributions at each load level.

    Args:
        raw_df    : Raw replication DataFrame from experiments.run_experiments().
        output_dir: Output directory.
        filename  : Output file name.

    Returns:
        Absolute path to the saved file.
    """
    _style()
    os.makedirs(output_dir, exist_ok=True)

    loads = sorted(raw_df["load"].unique())

    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    fig.suptitle(
        "Replication-Level Distributions by Load Level",
        fontsize=12, fontweight="bold",
    )

    delay_data = [raw_df[raw_df["load"] == l]["avg_delay"].values for l in loads]
    loss_data  = [raw_df[raw_df["load"] == l]["loss_ratio"].values for l in loads]
    xlabels    = [LOAD_LABELS.get(float(l), f"{l:.1f}") for l in loads]

    for ax, data, title, ylabel, color in [
        (axes[0], delay_data, "Average Delay Distribution",     "Delay (s)",         "#BBDEFB"),
        (axes[1], loss_data,  "Packet Loss Ratio Distribution", "Loss Ratio",         "#FFCDD2"),
    ]:
        bp = ax.boxplot(
            data, patch_artist=True, notch=False,
            medianprops=dict(color="black", linewidth=1.5),
        )
        for patch in bp["boxes"]:
            patch.set_facecolor(color)
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.set_xlabel("Traffic Load")
        ax.set_xticklabels(xlabels)

    fig.tight_layout()
    path = os.path.join(output_dir, filename)
    fig.savefig(path, dpi=FIGURE_DPI, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved: %s", path)
    print(f"  Saved: {path}")
    return os.path.abspath(path)


# ---------------------------------------------------------------------------
# Throughput line chart (supplementary)
# ---------------------------------------------------------------------------

def plot_throughput_line(
    summary: pd.DataFrame,
    output_dir: str = "outputs",
    filename: str = "throughput_line.png",
) -> str:
    """
    Line chart of mean throughput vs. load with shaded ±1 std band.

    Args:
        summary   : Aggregated summary DataFrame.
        output_dir: Output directory.
        filename  : Output file name.

    Returns:
        Absolute path to the saved file.
    """
    _style()
    os.makedirs(output_dir, exist_ok=True)

    loads  = summary["load"].values.astype(float) * 100   # convert to %
    means  = summary["throughput_mean"].values.astype(float)
    stds   = summary["throughput_std"].fillna(0).values.astype(float)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(loads, means, marker="o", color="#2196F3", linewidth=2, label="Mean throughput")
    ax.fill_between(loads, means - stds, means + stds,
                    alpha=0.25, color="#2196F3", label="±1 std dev")
    ax.set_xlabel("Traffic Load (% of capacity)")
    ax.set_ylabel("Throughput (packets/second)")
    ax.set_title("Network Throughput vs. Traffic Load")
    ax.legend()
    fig.tight_layout()

    path = os.path.join(output_dir, filename)
    fig.savefig(path, dpi=FIGURE_DPI, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved: %s", path)
    print(f"  Saved: {path}")
    return os.path.abspath(path)
