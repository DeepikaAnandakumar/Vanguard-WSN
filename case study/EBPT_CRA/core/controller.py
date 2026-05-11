from core import params
from clustering.ch_selection import select_cluster_heads
from clustering.cluster_formation import form_clusters
from routing.ebpt import compute_ebpt
from routing.traffic_aware import compute_traffic_aware_tree
from routing.qos import compute_qos_routes
from clustering.heed import select_cluster_heads_heed
from routing.pegasis import compute_pegasis_chain

try:
    from routing.forwarding import select_forwarders
except ImportError:
    from routing.forwarding import select_forwarding_nodes as select_forwarders
from routing.inter_cluster_routing import route_ch_to_bs

# Novel components for top-tier conference
try:
    from adaptive.parameter_tuning import AdaptiveParameterTuner, ApplicationAwareTuner
    from routing.traffic_aware_enhanced import compute_traffic_aware_ebpt, TrafficModel
    ADAPTIVE_AVAILABLE = True
except ImportError:
    ADAPTIVE_AVAILABLE = False
    AdaptiveParameterTuner = None
    ApplicationAwareTuner = None

class Controller:
    """
    Enhanced SDN Controller for EBPT-CRA with Adaptive Multi-Objective Optimization.
    
    Novel Features:
    - Adaptive parameter tuning based on network state
    - Traffic-aware routing with congestion avoidance
    - Application-aware optimization profiles
    """
    def __init__(self, network, routing_strategy="EBPT", ch_strategy="deterministic", 
                 gamma=0.0, adaptive=False, application_type="balanced", 
                 traffic_aware=False, traffic_weight=0.3):
        self.network = network
        self.routing_strategy = routing_strategy
        self.ch_strategy = ch_strategy  # "deterministic", "random", "energy_aware", or "adaptive"
        self.gamma = gamma  # Fairness parameter for EBPT (0.0 = pure energy, >0 = fairness-aware)
        self.adaptive = adaptive  # Enable adaptive parameter tuning (NOVEL)
        self.application_type = application_type  # Application profile (NOVEL)
        self.traffic_aware = traffic_aware  # Enable traffic-aware routing (NOVEL)
        self.traffic_weight = traffic_weight  # Weight of traffic in routing (NOVEL)
        
        # Initialize adaptive tuner if enabled
        if adaptive and ADAPTIVE_AVAILABLE:
            if application_type in ['real_time_monitoring', 'long_term_coverage', 'event_detection']:
                self.tuner = ApplicationAwareTuner(application_type=application_type)
            else:
                self.tuner = AdaptiveParameterTuner()
        else:
            self.tuner = None
        
        # Initialize traffic model if traffic-aware routing enabled
        if traffic_aware and ADAPTIVE_AVAILABLE:
            self.traffic_model = TrafficModel()
        else:
            self.traffic_model = None
        
        self.current_round = 0
        
    def build_network(self):
        """
        Execute the centralized logic to build the network topology.
        
        Enhanced with:
        - Adaptive parameter tuning (NOVEL)
        - Traffic-aware routing (NOVEL)
        - Application-aware optimization (NOVEL)
        """
        nodes = self.network.nodes
        bs = self.network.bs
        
        # 1. Clear previous state
        self._clear_node_state(nodes)
        
        # 2. Adaptive parameter tuning (NOVEL)
        if self.adaptive and self.tuner is not None:
            # Get network state for adaptation
            network_state = self._get_network_state()
            # Adapt gamma based on current network state
            self.gamma = self.tuner.adapt_gamma(
                self.network, 
                self.current_round,
                application_type=self.application_type
            )
        
        # 3. Compute Routing (Control Plane)
        if self.traffic_aware and ADAPTIVE_AVAILABLE:
            # Enhanced traffic-aware routing (NOVEL)
            from routing.traffic_aware_enhanced import compute_traffic_aware_ebpt
            self.traffic_model = compute_traffic_aware_ebpt(
                nodes, bs, 
                gamma=self.gamma,
                traffic_model=self.traffic_model,
                traffic_weight=self.traffic_weight
            )
        elif self.routing_strategy == "EBPT" or self.routing_strategy == "EBPT_LOAD_BALANCED":
            # Use gamma parameter from controller (allows dynamic tuning)
            from routing.ebpt import compute_ebpt
            compute_ebpt(nodes, bs, gamma=self.gamma)
            
        elif self.routing_strategy == "TRAFFIC_AWARE":
            compute_traffic_aware_tree(nodes, bs)
        elif self.routing_strategy == "QOS":
            # QoS creates dict of routes, but for simulation we need to pick one parent
            # to fit into current Node structure. 
            # We'll default to 'rt_parent' (Low Delay) for QoS verification
            routes = compute_qos_routes(nodes, bs)
            for n in nodes:
                if n.id in routes:
                    n.parent = routes[n.id].get('rt_parent')
                    if n.parent and n.parent is not bs:
                        n.parent.children.append(n)
        elif self.routing_strategy == "PEGASIS":
            # PEGASIS Routing (Chain-based)
            # Sets 'parent' pointers directly to form chain
            # Also handles Leader election (CH) internally
            self.network.bs.current_round = self.current_round # Pass round info
            compute_pegasis_chain(nodes, bs)
            # PEGASIS handles CH selection implicitly (Leader is CH)
            # So we might want to skip standard CH selection or ensure it respects the leader
            # We'll set a flag or just let standard CH selection run if it doesn't overwrite
            # But wait, standard CH selection overwrites is_ch.
            # So we need to protect it.

        else:
            # Default fallback — pass explicit gamma to ensure consistent behavior
            compute_ebpt(nodes, bs, gamma=self.gamma)
            # PEGASIS Routing (Chain-based)
            # Sets 'parent' pointers directly to form chain
            # Also handles Leader election (CH) internally
            self.network.bs.current_round = self.current_round # Pass round info
            compute_pegasis_chain(nodes, bs)
            # PEGASIS handles CH selection implicitly (Leader is CH)
            # So we might want to skip standard CH selection or ensure it respects the leader
            # We'll set a flag or just let standard CH selection run if it doesn't overwrite
            # But wait, standard CH selection overwrites is_ch.
            # So we need to protect it.


        
        # 3. Select Cluster Heads
        if self.routing_strategy == "PEGASIS":
             # Already handled in compute_pegasis_chain (Leader is CH)
             pass
        elif self.ch_strategy == "HEED":
            self.network.cluster_heads = select_cluster_heads_heed(nodes)
        else:
            self.network.cluster_heads = select_cluster_heads(nodes, method=self.ch_strategy)
        
        # 4. Form Clusters
        self.network.clusters = form_clusters(self.network.cluster_heads, nodes)
        
        # 5. Select Forwarders
        self.network.forwarders = select_forwarders(nodes, bs)
        
        # 6. Compute Inter-cluster Routes
        self.network.paths = route_ch_to_bs(self.network.cluster_heads, self.network.forwarders, bs)

    def _clear_node_state(self, nodes):
        for n in nodes:
            n.is_ch = False
            try: n.is_CH = False 
            except: pass
            n.is_forwarder = False
            n._recv_bits = 0
            n._forward_queue = []
            # Don't reset load here - it should accumulate during tree construction
            # Load will be initialized in compute_ebpt if needed
    
    def _get_network_state(self):
        """Extract network state for adaptive tuning."""
        alive_nodes = [n for n in self.network.nodes if getattr(n, 'alive', True)]
        if not alive_nodes:
            return {}
        
        energies = [n.energy for n in alive_nodes]
        loads = [getattr(n, 'load', 0) for n in alive_nodes]
        
        import numpy as np
        return {
            'energy_mean': np.mean(energies) if energies else 0,
            'energy_variance': np.var(energies) if energies else 0,
            'load_mean': np.mean(loads) if loads else 0,
            'load_variance': np.var(loads) if loads else 0,
            'alive_count': len(alive_nodes),
            'total_nodes': len(self.network.nodes)
        }
    
    def update_round(self, round_num: int):
        """Update controller state for new round."""
        self.current_round = round_num
    
    def update_performance(self, fnd: float, fairness: float, alpha: float = 0.5):
        """Update adaptive tuner with observed performance."""
        if self.tuner is not None:
            self.tuner.update_performance(fnd, fairness, alpha)
