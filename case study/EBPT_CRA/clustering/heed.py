import random
import numpy as np # type: ignore
import sys
import os
from typing import List, Any

# Ensure project root is in path for standalone execution
if "__file__" in globals():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if project_root not in sys.path:
        sys.path.append(project_root)

try:
    from core import params # type: ignore
except ImportError:
    # Fallback for complex environments
    import core.params as params # type: ignore

def select_cluster_heads_heed(nodes: List[Any], p_initial: float=0.05, c_prob: float=0.05):
    """
    Implements HEED (Hybrid Energy-Efficient Distributed) clustering.
    
    Phase 1: Initialization
        S_CH = { s | CH_prob(s) > rand } 
        CH_prob is function of residual energy.
    Phase 2: Iteration
        Nodes select best CH based on cost (AMRP: Average Min Reachability Power).
        If no CH, become Tentative CH.
    Phase 3: Finalization
        Tentative CHs become Final CHs if no better CH found.
    
    Simplified for simulation:
    1. Calculate CH_prob based on E_res/E_max.
    2. Select Tentative CHs.
    3. Non-CH nodes pick CH with min cost (distance/power).
    4. Resolve duplications (this is a centralized approximation of HEED's distributed nature).
    """
    
    alive_nodes = [n for n in nodes if getattr(n, 'alive', True)]
    if not alive_nodes:
        return []

    # Reset
    for n in nodes:
        n.is_ch = False
        n.my_heuristic_cost = float('inf')
        n.final_ch = None

    # Constants
    E_min = 1e-4 
    AMRP_constant = 10 # dBm or strict distance measure

    # Phase 1: Initialize Probability
    final_chs = []
    tentative_chs = []

    for node in alive_nodes:
        # P_CH = C_prob * E_residual / E_max
        E_res = getattr(node, 'energy', 0)
        E_max = getattr(node, 'initial_energy', 0.5)
        
        prob_ch = max(E_min, c_prob * (E_res / E_max))
        node.prob_ch = prob_ch
        
        if random.random() < prob_ch:
            tentative_chs.append(node)
            node.is_tentative_ch = True
        else:
            node.is_tentative_ch = False

    # Phase 2: Repeats (Iterations)
    # In distributed HEED, nodes broadcast "I am CH with cost X".
    # Here, we simulate by having all tentative CHs "broadcast".
    # Cost = Intracluster communication cost (AMRP). Simplified as Average Distance to Neighbors?
    # Or just residual energy (secondary parameter).
    # HEED main parameter is residual energy for election, and cost (degree/distance) for tie-breaking.
    
    # We'll use Degree/Distance as cost proxy inverse (Higher degree -> Lower AMRP/Cost? Or Lower Power -> Lower Cost).
    # Let's use Cost = Mean Distance to Neighbors (AMRP proxy).
    
    # Calculate costs for tentative CHs
    for ch in tentative_chs:
        # Distance to BS as a proxy for specific AMRP component?
        # Standard HEED uses AMRP: Average Mean Reachability Power.
        # We'll use distance to BS as a proxy for "Cost to Sink"
        # and inverse density for "Intra-Cluster Cost".
        # Simplified: Cost = 1 / Residual Energy (primary) + Distance to BS (tie breaker logic)
        ch.cost = (1.0 / (getattr(ch, 'energy', 1e-9))) # Lower is better? No, HEED uses cost.
        # Let's say Cost is communication cost.
        # High Energy -> Low Cost.
        pass

    # Simplified Execution:
    # 1. Tentative CHs are candidates.
    # 2. Ordinary nodes choose the least cost CH in range.
    # 3. If no CH in range, node becomes CH itself (Final CH) with probability 1 (eventually).
    
    # Let's just finalize the tentative list + coverage check for simulation speed.
    # If a node is not covered by any tentative CH, it forces itself to be CH.
    
    # Range limit
    Rc = getattr(params, 'TRANSMISSION_RANGE', 30) # type: ignore
    
    covered_nodes = set()
    
    # Join clusters
    for node in alive_nodes:
        if node in tentative_chs:
            final_chs.append(node)
            covered_nodes.add(node)
            continue
            
        # Find best CH in range
        best_ch = None
        min_cost = float('inf')
        
        for ch in tentative_chs:
            dist = np.sqrt((node.x - ch.x)**2 + (node.y - ch.y)**2)
            if dist <= Rc:
                # HEED Cost function: Min Power to reach CH.
                # Power proportional to dist^2
                cost = dist**2 
                if cost < min_cost:
                    min_cost = cost
                    best_ch = ch
        
        if best_ch:
            covered_nodes.add(node)
        else:
            # Not covered -> Force CH (Iteration end property of HEED)
            final_chs.append(node)
            covered_nodes.add(node)
            node.is_ch = True # Force
            
    # Mark final
    for ch in final_chs:
        ch.is_ch = True
        try:
            ch.is_CH = True
        except:
            pass
            
    return final_chs
