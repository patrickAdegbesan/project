"""
simulation_engine.py
Orchestrates the discrete-event simulation.

Topology: linear chain  src → node[0] → node[1] → … → node[N-1] → sink

Packets are injected by a Poisson process at node[0].  After each node
finishes serving a packet it calls node[i+1].process_arrival() to forward
it downstream.  Statistics are collected at every node and aggregated.
"""

import logging
from typing import Any, Dict, List, Optional

import simpy
import numpy as np

from network_node import NetworkNode
from poisson_traffic import PoissonTraffic
from config import SimConfig

logger = logging.getLogger(__name__)


class SimulationEngine:
    """
    Top-level simulation controller.

    Attributes:
        cfg               : SimConfig with all tunable parameters.
        env               : SimPy discrete-event environment.
        nodes             : Ordered list of NetworkNode objects (ingress→egress).
        traffic_generator : PoissonTraffic instance driving arrivals.
        _base_seed        : Master seed; component seeds are derived from it.
        stats             : Dictionary populated after run() completes.
    """

    def __init__(self, cfg: SimConfig, seed: int = 42) -> None:
        self.cfg = cfg
        self._base_seed = seed
        self.env: simpy.Environment = simpy.Environment()
        self.nodes: List[NetworkNode] = []
        self.traffic_generator: Optional[PoissonTraffic] = None
        self.stats: Dict[str, Any] = {}
        self._build()

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def _build(self) -> None:
        """Instantiate nodes and traffic generator; wire the forwarding chain."""
        rng = np.random.default_rng(self._base_seed)
        node_seeds = rng.integers(0, 2**31, size=self.cfg.num_nodes).tolist()
        traffic_seed = int(rng.integers(0, 2**31))

        self.nodes = [
            NetworkNode(
                node_id=i,
                env=self.env,
                service_rate=self.cfg.service_rate,
                buffer_size=self.cfg.buffer_size,
                seed=int(node_seeds[i]),
            )
            for i in range(self.cfg.num_nodes)
        ]

        # Wire linear forwarding chain: node[i] → node[i+1]
        for i in range(len(self.nodes) - 1):
            self.nodes[i].next_node = self.nodes[i + 1]

        self.traffic_generator = PoissonTraffic(
            arrival_rate=self.cfg.arrival_rate,
            packet_size_range=self.cfg.packet_size_range,
            seed=traffic_seed,
        )

        logger.info(
            "Built %d-node chain  λ=%.3f pkt/s  μ=%.3f pkt/s  T=%d s",
            self.cfg.num_nodes,
            self.cfg.arrival_rate,
            self.cfg.service_rate,
            self.cfg.duration,
        )

    # ------------------------------------------------------------------
    # SimPy generator
    # ------------------------------------------------------------------

    def _packet_generator(self):
        """Inject Poisson-distributed packets into the ingress node."""
        dest_id = self.cfg.num_nodes - 1
        while True:
            iat = self.traffic_generator.generate_inter_arrival_time()
            yield self.env.timeout(iat)
            pkt = self.traffic_generator.create_packet(
                current_time=self.env.now,
                source=0,
                dest=dest_id,
            )
            self.nodes[0].process_arrival(pkt)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Run the simulation for cfg.duration simulated seconds."""
        self.env.process(self._packet_generator())
        logger.info("Simulation starting …")
        self.env.run(until=self.cfg.duration)
        logger.info("Simulation finished at t=%.2f s", self.env.now)
        self.stats = self._collect_statistics()

    def get_statistics(self) -> Dict[str, Any]:
        """Return the statistics dict populated by run()."""
        if not self.stats:
            logger.warning("get_statistics() called before run().")
        return self.stats

    def reset(self, seed: Optional[int] = None) -> None:
        """
        Prepare the engine for a fresh independent replication.

        A new SimPy Environment is required because environments cannot be
        restarted.  Each node is rebound to the new environment.
        """
        if seed is not None:
            self._base_seed = seed

        new_env = simpy.Environment()
        self.env = new_env
        self.stats = {}
        self._build()
        logger.info("Engine reset (seed=%d).", self._base_seed)

    # ------------------------------------------------------------------
    # Statistics aggregation
    # ------------------------------------------------------------------

    def _collect_statistics(self) -> Dict[str, Any]:
        """
        Aggregate node-level counters into network-level metrics.

        - loss_ratio  : based on ingress (node[0]) arrivals vs. total drops
        - avg_delay   : mean sojourn time at the egress node
        - throughput  : egress forwarding rate (packets per second)
        - avg_queue   : mean queue occupancy averaged across all nodes
        """
        ingress = self.nodes[0]
        egress  = self.nodes[-1]

        total_received  = ingress.stats["received"]
        total_dropped   = sum(n.stats["dropped"] for n in self.nodes)
        total_forwarded = egress.stats["forwarded"]

        egress_delays = egress.stats["delays"]
        avg_delay  = float(np.mean(egress_delays)) if egress_delays else 0.0
        loss_ratio = total_dropped / total_received if total_received else 0.0
        throughput = total_forwarded / self.cfg.duration
        avg_queue  = float(np.mean([n.average_queue_length() for n in self.nodes]))

        per_node = [
            {
                "node_id":          n.node_id,
                "received":         n.stats["received"],
                "forwarded":        n.stats["forwarded"],
                "dropped":          n.stats["dropped"],
                "avg_delay":        n.average_delay(),
                "loss_ratio":       n.loss_ratio(),
                "avg_queue_length": n.average_queue_length(),
            }
            for n in self.nodes
        ]

        return {
            "avg_delay":        avg_delay,
            "loss_ratio":       loss_ratio,
            "throughput":       throughput,
            "avg_queue_length": avg_queue,
            "total_received":   total_received,
            "total_dropped":    total_dropped,
            "total_forwarded":  total_forwarded,
            "per_node":         per_node,
        }
