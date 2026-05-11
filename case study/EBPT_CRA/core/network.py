import random
from typing import TYPE_CHECKING, Any
from core.node import Node

import core.params as params

if TYPE_CHECKING:
    # Static type-checking imports to satisfy linters (no runtime effect)
    from routing.ebpt import compute_ebpt  # noqa: F401
    from routing.forwarding import select_forwarders, select_forwarding_nodes  # noqa: F401
    from energy.first_order_radio import ETX, ERX  # noqa: F401
from core.controller import Controller

class Network:
    def __init__(self, *args, **kwargs):
        """Flexible constructor to support both new and legacy APIs.

        Supported forms:
        - Network(n, field_x, field_y, bs_pos)
        - Network(n=<n>, field_x=<fx>, field_y=<fy>, bs_pos=(x,y))
        - Network(num_nodes, area_size)
        - Network(num_nodes=<n>, area_size=<size>)
        """
        self.nodes = []
        # import locally to avoid import-time/circular issues
        # Annotate metrics as Any so type checkers don't raise assignment incompatibility
        self.metrics: Any = None
        try:
            from clustering.metrics import Metrics
            self.metrics = Metrics()
        except Exception:
            # Fallback simple Metrics for environments where clustering package
            # isn't importable for some reason (keeps main script runnable).
            class Metrics:
                def __init__(self):
                    self.rounds = []
                    self.alive_nodes = []
                    self.total_energy = []
                    self.dead_nodes = []
                    self.num_chs = []

                    self.first_node_death = None
                    self.half_node_death = None
                    self.last_node_death = None

                def log(self, r, alive, energy, dead=0, num_chs=0):
                    self.rounds.append(r)
                    self.alive_nodes.append(alive)
                    self.total_energy.append(energy)
                    self.dead_nodes.append(dead)
                    self.num_chs.append(num_chs)

                    total = alive + dead
                    if dead > 0 and self.first_node_death is None:
                        self.first_node_death = r
                    if self.half_node_death is None and alive <= total/2:
                        self.half_node_death = r
                    if self.last_node_death is None and alive == 0:
                        self.last_node_death = r

            self.metrics = Metrics()

        # bookkeeping
        self._round = 0
        self.cluster_heads = []
        self.forwarders = []
        self.clusters = {}
        
        # SDN Controller
        self.controller = Controller(self)

        # Heterogeneity params
        self.heterogeneity_enabled = kwargs.get('heterogeneity_enabled', getattr(params, 'HETEROGENEITY_ENABLED', False))
        self.m_param = kwargs.get('m', getattr(params, 'HETEROGENEITY_M', 0.1))
        self.alpha_param = kwargs.get('alpha', getattr(params, 'HETEROGENEITY_ALPHA', 1.0))

        # New-style positional: Network(n, field_x, field_y, bs_pos)
        if len(args) == 4:
            n, field_x, field_y, bs_pos = args
            self.field_x = field_x
            self.field_y = field_y
            
            # Determine advanced nodes indices
            num_adv = int(n * self.m_param) if self.heterogeneity_enabled else 0
            adv_indices = set(random.sample(range(n), num_adv))
            
            for i in range(n):
                # Calculate energy
                eng = getattr(params, 'INITIAL_ENERGY', 0.5)
                if i in adv_indices:
                    eng = eng * (1 + self.alpha_param)
                
                self.nodes.append(
                    Node(i, random.uniform(0, field_x), random.uniform(0, field_y), energy=eng)
                )
            self.bs = Node("BS", bs_pos[0], bs_pos[1], energy=float("inf"))
            return

        # New-style keywords
        if all(k in kwargs for k in ("n", "field_x", "field_y", "bs_pos")):
            n = kwargs["n"]
            field_x = kwargs["field_x"]
            field_y = kwargs["field_y"]
            bs_pos = kwargs["bs_pos"]
            self.field_x = field_x
            self.field_y = field_y
            
            # Determine advanced nodes indices
            num_adv = int(n * self.m_param) if self.heterogeneity_enabled else 0
            adv_indices = set(random.sample(range(n), num_adv))

            for i in range(n):
                eng = getattr(params, 'INITIAL_ENERGY', 0.5)
                if i in adv_indices:
                    eng = eng * (1 + self.alpha_param)
                
                self.nodes.append(
                    Node(i, random.uniform(0, field_x), random.uniform(0, field_y), energy=eng)
                )
            self.bs = Node("BS", bs_pos[0], bs_pos[1], energy=float("inf"))
            return

        # Legacy positional: Network(num_nodes, area_size)
        if len(args) == 2:
            num_nodes, area_size = args
            self.area_size = area_size
            
            num_adv = int(num_nodes * self.m_param) if self.heterogeneity_enabled else 0
            adv_indices = set(random.sample(range(num_nodes), num_adv))
            
            for i in range(num_nodes):
                eng = getattr(params, 'INITIAL_ENERGY', 0.5)
                if i in adv_indices:
                    eng = eng * (1 + self.alpha_param)
                self.nodes.append(
                    Node(i, random.uniform(0, area_size), random.uniform(0, area_size), energy=eng)
                )
            self.bs = None
            return

        # Legacy keywords
        if "num_nodes" in kwargs and "area_size" in kwargs:
            num_nodes = kwargs["num_nodes"]
            area_size = kwargs["area_size"]
            self.area_size = area_size
            
            num_adv = int(num_nodes * self.m_param) if self.heterogeneity_enabled else 0
            adv_indices = set(random.sample(range(num_nodes), num_adv))
            
            for i in range(num_nodes):
                eng = getattr(params, 'INITIAL_ENERGY', 0.5)
                if i in adv_indices:
                    eng = eng * (1 + self.alpha_param)
                self.nodes.append(
                    Node(i, random.uniform(0, area_size), random.uniform(0, area_size), energy=eng)
                )
            self.bs = None
            return

        raise TypeError("Invalid arguments for Network constructor")

    def deploy_nodes(self, num_nodes=None, area_size=None):
        """(Legacy helper) Deploy nodes in a square area.
        
        If heterogeneity is enabled on the instance, applies it here too.
        """
        if num_nodes is None:
            num_nodes = len(self.nodes) if self.nodes else 0
        if area_size is None:
            area_size = getattr(self, "area_size", None) or getattr(self, "field_x", None) or 100
        self.nodes = []
        
        num_adv = int(num_nodes * self.m_param) if self.heterogeneity_enabled else 0
        adv_indices = set(random.sample(range(num_nodes), num_adv))

        for i in range(num_nodes):
            eng = getattr(params, 'INITIAL_ENERGY', 0.5)
            if i in adv_indices:
                eng = eng * (1 + self.alpha_param)
            self.nodes.append(Node(i, random.uniform(0, area_size), random.uniform(0, area_size), energy=eng))
        self.area_size = area_size

    def deploy_bs(self, x=None, y=None):
        """(Legacy helper) Deploy BS; if x/y omitted, place at center of area."""
        if x is None or y is None:
            area = getattr(self, "area_size", None) or getattr(self, "field_x", None) or 100
            x = area / 2
            y = area / 2
        self.bs = Node("BS", x, y, energy=float("inf"))

    def build(self):
        # Delegated to SDN Controller
        self.controller.build_network()

    def _is_alive(self, node):
        a = getattr(node, 'alive', None)
        if a is None:
            return getattr(node, 'energy', 0) > 0
        return a

    def run_round(self):
        """Execute a simulation round with explicit RX accounting, aggregation
        and forwarding.

        Steps:
        - reset per-node per-round bookkeeping
        - members -> CH: sender pays ETX, CH pays ERX
        - CH aggregates, pays E_DA * total_bits and sends aggregated bits upward
        - forwarders forward to BS (pay ETX per message), BS energy ignored
        """
        # local energy method imports with compatibility
        try:
            from energy.first_order_radio import tx_energy, rx_energy
        except Exception:
            from energy.first_order_radio import ETX as tx_energy, ERX as rx_energy

        # reset per-node bookkeeping
        for n in self.nodes:
            n._recv_bits = 0
            n._forward_queue = []

        # --- Intra-cluster member -> CH transmissions ---
        for ch in getattr(self, 'cluster_heads', []) or []:
            if not self._is_alive(ch):
                continue

            members = [m for m in self.clusters.get(ch.id, []) if m.id != ch.id]
            for m in members:
                if not self._is_alive(m) or not self._is_alive(ch):
                    continue
                # member transmits to CH
                d = m.distance_to(ch)
                m.consume_energy(tx_energy(params.DATA_BITS, d))
                # CH pays RX energy for reception
                ch.consume_energy(rx_energy(params.DATA_BITS))
                ch._recv_bits += params.DATA_BITS

            # CH aggregates and forwards
            total_bits = params.DATA_BITS + ch._recv_bits  # own data + received
            # aggregation cost (per-bit)
            ch.consume_energy(params.E_DA * total_bits)
            # QoS routing disables aggregation for real-time traffic (not aggregatable)
            if getattr(self.controller, 'routing_strategy', None) == 'QOS':
                aggregated_bits = total_bits  # no aggregation for real-time
            else:
                aggregated_bits = total_bits * params.AGGR_RATIO

            # send aggregated bits to parent (forwarder or bs)
            parent = getattr(ch, 'parent', None)
            if parent is not None and self._is_alive(ch):
                d = ch.distance_to(parent)
                ch.consume_energy(tx_energy(aggregated_bits, d))
                # Update load (CH determines to relay)
                ch.load += aggregated_bits
                
                # if parent is not BS, account RX at parent and queue forward
                if parent is not self.bs:
                    parent.consume_energy(rx_energy(aggregated_bits))
                    parent._forward_queue.append(aggregated_bits)
                else:
                    # parent is BS: per-spec BS energy ignored
                    pass

        # --- Forwarders forward their queued messages to BS ---
        for f in getattr(self, 'forwarders', []) or []:
            if not self._is_alive(f):
                continue
            for bits in list(f._forward_queue):
                # forward to BS (BS energy ignored)
                d = f.distance_to(self.bs)
                f.consume_energy(tx_energy(bits, d))
                # Update load
                f.load += bits

        # --- Any non-CH nodes that still have parent and weren't in clusters ---
        # (fallback to support older code behavior)
        for node in self.nodes:
            if node.is_ch:
                continue
            # If node still has a parent and wasn't already accounted for (not in cluster)
            if getattr(node, 'parent', None) and node._recv_bits == 0:
                parent = node.parent
                if self._is_alive(node) and self._is_alive(parent):
                    d = node.distance_to(parent)
                    node.consume_energy(tx_energy(params.DATA_BITS, d))
                    if parent is not self.bs:
                        try:
                            parent.consume_energy(rx_energy(params.DATA_BITS))
                        except Exception:
                            pass
                    else:
                        pass

        # increment round counter
        self._round += 1


    def alive_nodes(self):
        return sum(1 for n in self.nodes if self._is_alive(n))

    def reconfiguration_needed(self):
        for group in (getattr(self, 'cluster_heads', []) or [], getattr(self, 'forwarders', []) or []):
            for n in group:
                initial = getattr(n, 'initial_energy', getattr(n, 'energy', 1.0))
                if getattr(n, 'energy', 0) <= 0.5 * initial:
                    return True
        return False

    def log_metrics(self, r):
        total_energy = sum(n.energy for n in self.nodes if self._is_alive(n))
        alive = self.alive_nodes()
        dead = len(self.nodes) - alive
        # count only alive CHs
        num_chs = sum(1 for ch in getattr(self, 'cluster_heads', []) if self._is_alive(ch))
        
        # Calculate Jain's Fairness Index for Load
        # J = (sum(xi))^2 / (n * sum(xi^2))
        loads = [n.load for n in self.nodes if self._is_alive(n)]
        jain = 1.0
        if loads and sum(loads) > 0:
            numerator = sum(loads) ** 2
            denominator = len(loads) * sum(x**2 for x in loads)
            if denominator > 0:
                jain = numerator / denominator

        # Calculate Average Hop Count
        # Since we have a tree structure (parent pointers), we can trace up to BS
        total_hops = 0
        nodes_with_path = 0
        for n in self.nodes:
            if not self._is_alive(n):
                continue
            
            # Simple path trace
            hops = 0
            curr = n
            # limit hops to prevent infinite loop in case of cycles (though unlikely in tree)
            max_hops = len(self.nodes) 
            path_exists = False
            
            # If node is BS (not in self.nodes ideally, but just in case) or close
            if n == self.bs:
                 path_exists = True
            elif getattr(n, 'parent', None):
                curr = n
                while getattr(curr, 'parent', None) and hops < max_hops:
                    hops += 1
                    curr = curr.parent
                    if curr == self.bs:
                        path_exists = True
                        break
            
            if path_exists:
                total_hops += hops
                nodes_with_path += 1

        avg_hops = 0.0
        if nodes_with_path > 0:
            avg_hops = total_hops / nodes_with_path
                
        # Calculate Throughput: Total packets sent to BS this round
        # For simplicity, we can use the sum of 'load' across all nodes if load is reset per round.
        # Alternatively, we calculate it as data packets successfully reaching Sink.
        throughput = sum(loads) * params.DATA_BITS
        
        # Get all node energies for spatial plots
        node_energies = [n.energy for n in self.nodes]
        
        # Log node positions once if not already logged
        if hasattr(self.metrics, 'node_positions') and not self.metrics.node_positions:
            self.metrics.node_positions = [[n.x, n.y] for n in self.nodes]

        # call metrics logger (supports extended signature)
        try:
            self.metrics.log(r, alive, total_energy, dead=dead, num_chs=num_chs, jain=jain, 
                            avg_hops=avg_hops, throughput=throughput, node_energies=node_energies)
        except TypeError:
            # backward-compatible call
            self.metrics.log(r, alive, total_energy)
