"""
network_node.py
Defines a single network node: FIFO buffering and exponential service.

After serving a packet the node forwards it to self.next_node (if set).
The SimulationEngine wires next_node to create the linear chain topology.
"""

import logging
from typing import Any, Dict, List, Optional

import simpy
import numpy as np

from packet import Packet
from fifo_queue import FIFOQueue

logger = logging.getLogger(__name__)


class NetworkNode:
    """
    Models a single router/switch in the simulated network.

    Attributes:
        node_id      : Unique integer identifier.
        queue        : FIFOQueue – the finite packet buffer.
        service_rate : Mean service completions per second (μ).
        env          : Shared SimPy Environment.
        next_node    : Downstream NetworkNode; None means this is the egress node.
        _rng         : Per-node seeded NumPy Generator for service times.
        _server      : SimPy Resource representing the single transmission unit.
        stats        : Per-run counters: received, forwarded, dropped, delays.
    """

    def __init__(
        self,
        node_id: int,
        env: simpy.Environment,
        service_rate: float,
        buffer_size: int = 50,
        seed: int = 0,
    ) -> None:
        if service_rate <= 0:
            raise ValueError("service_rate must be positive.")

        self.node_id: int = node_id
        self.queue: FIFOQueue = FIFOQueue(max_size=buffer_size)
        self.service_rate: float = service_rate
        self.env: simpy.Environment = env
        self.next_node: Optional["NetworkNode"] = None

        self._rng: np.random.Generator = np.random.default_rng(seed)
        self._server: simpy.Resource = simpy.Resource(env, capacity=1)
        self._node_seed: int = seed   # stored so reset() can recreate _rng

        self.stats: Dict[str, Any] = {
            "received": 0,
            "forwarded": 0,
            "dropped": 0,
            "delays": [],
        }

    # ------------------------------------------------------------------
    # SimPy process entry points
    # ------------------------------------------------------------------

    def process_arrival(self, packet: Packet) -> None:
        """
        Handle a packet arriving at this node.

        Stamps the arrival time, tries to enqueue, and if accepted spawns
        a serve_packet process.
        """
        self.stats["received"] += 1
        packet.arrival_time = self.env.now

        accepted = self.queue.enqueue(packet)
        if not accepted:
            self.stats["dropped"] += 1
            logger.debug(
                "Node %d – pkt %d DROPPED at t=%.4f",
                self.node_id, packet.packet_id, self.env.now,
            )
        else:
            self.env.process(self._serve(packet))

    def _serve(self, packet: Packet):
        """
        SimPy generator: acquire server → dequeue → transmit → forward.

        Service time is drawn from Exp(μ).
        """
        with self._server.request() as req:
            yield req                   # wait until the server is free

            # Remove packet from buffer now that the server has claimed it
            self.queue.dequeue()

            service_time = float(
                self._rng.exponential(scale=1.0 / self.service_rate)
            )
            yield self.env.timeout(service_time)

            packet.departure_time = self.env.now
            delay = packet.calculate_delay()
            self.stats["forwarded"] += 1
            self.stats["delays"].append(delay)

            logger.debug(
                "Node %d – pkt %d served  delay=%.4f s  t=%.4f",
                self.node_id, packet.packet_id, delay, self.env.now,
            )

            # Forward downstream
            if self.next_node is not None:
                self.next_node.process_arrival(packet)

    # ------------------------------------------------------------------
    # Derived metrics
    # ------------------------------------------------------------------

    def average_delay(self) -> float:
        delays: List[float] = self.stats["delays"]
        return float(np.mean(delays)) if delays else 0.0

    def loss_ratio(self) -> float:
        if self.stats["received"] == 0:
            return 0.0
        return self.stats["dropped"] / self.stats["received"]

    def average_queue_length(self) -> float:
        return self.queue.average_length()

    # ------------------------------------------------------------------
    # Reset between replications
    # ------------------------------------------------------------------

    def reset(self, env: simpy.Environment, seed: Optional[int] = None) -> None:
        """
        Rebind to a new SimPy Environment and clear all state.

        SimPy Resource objects are tied to an Environment, so a new Resource
        must be created whenever the engine creates a fresh Environment.

        Args:
            env : New SimPy Environment created by SimulationEngine.reset().
            seed: Optional new RNG seed; defaults to the original node seed.
        """
        self.env = env
        self._server = simpy.Resource(env, capacity=1)
        self.queue.reset()
        self.stats = {"received": 0, "forwarded": 0, "dropped": 0, "delays": []}
        effective_seed = seed if seed is not None else self._node_seed
        self._rng = np.random.default_rng(effective_seed)

    def __repr__(self) -> str:
        nxt = self.next_node.node_id if self.next_node else "egress"
        return (
            f"NetworkNode(id={self.node_id}, μ={self.service_rate}, "
            f"next={nxt}, {self.queue})"
        )
