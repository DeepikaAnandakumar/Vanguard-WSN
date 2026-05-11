
def form_clusters(cluster_heads, nodes):
    """
    Form clusters of nodes around each cluster head.
    
    Args:
        cluster_heads: List of selected cluster heads
        nodes: All sensor nodes
    
    Returns:
        Dictionary {ch_id: [list of member nodes (including CH itself)]}
    """
    clusters = {ch.id: [] for ch in cluster_heads}
    
    # Simple Voronoi-like clustering: join nearest CH
    for node in nodes:
        if not getattr(node, 'alive', True):
            continue
            
        # Find nearest CH
        best_ch = None
        min_dist = float('inf')
        
        for ch in cluster_heads:
            d = node.distance_to(ch)
            if d < min_dist:
                min_dist = d
                best_ch = ch
        
        if best_ch:
            clusters[best_ch.id].append(node)
            
    return clusters
