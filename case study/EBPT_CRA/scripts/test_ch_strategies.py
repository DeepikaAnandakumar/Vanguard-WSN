"""Compare deterministic vs energy-aware CH selection for EBPT."""
import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.network import Network
import core.params as params
import random

def run_comparison():
    config = {
        'nodes': 50,
        'rounds': 500,
        'seeds': 3,
        'data_bits': 4000,
        'initial_energy': 0.5
    }
    
    results = {'deterministic': [], 'energy_aware': []}
    
    for ch_strategy in ['deterministic', 'energy_aware']:
        print(f"\n=== Testing {ch_strategy} CH selection ===")
        
        for seed in range(config['seeds']):
            random.seed(seed)
            params.DATA_BITS = config['data_bits']
            params.INITIAL_ENERGY = config['initial_energy']
            
            net = Network(n=config['nodes'], field_x=100, field_y=100, bs_pos=(50, 50))
            for n in net.nodes:
                n.initial_energy = config['initial_energy']
                n.energy = config['initial_energy']
            
            net.controller.routing_strategy = "EBPT"
            net.controller.ch_strategy = ch_strategy
            net.build()
            
            metrics = {
                'rounds': [],
                'alive': [],
                'energy': [],
                'num_chs': []
            }
            
            for r in range(config['rounds']):
                net.controller.build_network()
                net.run_round()
                net.log_metrics(r)
                
                metrics['rounds'].append(r)
                metrics['alive'].append(net.alive_nodes())
                metrics['energy'].append(sum(n.energy for n in net.nodes if net._is_alive(n)))
                metrics['num_chs'].append(len(net.cluster_heads))
                
                if net.alive_nodes() == 0:
                    break
            
            fnd = next((r for r, a in zip(metrics['rounds'], metrics['alive']) if a < config['nodes']), metrics['rounds'][-1])
            lnd = metrics['rounds'][-1] if metrics['alive'][-1] == 0 else "Survived"
            
            result = {
                'seed': seed,
                'fnd': fnd,
                'lnd': lnd,
                'metrics': metrics
            }
            results[ch_strategy].append(result)
            print(f"  Seed {seed}: FND={fnd}, LND={lnd}, Final_Alive={metrics['alive'][-1]}")
    
    # Summary
    print("\n=== SUMMARY ===")
    for strategy in ['deterministic', 'energy_aware']:
        fnds = [r['fnd'] for r in results[strategy]]
        print(f"{strategy.upper()}: FND mean = {sum(fnds)/len(fnds):.1f}, std = {(sum((x - sum(fnds)/len(fnds))**2 for x in fnds) / len(fnds))**0.5:.1f}")
    
    # Save results
    os.makedirs('ch_strategy_comparison', exist_ok=True)
    with open('ch_strategy_comparison/results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to ch_strategy_comparison/results.json")

if __name__ == '__main__':
    run_comparison()
