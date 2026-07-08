"""
packet.py
Defines the Packet dataclass representing a network packet in the simulation.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Packet:
    """
    Represents a single network packet travelling through the simulated network.

    Attributes:
        packet_id      : Unique identifier for the packet.
        source         : ID of the originating node.
        dest           : ID of the destination node.
        size           : Payload size in bytes.
        creation_time  : Simulation time at which the packet was generated.
        arrival_time   : Simulation time at which the packet arrived at a node queue.
        departure_time : Simulation time at which the packet left the server.
        dropped        : True if the packet was discarded due to a full buffer.
    """

    packet_id: int
    source: int
    dest: int
    size: int
    creation_time: float
    arrival_time: float = 0.0
    departure_time: Optional[float] = None
    dropped: bool = False

    def calculate_delay(self) -> float:
        """
        Return sojourn time (queuing + service) at the node where this was last served.
        Returns 0.0 if the packet was dropped or has not yet departed.
        """
        if self.dropped or self.departure_time is None:
            return 0.0
        return self.departure_time - self.arrival_time

    def __repr__(self) -> str:
        status = "DROPPED" if self.dropped else f"delay={self.calculate_delay():.4f}s"
        return (
            f"Packet(id={self.packet_id}, src={self.source}, "
            f"dst={self.dest}, size={self.size}B, {status})"
        )
