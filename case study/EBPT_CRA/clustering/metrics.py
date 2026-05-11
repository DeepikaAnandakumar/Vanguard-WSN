class Metrics:
    def __init__(self):
        self.rounds = []
        self.alive_nodes = []
        self.total_energy = []
        self.dead_nodes = []
        self.num_chs = []
        self.jains_index = [] # Fairness index

        self.average_hop_count = []
        
        self.first_node_death = None
        self.half_node_death = None
        self.last_node_death = None
        self.throughput = []
        self.per_node_energy = {} # round -> list of energies
        self.node_positions = []

    def log(self, r, alive, energy, dead=0, num_chs=0, jain=1.0, avg_hops=0.0, throughput=0.0, node_energies=None):
        self.rounds.append(r)
        self.alive_nodes.append(alive)
        self.total_energy.append(energy)
        self.dead_nodes.append(dead)
        self.num_chs.append(num_chs)
        self.jains_index.append(jain)
        self.average_hop_count.append(avg_hops)
        self.throughput.append(throughput)
        
        # Log per-node energy periodically or at key rounds to save space
        if r % 100 == 0 or alive == 0:
            if node_energies is not None:
                self.per_node_energy[str(r)] = list(node_energies)

        total = alive + dead
        if total == 0: total = 1 # avoid div zero
        
        if dead > 0 and self.first_node_death is None:
            self.first_node_death = r
        if self.half_node_death is None and alive <= total/2:
            self.half_node_death = r
        if self.last_node_death is None and alive == 0:
            self.last_node_death = r
