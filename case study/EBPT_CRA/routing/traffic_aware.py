from core import params
from energy.first_order_radio import ETX, ERX

def traffic_aware_weight(node_i, node_j):
    """
    Traffic-Aware Edge Weight.
    Prioritizes nodes with low Queue Length / Load.
    
    Formula:
    W_ij = (1 / (1 + Load_j)) * (Energy_j / Initial_Energy_j)
    """
    if node_i.energy <= 0 or node_j.energy <= 0:
        return -1

    load_j = getattr(node_j, 'load', 0)
    # Normalize load factor
    load_factor = 1.0 / (1.0 + 0.5 * load_j) 
    
    # Energy factor
    energy_factor = node_j.energy / getattr(node_j, 'initial_energy', 1.0)
    
    return load_factor * energy_factor

def compute_traffic_aware_tree(nodes, bs):
    """
    Builds a routing tree optimized for traffic (congestion) avoidance.
    """
    # Clear previous
    for n in nodes:
        n.parent = None
        n.children = []
        
    nodes_sorted = sorted(nodes, key=lambda n: n.distance_to(bs))
    
    for n in nodes_sorted:
        if not getattr(n, 'alive', True):
            continue
            
        candidates = [bs] + [m for m in nodes_sorted if m is not n and m.distance_to(bs) < n.distance_to(bs) and getattr(m, 'alive', True)]
        
        # Select best parent based on Traffic Aware Weight
        parent = max(candidates, key=lambda candidate: traffic_aware_weight(n, candidate))
        
        n.parent = parent
        if parent is not bs:
            parent.children.append(n)
