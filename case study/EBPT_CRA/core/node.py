from core.params import INITIAL_ENERGY

class Node:
    def __init__(self, node_id, x, y, energy=None):
        self.id = node_id
        self.x = x
        self.y = y

        # If energy is None, use current parameter value to allow runtime overrides
        if energy is None:
            from core import params as _p
            energy = getattr(_p, 'INITIAL_ENERGY', INITIAL_ENERGY)

        self.energy = energy
        self.initial_energy = energy
        # keep compatibility with variants that use `alive` or energy check
        self.alive = True

        # Routing / clustering roles
        self.parent = None
        self.children = []
        self.is_ch = False
        self.is_forwarder = False
        # compatibility alias (some modules refer to is_CH)
        self.is_CH = False

        # bookkeeping for a round
        self._recv_bits = 0  # total bits received this round
        self._forward_queue = []  # list of bit-sizes to forward to BS
        
        # Load balancing
        self.load = 0 # Cumulative bits forwarded (or load index)

    def distance_to(self, other):
        return ((self.x - other.x)**2 + (self.y - other.y)**2) ** 0.5

    def consume_energy(self, amount):
        self.energy -= amount
        if self.energy <= 0:
            self.alive = False

