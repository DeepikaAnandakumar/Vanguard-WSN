
import numpy as np
from scipy.optimize import linprog
import networkx as nx

class NUMSolver:
    """
    Solves the Network Utility Maximization (NUM) problem for WSN lifetime.
    
    This class provides the 'God View' or Theoretical Upper Bound for network lifetime
    by formulating the routing problem as a Linear Program (LP).
    
    Objective:
        Maximize T (Network Lifetime)
        
    Subject to:
        1. Flow Conservation: Incoming + Generated = Outgoing
        2. Energy Constraint: Total energy consumed by node i <= Initial Energy i
        3. Link Capacity (Optional): Bandwidth limits
    
    This provides a strict upper bound against which heuristics (EBPT, HEED) 
    can be compared.
    """
    
    def __init__(self, nodes, base_station, energy_model_params):
        """
        Args:
            nodes: List of Node objects (with .id, .x, .y, .initial_energy)
            base_station: Node object representing BS
            energy_model_params: Dict with 'E_elec', 'E_fs', 'E_mp', etc.
        """
        self.nodes = nodes
        self.bs = base_station
        self.params = energy_model_params
        self.num_nodes = len(nodes)
        
    def _calculate_cost(self, u, v_pos):
        """Calculate transmission cost from node u to position v_pos."""
        d = np.sqrt((u.x - v_pos[0])**2 + (u.y - v_pos[1])**2)
        # First order radio model
        # ETX = E_elec * k + E_amp * k * d^2 (or d^4)
        # We assume k=1 bit for cost calculation, scaled later
        E_elec = self.params.get('E_elec', 50e-9)
        d0 = self.params.get('d0', 87.0)
        
        if d < d0:
            E_amp = self.params.get('E_fs', 10e-12)
            cost = E_elec + E_amp * (d**2)
        else:
            E_amp = self.params.get('E_mp', 0.0013e-12)
            cost = E_elec + E_amp * (d**4)
            
        return cost

    def solve_max_lifetime_lp(self, packet_size_bits=2000):
        """
        Solves the Max Lifetime LP.
        
        Variables:
            f_ij: Flow from node i to node j (per round)
            T: Total lifetime (rounds)
            
        However, to make it a standard LP, we typically fix T and check feasibility,
        or formulate as:
        Max T
        s.t.
        sum(f_ij) - sum(f_ki) = g_i * T  (for all i != BS)
        sum(E_tx(i,j)*f_ij + E_rx*f_ki) <= E_init_i
        
        This is a non-linear problem because of T in constraints.
        Standard transformation: Set variable x_ij = total flow on link i->j over WHOLE lifetime.
        Then we solve:
        Maximize T
        s.t.
        sum(x_ij) - sum(x_ki) = g_i * T  (Rate * Lifetime = Total Data)
        sum(cost_ij * x_ij + cost_rx * x_in) <= E_init_i
        x_ij >= 0, T >= 0
        """
        
        # Nodes map to indices 0..N-1
        # Links: All pairs (i,j) and (i, BS). 
        # To reduce complexity, we only consider neighbors within range R or k-NN.
        # For 'God View', we can assume full mesh but prune high cost links.
        
        N = self.num_nodes
        # Create all possible links (i, j) where i is a sensor, j is sensor or BS
        links = []
        for i in range(N):
            # To other sensors
            for j in range(N):
                if i != j:
                    links.append((i, j))
            # To BS (represented as index N)
            links.append((i, N))
            
        L = len(links)
        # Variables: [x_0...x_L-1, T] -> Size L + 1
        # x_k is flow on link k
        
        # Objective: Maximize T
        # c = [0, 0, ..., -1] (scipy minimizes, so minimize -T)
        c = np.zeros(L + 1)
        c[-1] = -1.0
        
        # Constraints
        A_eq = []
        b_eq = []
        A_ub = []
        b_ub = []
        
        E_elec = self.params.get('E_elec', 50e-9)
        E_rx_cost = E_elec * packet_size_bits # Reception cost per bit * bits
        
        # 1. Flow Conservation per Node i
        # sum(outgoing x_ij) - sum(incoming x_ki) - 1 * T = 0
        # (Assuming generation rate 1 packet/round)
        
        for i in range(N):
            row = np.zeros(L + 1)
            # Outgoing links from i
            for idx, (u, v) in enumerate(links):
                if u == i:
                    row[idx] = 1
            # Incoming links to i
            for idx, (u, v) in enumerate(links):
                if v == i:
                    row[idx] = -1
            
            # Generation rate term (-1 * T)
            # We assume each node generates 1 packet per round
            row[L] = -1 * packet_size_bits 
            
            A_eq.append(row)
            b_eq.append(0)
            
        # 2. Energy Constraints per Node i
        # sum(Tx_cost * x_ij) + sum(Rx_cost * x_ki) <= E_init_i
        
        for i in range(N):
            row = np.zeros(L + 1)
            
            # Tx costs
            for idx, (u, v) in enumerate(links):
                if u == i:
                    # Calculate cost per bit * packet size
                    # Note: x_ij is in BITS if we use bits for generation
                    # Let's assume x_ij is in PACKETS for numerical stability?
                    # No, let's stick to cost calculation.
                    # x_ij represents total bits? 
                    # Let's assume x_ij is TOTAL BITS.
                    
                    # Cost to send 1 bit
                    if v == N: # BS
                        dist = np.sqrt((self.nodes[u].x - self.bs.x)**2 + (self.nodes[u].y - self.bs.y)**2)
                    else:
                        dist = np.sqrt((self.nodes[u].x - self.nodes[v].x)**2 + (self.nodes[u].y - self.nodes[v].y)**2)
                    
                    # Calculate bit cost
                    d0 = self.params.get('d0', 87.0)
                    if dist < d0:
                        e_bit = self.params.get('E_elec', 50e-9) + self.params.get('E_fs', 10e-12) * (dist**2)
                    else:
                        e_bit = self.params.get('E_elec', 50e-9) + self.params.get('E_mp', 0.0013e-12) * (dist**4)
                    
                    row[idx] = e_bit
            
            # Rx costs
            for idx, (u, v) in enumerate(links):
                if v == i:
                    row[idx] = self.params.get('E_elec', 50e-9)
            
            # T is not in energy constraint directly
            row[L] = 0
            
            A_ub.append(row)
            b_ub.append(self.nodes[i].initial_energy)

        # Bounds: x_ij >= 0, T >= 0
        bounds = [(0, None) for _ in range(L + 1)]
        
        # Solve
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
        
        if res.success:
            # Result T is in the last variable (and it's negative in objective)
            max_lifetime = res.x[-1]
            # Convert bits lifetime to rounds (since 1 round = 1 packet per node)
            # T is already in Rounds because of the constraint: Flow = T * packet_size
            rounds = max_lifetime
            return rounds, res.x
        else:
            return 0, None

def get_lp_bound(nodes, bs, params):
    solver = NUMSolver(nodes, bs, params)
    rounds, _ = solver.solve_max_lifetime_lp()
    return rounds
