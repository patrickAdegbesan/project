"""
poisson_traffic.py
Generates synthetic packet traffic following a Poisson arrival process.
"""

import logging
from typing import Optional, Tuple

import numpy as np

from packet import Packet

logger = logging.getLogger(__name__)


class PoissonTraffic:
    """
    Packet traffic source modelling a Poisson arrival process.

    Inter-arrival times are exponentially distributed with mean 1/arrival_rate,
    which is the continuous-time equivalent of a Poisson counting process.

    Attributes:
        arrival_rate     : Mean packet arrivals per second (λ).
        packet_size_range: (min_bytes, max_bytes) for uniform payload-size sampling.
        _rng             : Seeded NumPy Generator for reproducibility.
        _packet_counter  : Monotonically increasing packet ID.
    """

    def __init__(
        self,
        arrival_rate: float,
        packet_size_range: Tuple[int, int] = (64, 1500),
        seed: int = 42,
    ) -> None:
        if arrival_rate <= 0:
            raise ValueError("arrival_rate must be positive.")
        if packet_size_range[0] > packet_size_range[1]:
            raise ValueError("packet_size_range min must be <= max.")

        self.arrival_rate: float = arrival_rate
        self.packet_size_range: Tuple[int, int] = packet_size_range
        self._rng: np.random.Generator = np.random.default_rng(seed)
        self._packet_counter: int = 0

    # ------------------------------------------------------------------
    # Random variate generators
    # ------------------------------------------------------------------

    def generate_inter_arrival_time(self) -> float:
        """Draw the next inter-arrival time from Exp(λ)."""
        iat = float(self._rng.exponential(scale=1.0 / self.arrival_rate))
        logger.debug("IAT=%.6f s", iat)
        return iat

    def generate_packet_size(self) -> int:
        """Draw a payload size uniformly from [min_bytes, max_bytes]."""
        lo, hi = self.packet_size_range
        return int(self._rng.integers(lo, hi + 1))

    # ------------------------------------------------------------------
    # Packet factory
    # ------------------------------------------------------------------

    def create_packet(
        self,
        current_time: float,
        source: int = 0,
        dest: int = 1,
    ) -> Packet:
        """
        Create and return a new Packet stamped with *current_time*.

        Args:
            current_time: Simulation clock value at the moment of creation.
            source      : Source node ID.
            dest        : Destination node ID.
        """
        self._packet_counter += 1
        pkt = Packet(
            packet_id=self._packet_counter,
            source=source,
            dest=dest,
            size=self.generate_packet_size(),
            creation_time=current_time,
            arrival_time=current_time,
        )
        logger.debug("Created %s", pkt)
        return pkt

    def reset(self, seed: Optional[int] = None) -> None:
        """Reset packet counter and optionally re-seed the RNG."""
        self._packet_counter = 0
        if seed is not None:
            self._rng = np.random.default_rng(seed)
