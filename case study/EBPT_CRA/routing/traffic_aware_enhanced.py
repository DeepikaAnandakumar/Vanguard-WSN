"""
Enhanced traffic-aware routing with congestion modeling.

This module adds an *experimental* traffic-awareness layer on top of the
existing EBPT-based routing. The goal is to **explore**, in a transparent
and reproducible way, how simple congestion-aware terms interact with the
energy- and fairness-aware weight functions already in the system.

Important:
- We do **not** claim this is the first traffic-aware WSN routing scheme.
- We treat this as a concrete design choice that is evaluated empirically
  in the 50-node (and partially 100-node) experiment suites.
"""

import numpy as np
from typing import List, Dict, Optional
from collections import defaultdict, deque
from energy.first_order_radio import ETX, ERX
from routing.ebpt_weight import ebpt_edge_weight
from core import params


class TrafficModel:
    """
    Model traffic load and congestion in the network.

    Features:
    1. Historical traffic tracking (simple moving average).
    2. A lightweight congestion indicator.
    3. Queue-depth-style bookkeeping for potential extensions.
    """
    
    def __init__(self, history_window: int = 10):
        """
        Initialize traffic model.
        
        Args:
            history_window: Number of rounds to track in history
        """
        self.history_window = history_window
        self.traffic_history = defaultdict(lambda: deque(maxlen=history_window))
        self.queue_depths = defaultdict(int)
        self.congestion_threshold = 0.7  # 70% of capacity
    
    def update_traffic(self, node_id: int, traffic_load: float) -> None:
        """Update traffic history for a node."""
        self.traffic_history[node_id].append(traffic_load)
    
    def get_traffic_load(self, node_id: int) -> float:
        """Get current traffic load (average over history)."""
        history = self.traffic_history[node_id]
        if not history:
            return 0.0
        return np.mean(history)
    
    def get_congestion_level(self, node_id: int, capacity: float = 1.0) -> float:
        """
        Get congestion level (0 = no congestion, 1 = fully congested).
        
        Args:
            node_id: Node identifier
            capacity: Maximum traffic capacity
        
        Returns:
            Congestion level [0, 1]
        """
        load = self.get_traffic_load(node_id)
        return min(load / capacity, 1.0) if capacity > 0 else 0.0
    
    def is_congested(self, node_id: int, capacity: float = 1.0) -> bool:
        """Check if node is congested."""
        return self.get_congestion_level(node_id, capacity) > self.congestion_threshold


def traffic_aware_weight(node_i, node_j, gamma: float = 0.5, 
                         traffic_model: Optional[TrafficModel] = None,
                         traffic_weight: float = 0.3) -> float:
    """
    Enhanced weight function combining energy, fairness, and traffic awareness.

    Working formula:
        W(n, m, γ, τ) = [Energy_Score / (1 + γ·Load)] / (1 + τ·Congestion)
    
    Where:
    - Energy_Score: Energy efficiency (existing)
    - γ: Fairness parameter (existing)
    - Load: Current load on candidate parent (existing)
    - τ: Traffic weight parameter (NEW)
    - Congestion: Traffic congestion level (NEW)
    
    Args:
        node_i: Source node
        node_j: Candidate parent node
        gamma: Fairness parameter [0, 1]
        traffic_model: Traffic model for congestion estimation
        traffic_weight: Weight of traffic penalty [0, 1]
    
    Returns:
        Weight score (higher is better)
    """
    # Base energy-aware weight (existing)
    base_weight = ebpt_edge_weight(node_i, node_j, gamma)
    
    if base_weight <= 0:
        return -1
    
    # Traffic-aware penalty (NEW)
    if traffic_model is not None:
        congestion = traffic_model.get_congestion_level(node_j.id)
        traffic_penalty = 1 + (traffic_weight * congestion)
        final_weight = base_weight / traffic_penalty
    else:
        # Fallback: use load as proxy for traffic
        load_j = getattr(node_j, 'load', 0)
        traffic_penalty = 1 + (traffic_weight * min(load_j / 10.0, 1.0))
        final_weight = base_weight / traffic_penalty
    
    return final_weight


