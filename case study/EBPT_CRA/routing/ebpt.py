def compute_ebpt(nodes, bs, gamma=0.1):
    """
    Build a simple EBPT (Energy-Balanced Path Tree).
    
    Args:
        nodes: List of sensor nodes
        bs: Base station node
        gamma: Load balancing factor (0.0 = Pure Energy/Distance, >0 = Fairness Aware)

    Algorithm (greedy by distance-to-BS):
    - Sort nodes by distance to BS (closest first).
    - For each node in increasing distance order, choose as parent the
      closest candidate among BS and previously-processed nodes (which are
      guaranteed to be closer to BS), producing a directed tree toward BS.
    - Populate each node.children list for subtree traversal.

    This produces an acyclic tree rooted at BS and is compatible with
    the newer `form_clusters(cluster_heads)` API which traverses
    `node.children` to collect cluster members.
    """
    # clear existing parent/children relationships
    for n in nodes:
        n.parent = None
        n.children = []

    # sort nodes by distance to BS (increasing) - still needed for acyclic dependency
    # Precompute distances to avoid repeated sqrt computations during candidate selection
    nodes_with_dist = [(n, n.distance_to(bs)) for n in nodes]
    nodes_with_dist.sort(key=lambda x: x[1])
    nodes_sorted = [nd[0] for nd in nodes_with_dist]
    
    # Import weight function
    from routing.ebpt_weight import ebpt_edge_weight

    # Initialize load for all nodes (for fairness calculation)
    # Load represents number of children (traffic load)
    for n in nodes:
        if not hasattr(n, 'load') or n.load is None:
            n.load = 0
        else:
            # Reset load at start of tree construction (fresh tree)
            n.load = 0
    
    # Iterate in increasing distance order; keep processed nodes in a list
    processed = []
    for n in nodes_sorted:
        if not getattr(n, 'alive', True):
            continue
        # candidate parents: BS plus nodes already processed (they are closer to BS by construction)
        candidates = [bs] + [m for m in processed if getattr(m, 'alive', True)]
        
        # Select best parent based on WEIGHT (Maximize Score)
        # ebpt_edge_weight returns a score where Higher is Better
        # Load is considered in the weight function (higher load = lower score when gamma > 0)
        # At this point, candidates' load reflects children already assigned from previously processed nodes
        parent = max(candidates, key=lambda candidate: ebpt_edge_weight(n, candidate, gamma=gamma))
        n.parent = parent
        if parent is not bs:
            parent.children.append(n)
            # Update load: parent receives traffic from this child
            # This load will be considered when selecting parents for future nodes
            parent.load = len(parent.children)  # Load = number of children (simplified model)
        # Mark this node as processed so it can be a candidate for later nodes
        processed.append(n)


# backward-compatible alias for older callers
compute_ebpt.__name__ = 'compute_ebpt'
build_ebpt = compute_ebpt
