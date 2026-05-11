import os
import sys
import json
import argparse
import csv
import numpy as np
from typing import List, Dict, Any, Union, cast
from statistics import mean, stdev

# Add project root to path for standalone execution
if "__file__" in globals():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if project_root not in sys.path:
        sys.path.append(project_root)

from core.network import Network
from core.controller import Controller
from theory.num_framework import get_lp_bound

def run_single_simulation(algorithm_config, seed, network_config):
    """Run single simulation."""
    np.random.seed(seed)
    
    # Create network
    net = Network(
        n=network_config['nodes'],
        field_x=network_config['field_size'],
        field_y=network_config['field_size'],
        bs_pos=(network_config['field_size']/2, network_config['field_size']/2)
    )
    
    # Create controller
    controller = Controller(
        network=net,
        routing_strategy=algorithm_config.get('routing', 'EBPT'),
        ch_strategy=algorithm_config.get('ch_strategy', 'energy_aware'),
        gamma=algorithm_config.get('gamma', 0.0),
        adaptive=algorithm_config.get('adaptive', False)
    )
    
    net.controller = controller
    net.build()
    
    # Run simulation
    metrics = {'rounds': [], 'alive': []}
    
    for r in range(network_config['rounds']):
        controller.update_round(r)
        controller.build_network()
        net.run_round()
        
        metrics['rounds'].append(r)
        metrics['alive'].append(net.alive_nodes())
        
        if net.alive_nodes() == 0:
            break
            
    # Calculate FND, etc.
    fnd_idx = next((r for r, a in zip(metrics['rounds'], metrics['alive']) 
                if a < network_config['nodes']), network_config['rounds'])
    
    simulation_result: Any = {
        'seed': seed,
        'algorithm': algorithm_config['name'],
        'fnd': int(fnd_idx),
        'metrics': metrics
    }
    return simulation_result

def run_num_experiments(output_dir='num_results', seeds=5, sizes=[50]):
    """Run experiments comparing EBPT against HEED, PEGASIS, and LP Bound."""
    os.makedirs(output_dir, exist_ok=True)
    
    network_config = {'nodes': 50, 'rounds': 5000, 'field_size': 100}
    
    # Algorithms to test
    algorithms = [
        # 1. The Classic Baselines
        {'name': 'HEED_Clustered', 'routing': 'EBPT', 'ch_strategy': 'HEED'}, # HEED Clustering + Default Routing
        {'name': 'PEGASIS', 'routing': 'PEGASIS', 'ch_strategy': 'deterministic'}, # PEGASIS Routing + Leader
        
        # 2. Our Proposed Method (EBPT-NUM)
        {'name': 'EBPT_Flat_Gamma_0.5', 'routing': 'EBPT', 'ch_strategy': None, 'gamma': 0.5}, # NOVEL: Pure Tree, No Clustering overhead
        {'name': 'EBPT_Clustered_Gamma_0.5', 'routing': 'EBPT', 'ch_strategy': 'energy_aware', 'gamma': 0.5},
        
        # 3. Reference (LEACH-like)
        {'name': 'LEACH_EnergyAware', 'routing': 'EBPT', 'ch_strategy': 'energy_aware', 'gamma': 0.0}
    ]
    
    all_results: Any = {}
    
    for size in sizes:
        print(f"\n--- Running for {size} Nodes ---")
        network_config['nodes'] = size
        
        # 1. Calculate Theoretical Upper Bound (The "God Line")
        # Instantiate a dummy network just to get positions for LP?
        # No, for meaningful LP bound, we should average LP bound over multiple topologies,
        # OR compute LP bound for the SPECIFIC topology of each seed.
        # Computing LP for every seed is expensive but accurate.
        # Let's do it for the FIRST seed or average of first 5.
        
        lp_fnd_values = []
        print("Calculating LP Upper Bound (God Line)...")
        for seed in range(min(seeds, 5)): # Limit LP calc to 5 seeds to save time
             np.random.seed(seed)
             net = Network(n=size, field_x=100, field_y=100, bs_pos=(50,50))
             params = {'E_elec': 50e-9, 'E_fs': 10e-12, 'E_mp': 0.0013e-12, 'd0': 87.0}
             try:
                 bound = get_lp_bound(net.nodes, net.bs, params)
                 if bound > 0:
                     lp_fnd_values.append(bound)
             except Exception as e:
                 print(f"LP Solver failed for seed {seed}: {e}")
                 
        avg_lp_bound = mean(lp_fnd_values) if lp_fnd_values else 0
        print(f"  Avg LP Bound: {avg_lp_bound:.1f} rounds")
        
        size_results = cast(Any, {})
        size_results['lp_bound_mean'] = float(avg_lp_bound)
        size_results['lp_bound_std'] = float(stdev(lp_fnd_values)) if len(lp_fnd_values)>1 else 0.0
        
        # 2. Run Simulations
        raw_data: Any = {}
        
        # Prepare CSV file
        csv_file = f'{output_dir}/raw_results_{size}.csv'
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Seed', 'Algorithm', 'FND', 'LP_Bound', 'Optimality_Gap'])
            
        for algo in algorithms:
            print(f"  Simulating {algo['name']}...")
            algo_results = []
            for seed in range(seeds):
                try:
                    res = run_single_simulation(algo, seed, network_config)
                    # Print progress for long runs
                    if network_config['rounds'] > 2000 and seed == 0:
                         print(f"    Seed {seed} finished with FND: {res['fnd']}")
                    
                    sim_fnd = int(res['fnd']) # type: ignore
                    algo_results.append(sim_fnd)
                    
                    # Incremental Save
                    with open(csv_file, 'a', newline='') as f:
                        w = csv.writer(f)
                        num_avg_lp_bound = float(avg_lp_bound)
                        gap = (float(sim_fnd) / num_avg_lp_bound * 100.0) if num_avg_lp_bound > 0 else 0.0
                        w.writerow([seed, algo['name'], sim_fnd, num_avg_lp_bound, gap]) # type: ignore
                        
                except Exception as e:
                    print(f"    Error in seed {seed}: {e}")
                    algo_results.append(0) # partial failure handling

            raw_data[algo['name']] = algo_results # type: ignore
            
            algo_mean = float(mean(algo_results))
            algo_std = float(stdev(algo_results)) if len(algo_results)>1 else 0.0
            
            # Optimality Gap
            num_avg_lp_bound = float(avg_lp_bound)
            gap = (float(algo_mean) / num_avg_lp_bound * 100.0) if num_avg_lp_bound > 0 else 0.0
            print(f"    FND: {algo_mean:.1f} ({gap:.1f}% of Optimal)")
            
            size_results[str(algo['name'])] = { # type: ignore
                'fnd_mean': algo_mean,
                'fnd_std': algo_std,
                'optimality_gap': gap
            }
            
        all_results[str(size) + "_nodes"] = size_results # type: ignore
        
        # Save intermediate JSON
        with open(f'{output_dir}/num_results_{size}.json', 'w') as f:
            json.dump(size_results, f, indent=2)
            
    return all_results

if __name__ == '__main__':
    run_num_experiments()