def compute_traffic_aware_ebpt(nodes, bs, gamma: float = 0.5,
                               traffic_model: Optional[TrafficModel] = None,
                               traffic_weight: float = 0.3):
    """
    Compute an EBPT-style tree with traffic-aware routing.

    Algorithm:
    1. Build the tree using distance ordering (as in standard EBPT).
    2. For each node, select a parent that trades off:
       - Energy efficiency.
       - Load balance (γ parameter).
       - Traffic avoidance (congestion term).
    3. Update the traffic model as the tree is built.
    
    Args:
        nodes: List of sensor nodes
        bs: Base station node
        gamma: Fairness parameter
        traffic_model: Traffic model instance
        traffic_weight: Weight of traffic in routing decisions
    """
    # Clear existing relationships
    for n in nodes:
        n.parent = None
        n.children = []
        if not hasattr(n, 'load') or n.load is None:
            n.load = 0
        else:
            n.load = 0
    
    # Sort by distance to BS
    nodes_sorted = sorted(nodes, key=lambda n: n.distance_to(bs))
    
    # Initialize traffic model if not provided
    if traffic_model is None:
        traffic_model = TrafficModel()
    
    # Build tree with traffic awareness
    for n in nodes_sorted:
        if not getattr(n, 'alive', True):
            continue
        
        # Candidate parents: BS + nodes closer to BS
        candidates = [bs] + [
            m for m in nodes_sorted 
            if m is not n 
            and m.distance_to(bs) < n.distance_to(bs) 
            and getattr(m, 'alive', True)
        ]
        
        # Select best parent using traffic-aware weight
        parent = max(
            candidates,
            key=lambda candidate: traffic_aware_weight(
                n, candidate, gamma, traffic_model, traffic_weight
            )
        )
        
        n.parent = parent
        if parent is not bs:
            parent.children.append(n)
            parent.load = len(parent.children)
            
            # Update traffic model (NEW)
            # Estimate traffic: number of children * data rate
            estimated_traffic = parent.load * params.DATA_BITS
            traffic_model.update_traffic(parent.id, estimated_traffic)
    
    return traffic_model


def compute_hybrid_routing(nodes, bs, gamma: float = 0.5,
                           traffic_weight: float = 0.3,
                           adaptive: bool = True,
                           network_state: Optional[Dict] = None):
    """
    Hybrid routing combining energy, fairness, and traffic awareness.

    This routine wires together the energy/fairness-aware EBPT weights
    with an additional traffic term and an optional coarse-grained
    adaptation of `traffic_weight` based on a supplied `network_state`.
    It is intended as an **experimental baseline** for studying how
    congestion-aware tweaks behave in the existing framework, not as a
    claimed "first" or final optimal design.
    
    Args:
        nodes: List of sensor nodes
        bs: Base station node
        gamma: Fairness parameter (can be adapted)
        traffic_weight: Weight of traffic in decisions
        adaptive: Whether to adapt parameters based on network state
        network_state: Current network state for adaptation
    
    Returns:
        Traffic model instance (for tracking)
    """
    # Adaptive parameter adjustment (NEW)
    if adaptive and network_state:
        # Adjust traffic_weight based on congestion
        congestion_level = network_state.get('avg_congestion', 0)
        if congestion_level > 0.7:
            traffic_weight = min(traffic_weight * 1.5, 0.5)  # Increase traffic awareness
        elif congestion_level < 0.3:
            traffic_weight = max(traffic_weight * 0.8, 0.1)  # Decrease (less important)
    
    # Build traffic-aware tree
    traffic_model = compute_traffic_aware_ebpt(
        nodes, bs, gamma, None, traffic_weight
    )
    
    return traffic_model

