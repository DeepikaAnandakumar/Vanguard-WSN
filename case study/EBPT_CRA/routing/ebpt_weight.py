from energy.first_order_radio import ETX, ERX

DATA_BITS = 2500


def ebpt_edge_weight(node_i, node_j, gamma=0.1):
    """
    EBPT edge weight with Load Balancing penalty:
    Score = (Energy/Cost) / (1 + gamma * Load)
    
    We want to MAXIMIZE this score (Higher Energy & Lower Load is better).
    """
    if node_i.energy <= 0 or node_j.energy <= 0:
        return -1 # Invalid

    d = node_i.distance_to(node_j)
    
    # Base "Goodness" based on energy (how many packets they can support)
    energy_score = (node_i.energy / ETX(DATA_BITS, d)) + \
                   (node_j.energy / ERX(DATA_BITS))
                   
    # Load Penalty (Fairness)
    # node_j is the parent/receiver, so check its load
    load_j = getattr(node_j, 'load', 0)
    
    # Final Score: Energy Score / Load Factor
    # As load increases, score decreases
    final_score = energy_score / (1.0 + gamma * load_j)

    return final_score
