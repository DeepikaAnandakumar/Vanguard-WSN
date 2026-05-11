import random
from core import params

def select_cluster_heads(nodes, p=None, method='deterministic'):
    """
    Select cluster heads from sensor nodes.
    
    Args:
        nodes: List of sensor nodes
        p: Cluster head probability (default from params.CH_PROB)
        method: Selection method - 'deterministic', 'random', or 'energy_aware'
    
    Returns:
        List of selected cluster head nodes
    """
    if p is None:
        p = params.CH_PROB
    
    chs = []
    
    # Reset all nodes
    for node in nodes:
        node.is_ch = False
        try:
            node.is_CH = False
        except:
            pass
    
    alive_nodes = [n for n in nodes if getattr(n, 'alive', True)]
    
    if method == 'deterministic':
        # Deterministic selection based on ID
        # "node selected as CH if node.id % int(1/p) == 0"
        step = int(1/p) if p > 0 else 100
        for node in alive_nodes:
            if node.id % step == 0:
                node.is_ch = True
                try:
                    node.is_CH = True
                except:
                    pass
                chs.append(node)
    
    elif method == 'random':
        # Random selection with probability p
        for node in alive_nodes:
            if random.random() < p:
                node.is_ch = True
                try:
                    node.is_CH = True
                except:
                    pass
                chs.append(node)
    
    elif method == 'energy_aware':
        # LEACH-style energy-aware selection
        # Nodes with higher energy are more likely to become CHs
        if not alive_nodes:
            return chs
        
        # Calculate average energy
        avg_energy = sum(n.energy for n in alive_nodes) / len(alive_nodes)
        
        # For each node, probability depends on energy relative to average
        # Higher energy -> higher probability
        for node in alive_nodes:
            energy_ratio = node.energy / avg_energy if avg_energy > 0 else 1.0
            # Threshold: T(n) = p / (1 - p * (r mod 1/p))
            # Simplified: use energy-weighted probability
            threshold = p * energy_ratio
            if random.random() < min(threshold, 1.0):
                node.is_ch = True
                try:
                    node.is_CH = True
                except:
                    pass
                chs.append(node)
    
    return chs


def select_cluster_heads_energy_aware(nodes, p=None, energy_aware=True):
    """
    Select cluster heads using energy-aware (LEACH-inspired) thresholding.
    
    Nodes with higher remaining energy are more likely to be selected as CH.
    Uses a threshold-based approach: a node becomes CH if:
    - Its remaining energy is above a threshold (function of total initial energy)
    - It was not recently a CH (not tracked currently, but can be extended)
    - A probabilistic check passes (weighted by energy)
    
    Args:
        nodes: List of sensor nodes
        p: Base cluster head probability (default from params.CH_PROB)
        energy_aware: If True, modulate probability by node's energy level
    
    Returns:
        List of selected cluster head nodes
    """
    if p is None:
        p = params.CH_PROB
    
    if not energy_aware:
        return select_cluster_heads(nodes, p)
    
    chs = []
    alive_nodes = [n for n in nodes if getattr(n, 'alive', True)]
    
    if not alive_nodes:
        return chs
    
    # Calculate average initial energy
    initial_energies = [getattr(n, 'initial_energy', 1.0) for n in alive_nodes]
    avg_init_energy = sum(initial_energies) / len(initial_energies) if initial_energies else 1.0
    
    # Normalize energy levels (0 to 1)
    for node in alive_nodes:
        init_e = getattr(node, 'initial_energy', 1.0)
        curr_e = getattr(node, 'energy', 0)
        energy_ratio = curr_e / init_e if init_e > 0 else 0
        node._energy_ratio = max(0, min(1, energy_ratio))  # clamp to [0,1]
    
    # Select CHs: use energy-weighted probability
    for node in alive_nodes:
        # Base probability modulated by node's energy ratio
        # Higher energy -> higher chance to be CH
        energy_weight = node._energy_ratio  # 0 to 1
        effective_p = p * (1 + energy_weight)  # scaled probability [p, 2p]
        
        # Probabilistic selection
        node.is_ch = False
        try:
            node.is_CH = False
        except:
            pass
        
        if random.random() < effective_p:
            node.is_ch = True
            try:
                node.is_CH = True
            except:
                pass
            chs.append(node)
    
    # Ensure at least one CH is selected (if any alive nodes)
    if not chs and alive_nodes:
        # Select the node with highest energy
        best = max(alive_nodes, key=lambda n: n._energy_ratio)
        best.is_ch = True
        try:
            best.is_CH = True
        except:
            pass
        chs.append(best)
    
    return chs
