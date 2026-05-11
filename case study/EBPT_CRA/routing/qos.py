from routing.ebpt import compute_ebpt

def compute_qos_routes(nodes, bs):
    """
    Computes distinct routes for different QoS requirements.
    
    1. Real-Time Traffic -> Shortest Path (Low Delay)
    2. Normal Traffic   -> Energy Balanced Path (EBPT)
    
    Since the current simulation structure supports one 'parent' per node,
    this module calculates both but applies the "Real-Time" priority
    by default for demonstration, or could be toggled.
    
    Returns:
        dict: {node_id: {'rt_parent': node, 'normal_parent': node}}
    """
    routes = {}
    
    # 1. Normal Traffic (Energy Efficient)
    # We simulate this by running EBPT (which modifies node.parent, so we save it)
    compute_ebpt(nodes, bs)
    for n in nodes:
        routes[n.id] = {'normal_parent': n.parent}
        
    # 2. Real-Time Traffic (Low Delay => Shortest Distance to Next Hop towards BS)
    # To minimize delay, we want fewest hops? Or shortest physical distance?
    # Usually shortest path in hops or Euclidean distance.
    # Greedy Distance: Always pick neighbor closest to BS.
    
    for n in nodes:
        if not getattr(n, 'alive', True):
            continue
            
        # Candidates closer to BS
        candidates = [bs] + [m for m in nodes if m is not n and m.distance_to(bs) < n.distance_to(bs) and getattr(m, 'alive', True)]
        
        # Pick candidate that is Physically Closest to 'n' (Shortest Hop)
        # and also progresses to BS.
        if candidates:
            # Min distance to candidate (shortest hop)
            rt_parent = min(candidates, key=lambda c: n.distance_to(c))
            
            if n.id in routes:
                routes[n.id]['rt_parent'] = rt_parent
            else:
                 routes[n.id] = {'rt_parent': rt_parent}
                 
    return routes
