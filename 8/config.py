"""
config.py
Centralised configuration dataclass for the simulation system.
"""

from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class SimConfig:
    """
    Simulation configuration container.

    Fields:
        arrival_rate      : Packet arrival rate λ (packets/second).
        service_rate      : Node service rate μ (packets/second).
        num_nodes         : Number of sequential nodes in the network path.
        buffer_size       : Maximum packets each FIFO buffer can hold.
        duration          : Simulated time (seconds) per replication.
        packet_size_range : (min, max) payload sizes in bytes.
        num_replications  : Independent replications per experiment condition.
        load_levels       : Traffic-load multipliers applied to μ to derive λ.
        output_dir        : Directory where plots and CSV results are written.
    """

    arrival_rate: float = 0.8
    service_rate: float = 1.0
    num_nodes: int = 3
    buffer_size: int = 50
    duration: int = 500
    packet_size_range: Tuple[int, int] = (64, 1500)
    num_replications: int = 5
    load_levels: Tuple[float, ...] = (0.5, 0.8, 1.0, 1.2)
    output_dir: str = "outputs"


def default_config() -> SimConfig:
    """Return the standard simulation configuration."""
    return SimConfig()


def validation_config() -> SimConfig:
    """
    Single-node M/M/1 configuration for theory validation.

    λ=0.8, μ=1.0 → ρ=0.8; theoretical mean sojourn E[T] = 1/(μ−λ) = 5.0 s.
    A large buffer (200) approximates the infinite-queue assumption of M/M/1.
    A longer duration (1000 s) reduces variance for a fair comparison.
    """
    return SimConfig(
        arrival_rate=0.8,
        service_rate=1.0,
        num_nodes=1,
        buffer_size=200,
        duration=1000,
        num_replications=1,
    )
