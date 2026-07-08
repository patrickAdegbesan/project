"""
validation.py
Validates the simulation engine against closed-form M/M/1 queuing theory.

M/M/1 formulae used:
    ρ    = λ / μ                          (server utilisation)
    E[T] = 1 / (μ − λ)                   (mean sojourn time)
    E[L] = ρ / (1 − ρ)                   (mean number in system)
    E[W] = ρ / (μ − λ)                   (mean waiting time in queue)
"""

import logging
from typing import Dict, Any

from config import validation_config
from simulation_engine import SimulationEngine

logger = logging.getLogger(__name__)

TOLERANCE = 0.10   # 10 % relative error threshold


def mm1_theoretical(lam: float, mu: float) -> Dict[str, float]:
    """
    Compute closed-form M/M/1 metrics.

    Args:
        lam: Arrival rate λ (packets/s).
        mu : Service rate μ (packets/s).

    Returns:
        Dict with keys rho, E_T, E_L, E_W.

    Raises:
        ValueError: If the system is unstable (ρ ≥ 1).
    """
    rho = lam / mu
    if rho >= 1.0:
        raise ValueError(
            f"M/M/1 system is unstable: ρ={rho:.3f} ≥ 1.  "
            "Reduce λ or increase μ."
        )
    return {
        "rho": rho,
        "E_T": 1.0 / (mu - lam),
        "E_L": rho / (1.0 - rho),
        "E_W": rho / (mu - lam),
    }


def run_validation(seed: int = 42) -> Dict[str, Any]:
    """
    Run the M/M/1 validation experiment and return a result dictionary.

    Steps:
      1. Compute theoretical metrics for λ=0.8, μ=1.0 (E[T]=5.0 s, ρ=0.8).
      2. Simulate a single-node network for 1000 simulated seconds.
      3. Compare simulated mean sojourn time with E[T].
      4. Assert relative error < TOLERANCE (10 %).

    Args:
        seed: Master random seed.

    Returns:
        Dict with keys: theoretical, simulated, relative_errors, passed.

    Raises:
        AssertionError: If relative error exceeds TOLERANCE.
    """
    cfg = validation_config()
    lam, mu = cfg.arrival_rate, cfg.service_rate

    theory = mm1_theoretical(lam, mu)
    logger.info("M/M/1 theory (λ=%.2f, μ=%.2f): %s", lam, mu, theory)

    engine = SimulationEngine(cfg, seed=seed)
    engine.run()
    sim_stats = engine.get_statistics()

    sim_E_T = sim_stats["avg_delay"]
    # Utilisation estimated as fraction of service capacity consumed
    sim_rho = sim_stats["total_forwarded"] / (cfg.duration * mu)

    rel_err_T   = abs(sim_E_T - theory["E_T"]) / theory["E_T"]
    rel_err_rho = abs(sim_rho - theory["rho"])  / theory["rho"]

    logger.info(
        "Validation:\n"
        "  Theory E[T]=%.4f  Sim E[T]=%.4f  err=%.2f%%\n"
        "  Theory ρ=%.4f     Sim ρ=%.4f     err=%.2f%%",
        theory["E_T"], sim_E_T, rel_err_T * 100,
        theory["rho"],  sim_rho,  rel_err_rho * 100,
    )

    result = {
        "theoretical": theory,
        "simulated": {
            "E_T": sim_E_T,
            "rho": sim_rho,
            "loss_ratio": sim_stats["loss_ratio"],
            "throughput":  sim_stats["throughput"],
        },
        "relative_errors": {
            "E_T": rel_err_T,
            "rho": rel_err_rho,
        },
        "passed": rel_err_T < TOLERANCE,
    }

    assert rel_err_T < TOLERANCE, (
        f"Validation FAILED: E[T] relative error {rel_err_T:.2%} exceeds "
        f"tolerance {TOLERANCE:.0%}.  "
        f"Theory={theory['E_T']:.4f}  Sim={sim_E_T:.4f}"
    )

    print(
        f"\n[VALIDATION PASSED]\n"
        f"  Theoretical E[T] = {theory['E_T']:.4f} s\n"
        f"  Simulated   E[T] = {sim_E_T:.4f} s\n"
        f"  Relative error   = {rel_err_T:.2%}  (tolerance {TOLERANCE:.0%})\n"
    )
    return result
