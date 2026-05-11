
import os
import sys
import json
import csv
import argparse
import random
from statistics import mean, stdev

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.network import Network
import core.params as params

# Configurations for the paper
SCENARIOS = {
    "Vanguard": {
        "routing": "EBPT",
        "ch_strategy": "energy_aware",
        "gamma": 0.5,
        "description": "Proposed Method (Traffic-Aware + Energy-Balanced)"
    },
    "LEACH-MultiHop": {
        "routing": "EBPT", # Using EBPT with gamma=0 behaves as greedy distance routing
        "ch_strategy": "random",
        "gamma": 0.0,
        "description": "Baseline Clustering (Random CH + Greedy Routing)"
    },
    "HEED-MultiHop": {
        "routing": "EBPT",
        "ch_strategy": "HEED",
        "gamma": 0.0,
        "description": "HEED Clustering + Greedy Routing"
    },
    "PEGASIS": {
        "routing": "PEGASIS",
        "ch_strategy": "random", # PEGASIS handles chain internally
        "gamma": 0.0,
        "description": "Chain-based Routing"
    }
}

def run_simulation(scenario_name, config, seed):
    print(f"Running {scenario_name} - Seed {seed}...")
    
    scen = SCENARIOS[scenario_name]
    
    random.seed(seed)
    
    # Override params
    params.INITIAL_ENERGY = config['initial_energy']
    params.DATA_BITS = config['data_bits']
    
    net = Network(n=config['nodes'], field_x=100, field_y=100, bs_pos=(50, 50))
    for n in net.nodes:
        n.initial_energy = config['initial_energy']
        n.energy = config['initial_energy']
        
    net.controller.routing_strategy = scen['routing']
    net.controller.ch_strategy = scen['ch_strategy']
    net.controller.gamma = scen['gamma']
    
    net.build()
    
    metrics = {
        "rounds": [],
        "alive": [],
        "energy": [],
        "throughput": [] # Packets sent
    }
    
    start_nodes = config['nodes']
    
    for r in range(config['rounds']):
        if r % 50 == 0: # Periodic rebuild
            net.controller.build_network()
            
        net.run_round()
        
        metrics["rounds"].append(r)
        metrics["alive"].append(net.alive_nodes())
        metrics["energy"].append(sum(n.energy for n in net.nodes if net._is_alive(n)))
        # Throughput approximation: alive nodes * data_bits (assuming perfect delivery for now or using net stats if available)
        # net doesn't track total packets globally easily, but params.DATA_BITS is sent by each alive node per round
        metrics["throughput"].append(net.alive_nodes() * params.DATA_BITS)
        
        if net.alive_nodes() == 0:
            break
            
    return metrics

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seeds', type=int, default=10) # 10 seeds for average
    parser.add_argument('--nodes', type=int, default=100)
    parser.add_argument('--rounds', type=int, default=2000)
    parser.add_argument('--out', type=str, default='paper_results')
    args = parser.parse_args()
    
    config = {
        'initial_energy': 0.5,
        'data_bits': 2000,
        'nodes': args.nodes,
        'rounds': args.rounds
    }
    
    os.makedirs(args.out, exist_ok=True)
    
    all_results = {}
    
    for name in SCENARIOS:
        metrics_list = []
        for s in range(args.seeds):
            m = run_simulation(name, config, s)
            metrics_list.append(m)
            
        all_results[name] = metrics_list
        
        # Save raw data
        with open(os.path.join(args.out, f"{name}.json"), "w") as f:
            json.dump(metrics_list, f)
            
    print("Simulations Complete.")

if __name__ == "__main__":
    main()
