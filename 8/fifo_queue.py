"""
fifo_queue.py
Implements a finite FIFO buffer used at each network node.
"""

import logging
from typing import List, Optional

import numpy as np

from packet import Packet

logger = logging.getLogger(__name__)


class FIFOQueue:
    """
    Finite-capacity First-In-First-Out packet buffer.

    Attributes:
        max_size          : Maximum number of packets the buffer can hold.
        queue             : Internal list acting as the FIFO store.
        dropped_count     : Running total of packets discarded due to overflow.
        max_length_history: Snapshot of queue depth recorded after every
                            enqueue/dequeue; used for average-occupancy calculation.
    """

    def __init__(self, max_size: int) -> None:
        if max_size <= 0:
            raise ValueError("max_size must be a positive integer.")
        self.max_size: int = max_size
        self.queue: List[Packet] = []
        self.dropped_count: int = 0
        self.max_length_history: List[int] = []

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    def enqueue(self, packet: Packet) -> bool:
        """
        Add *packet* to the tail of the queue.

        Returns True on success, False (and marks packet.dropped) if full.
        """
        if self.is_full():
            packet.dropped = True
            self.dropped_count += 1
            logger.debug("Buffer full – dropped %s", packet)
            return False

        self.queue.append(packet)
        self.max_length_history.append(len(self.queue))
        logger.debug("Enqueued %s (depth %d)", packet, len(self.queue))
        return True

    def dequeue(self) -> Optional[Packet]:
        """Remove and return the head-of-line packet, or None if empty."""
        if self.is_empty():
            return None
        packet = self.queue.pop(0)
        self.max_length_history.append(len(self.queue))
        logger.debug("Dequeued %s (depth %d)", packet, len(self.queue))
        return packet

    # ------------------------------------------------------------------
    # State queries
    # ------------------------------------------------------------------

    def is_full(self) -> bool:
        return len(self.queue) >= self.max_size

    def is_empty(self) -> bool:
        return len(self.queue) == 0

    def current_length(self) -> int:
        return len(self.queue)

    def average_length(self) -> float:
        if not self.max_length_history:
            return 0.0
        return float(np.mean(self.max_length_history))

    def reset(self) -> None:
        """Clear buffer and all statistics."""
        self.queue.clear()
        self.dropped_count = 0
        self.max_length_history.clear()

    def __repr__(self) -> str:
        return (
            f"FIFOQueue(depth={self.current_length()}/{self.max_size}, "
            f"dropped={self.dropped_count})"
        )
