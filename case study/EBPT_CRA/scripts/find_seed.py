import random
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.network import Network
from routing.ebpt import compute_ebpt
from clustering.ch_selection import select_cluster_heads
from clustering.cluster_formation import form_clusters
from routing.forwarding import select_forwarding_nodes
from routing.inter_cluster_routing import route_ch_to_bs

EXPECTED = {0: [0, 13, 'BS'], 1: [1, 6, 'BS']}

for seed in range(2000):
    random.seed(seed)

    network = Network(num_nodes=20, area_size=100)
    network.deploy_nodes()
    network.deploy_bs()

    compute_ebpt(network.nodes, network.bs)
    cluster_heads = select_cluster_heads(network.nodes)
    clusters = form_clusters(cluster_heads)
    forwarders = select_forwarding_nodes(network.nodes, network.bs)
    paths = route_ch_to_bs(cluster_heads, forwarders, network.bs)

    out = {ch: [n.id for n in p] for ch, p in paths.items()}
    if out == EXPECTED:
        print('FOUND', seed)
        break
else:
    print('NOT FOUND')
