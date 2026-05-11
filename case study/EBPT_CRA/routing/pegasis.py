
import numpy as np

def compute_pegasis_chain(nodes, bs):
    """
    Builds a PEGASIS chain (Power-Efficient Gathering in Sensor Information Systems).
    
    Algorithm:
    1. Start with the node furthest from the BS.
    2. Greedily select the closest unvisited neighbor as the next node in the chain.
    3. The chain ends? No, the chain is a path covering all nodes.
    4. Leader Election: In each round, a random node (or rotating) is the Leader.
       - The Leader collects data from the chain and sends to BS.
       - For simulation, we need to set `node.parent` pointers to form the flow towards the Leader.
    
    Implementation Detail:
    - Since Leader rotates every round, this function might need to be called every round 
      OR we compute the chain once (neighbors don't change) and just change flow direction.
    - However, `compute_ebpt` is called every round in the loop. So we can re-compute or just re-orient.
    - Re-orienting is easier.
    
    Args:
        nodes: List of nodes.
        bs: Base Station.
    """
    
    alive_nodes = [n for n in nodes if getattr(n, 'alive', True)]
    if not alive_nodes:
        return

    # Clear existing parents
    for n in nodes:
        n.parent = None
        n.children = []

    # 1. Build Chain (Greedy TSP-like)
    # Start with furthest from BS
    curr = max(alive_nodes, key=lambda n: np.sqrt((n.x - bs.x)**2 + (n.y - bs.y)**2))
    chain = [curr]
    unvisited = set(alive_nodes)
    unvisited.remove(curr)
    
    while unvisited:
        # Find closest neighbor to current tip 'curr'
        if not unvisited:
            break
            
        closest = min(unvisited, key=lambda n: np.sqrt((n.x - curr.x)**2 + (n.y - curr.y)**2))
        chain.append(closest)
        unvisited.remove(closest)
        curr = closest
        
    # 'chain' is a list of nodes ordered [Start -> ... -> End]
    # But data flow depends on Leader position.
    
    # 2. Select Leader
    # Simple strategy: Random leader or Modulo round number
    # For fairness, standard PEGASIS rotates i mod N.
    # We need 'current_round' to be passed? 
    # Or we just pick a random one here if round not available.
    # Ideally should be passed. Let's assume passed or attribute.
    
    # Check if controller attached to network has current_round
    # This is a hacky way to access state, but workable.
    import random
    leader_idx = random.randint(0, len(chain)-1) # Default random if no round info
    
    try:
        # Try to find a way to get round number... 
        # Maybe use a static counter or heuristic
        leader_idx = int(getattr(bs, 'current_round', 0)) % len(chain)
    except:
        pass
        
    leader = chain[leader_idx]
    leader.is_ch = True # Mark as CH
    
    # 3. Orient Parent pointers towards Leader
    # Chain: [0] -- [1] -- ... -- [Leader] -- ... -- [N]
    # Left side: [0] -> [1] -> ... -> [Leader]
    # Right side: [N] -> [N-1] -> ... -> [Leader]
    
    # Set parents for left side
    for i in range(leader_idx):
        child = chain[i]
        parent = chain[i+1]
        child.parent = parent
        parent.children.append(child)
        
    # Set parents for right side
    for i in range(len(chain)-1, leader_idx, -1):
        child = chain[i]
        parent = chain[i-1]
        child.parent = parent
        parent.children.append(child)
        
    # Leader's parent is BS
    leader.parent = bs
    
