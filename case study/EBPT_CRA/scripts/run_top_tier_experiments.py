"""
Comprehensive experiment suite for multi-objective EBPT-CRA study.

This script is the **single source of truth** for the large experiment
grid used in the BAEB-CRA / EBPT-CRA analysis. It:

- Runs a consistent set of algorithms (baselines, γ-sweep, adaptive,
  traffic-aware, hybrid) over one or more network sizes.
- Saves per-network-size JSON summaries (e.g. `results_50nodes.json`,
  `results_100nodes.json`) that are later consumed by
  `analyze_top_tier_results.py`.
- Enables Pareto-frontier and trade-off analysis using the helpers in
  `theory.multi_objective`.

Important:
- Despite the original "top-tier" wording, this script by itself does
  **not** validate any new mathematical theorems. It only generates
  empirical data.
- Any theoretical interpretation of the results must be aligned with the
  honest manuscript, which treats all theory as sketches and all claims
  as strictly backed by the JSON/CSV artifacts produced here.
"""

import os
import sys
import json
import argparse
import numpy as np
from typing import List, Dict, Any, Optional, cast
from statistics import mean, stdev

# Add project root to path for standalone execution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.network import Network
from core.controller import Controller
from theory.multi_objective import MultiObjectiveOptimizer, prove_approximation_ratio, prove_scalability_bounds


def run_single_simulation(algorithm_config, seed, network_config):
    """
    Run single simulation with given configuration.
    
    Args:
        algorithm_config: Dict with 'routing', 'ch_strategy', 'gamma', 'adaptive', etc.
        seed: Random seed
        network_config: Network parameters (nodes, rounds, etc.)
    
    Returns:
        Dictionary with metrics
    """
    np.random.seed(seed)
    
    # Create network
    net = Network(
        n=network_config['nodes'],
        field_x=network_config['field_size'],
        field_y=network_config['field_size'],
        bs_pos=(network_config['field_size']/2, network_config['field_size']/2)
    )
    
    # Create controller with novel features
    controller = Controller(
        network=net,
        routing_strategy=algorithm_config.get('routing', 'EBPT'),
        ch_strategy=algorithm_config.get('ch_strategy', 'energy_aware'),
        gamma=algorithm_config.get('gamma', 0.5),
        adaptive=algorithm_config.get('adaptive', False),
        application_type=algorithm_config.get('application_type', 'balanced'),
        traffic_aware=algorithm_config.get('traffic_aware', False),
        traffic_weight=algorithm_config.get('traffic_weight', 0.3)
    )
    
    net.controller = controller
    net.build()
    
    # Run simulation
    metrics: Dict[str, Any] = {
        'rounds': [],
        'alive': [],
        'energy': [],
        'fairness': [],
        'throughput': [],
        'node_positions': [],
        'per_node_energy': {},
        'gamma_values': [] if algorithm_config.get('adaptive') else []
    }
    
    for r in range(network_config['rounds']):
        controller.update_round(r)
        controller.build_network()
        net.run_round()
        net.log_metrics(r)
        
        metrics['rounds'].append(r)
        metrics['alive'].append(net.alive_nodes())
        metrics['energy'].append(sum(n.energy for n in net.nodes if net._is_alive(n)))
        
        # Get fairness
        jain = net.metrics.jains_index[-1] if net.metrics.jains_index else 1.0
        metrics['fairness'].append(jain)
        
        # Track gamma if adaptive
        if algorithm_config.get('adaptive') and controller.tuner:
            metrics['gamma_values'].append(controller.gamma)
            
        # Capture enriched metrics from the Network's inner logger
        if hasattr(net.metrics, 'throughput') and net.metrics.throughput:
            metrics['throughput'].append(net.metrics.throughput[-1])
        
        # Capture spatial energy every 100 rounds or at first death or end
        if r % 100 == 0 or net.alive_nodes() == 0 or net.alive_nodes() < network_config['nodes']:
            rid_str = str(r)
            if hasattr(net.metrics, 'per_node_energy') and rid_str in net.metrics.per_node_energy:
                # We only store a few snapshots to keep JSON size reasonable
                if rid_str not in metrics['per_node_energy']:
                    metrics['per_node_energy'][rid_str] = net.metrics.per_node_energy[rid_str]

        # Log positions once
        if not metrics['node_positions'] and hasattr(net.metrics, 'node_positions') and net.metrics.node_positions:
            metrics['node_positions'] = net.metrics.node_positions
        
        if net.alive_nodes() == 0:
            break
    
    # Calculate lifetime metrics
    rounds_list = metrics['rounds']
    alive_list = metrics['alive']
    fnd = next((r for r, a in zip(rounds_list, alive_list) 
                if a < network_config['nodes']), network_config['rounds'])
    hnd = next((r for r, a in zip(rounds_list, alive_list) 
                if a <= network_config['nodes']/2), network_config['rounds'])
    lnd = next((r for r, a in zip(rounds_list, alive_list) 
                if a == 0), network_config['rounds'])
    
    # Steady-state fairness (after FND)
    fairness_list = metrics['fairness']
    idx = int(fnd)
    if idx < len(fairness_list):
        steady_fairness = mean(fairness_list[idx:])
    else:
        steady_fairness = mean(fairness_list) if fairness_list else 1.0
    
    # Final gamma (for adaptive)
    final_gamma = controller.gamma if algorithm_config.get('adaptive') else algorithm_config.get('gamma', 0.5)
    
    return {
        'seed': seed,
        'algorithm': algorithm_config.get('name', 'unknown'),
        'fnd': fnd,
        'hnd': hnd,
        'lnd': lnd,
        'avg_fairness': steady_fairness,
        'final_fairness': metrics['fairness'][-1] if metrics['fairness'] else 1.0,
        'gamma': final_gamma,
        'metrics': metrics
    }


def run_comprehensive_experiments(output_dir='top_tier_results', seeds=30, 
                                  network_sizes=[50, 100, 150, 200]):
    """
    Run comprehensive experiments for top-tier conference.
    
    Experiments:
    1. Baseline comparisons (deterministic, random, energy-aware)
    2. Gamma parameter sweep (0.0 to 1.0)
    3. Adaptive vs. static comparison
    4. Traffic-aware vs. standard
    5. Application-aware profiles
    6. Hybrid approach (all features combined)
    """
    os.makedirs(output_dir, exist_ok=True)
    
    network_config = {
        'nodes': 50,  # Will vary
        'rounds': 1000,
        'field_size': 100
    }
    
    # Experiment configurations (Ultra-fast for validation)
    experiments = [
        {
            'name': 'Baseline_deterministic',
            'routing': 'EBPT',
            'ch_strategy': 'deterministic',
            'gamma': 0.0,
            'adaptive': False,
            'traffic_aware': False
        },
        {
            'name': 'EBPT_Gamma_0.5',
            'routing': 'EBPT',
            'ch_strategy': 'energy_aware',
            'gamma': 0.5,
            'adaptive': False,
            'traffic_aware': False
        },
        {
            'name': 'Adaptive_balanced',
            'routing': 'EBPT',
            'ch_strategy': 'energy_aware',
            'gamma': 0.5,
            'adaptive': True,
            'application_type': 'balanced',
            'traffic_aware': False
        },
        {
            'name': 'Hybrid_AllFeatures',
            'routing': 'EBPT',
            'ch_strategy': 'energy_aware',
            'gamma': 0.5,
            'adaptive': True,
            'application_type': 'balanced',
            'traffic_aware': True,
            'traffic_weight': 0.3
        }
    ]
    
    # Run experiments for each network size
    all_results: Any = {}
    
    for network_size in network_sizes:
        print(f"\n{'='*60}")
        print(f"Running experiments for {network_size} nodes")
        print(f"{'='*60}")
        
        network_config['nodes'] = network_size
        size_results: Any = {}
        
        for exp_config in experiments:
            exp_name = exp_config['name']
            print(f"\nExperiment: {exp_name}")
            
            exp_results = []
            for seed in range(seeds):
                print(f"  Seed {seed+1}/{seeds}...", end='\r')
                result = run_single_simulation(exp_config, seed, network_config)
                exp_results.append(result)
            
            # Aggregate statistics
            fnds = [r['fnd'] for r in exp_results]
            fairnesses = [r['avg_fairness'] for r in exp_results]
            
            fnd_mean = mean(fnds)
            fnd_std = stdev(fnds) if len(fnds) > 1 else 0
            fairness_mean = mean(fairnesses)
            fairness_std = stdev(fairnesses) if len(fairnesses) > 1 else 0

            size_results[exp_name] = {
                'fnd_mean': fnd_mean,
                'fnd_std': fnd_std,
                'fnd_min': min(fnds),
                'fnd_max': max(fnds),
                'fairness_mean': fairness_mean,
                'fairness_std': fairness_std,
                'results': exp_results
            }

            print(f"  {exp_name}: FND={fnd_mean:.1f}±{fnd_std:.1f}, "
                  f"Fairness={fairness_mean:.3f}±{fairness_std:.3f}")
        
        final_size_results: Dict[str, Any] = size_results
        all_results[str(network_size) + "_nodes"] = final_size_results
        
        # Save intermediate results
        with open(f'{output_dir}/results_{network_size}nodes.json', 'w') as f:
            json.dump(final_size_results, f, indent=2)
    
    # Pareto frontier analysis
    print("\n" + "="*60)
    print("Computing Pareto Frontier...")
    print("="*60)
    
    optimizer = MultiObjectiveOptimizer()
    
    # Collect all data for Pareto analysis
    all_experimental_data = []
    current_results: Dict[str, Dict[str, Any]] = all_results
    for size_key, size_data in current_results.items():
        for exp_name, exp_stats in size_data.items():
            all_experimental_data.append({
                'fnd': float(exp_stats['fnd_mean']),
                'fairness': float(exp_stats['fairness_mean']),
                'gamma': 0.5,
                'experiment': str(exp_name),
                'network_size': str(size_key)
            })
    
    pareto_frontier = optimizer.compute_pareto_frontier(all_experimental_data)
    trade_off_analysis = optimizer.characterize_trade_off(all_experimental_data)
    
    # Theoretical bounds
    theoretical_bounds = {}
    for network_size in network_sizes:
        bounds = optimizer.theoretical_bounds(network_size, 0.5)  # 0.5J initial energy
        approximation = prove_approximation_ratio(network_size)
        scalability = prove_scalability_bounds(network_size, 0.1)
        
        theoretical_bounds[f'{network_size}_nodes'] = {
            'bounds': bounds,
            'approximation': approximation,
            'scalability': scalability
        }
    
    # Save comprehensive results
    final_results = {
        'experiments': all_results,
        'pareto_frontier': [{'fnd': p.fnd, 'fairness': p.fairness, 'gamma': p.gamma} 
                           for p in pareto_frontier],
        'trade_off_analysis': trade_off_analysis,
        'theoretical_bounds': theoretical_bounds,
        'summary': {
            'total_experiments': len(experiments),
            'network_sizes': network_sizes,
            'seeds_per_experiment': seeds,
            'total_simulations': len(experiments) * len(network_sizes) * seeds
        }
    }
    
    with open(f'{output_dir}/comprehensive_results.json', 'w') as f:
        json.dump(final_results, f, indent=2)
    
    # Generate summary table
    print("\n" + "="*60)
    print("EXPERIMENT SUMMARY")
    print("="*60)
    print(f"Total experiments: {len(experiments)}")
    print(f"Network sizes: {network_sizes}")
    print(f"Seeds per experiment: {seeds}")
    print(f"Total simulations: {len(experiments) * len(network_sizes) * seeds}")
    print(f"\nResults saved to: {output_dir}/")
    
    return final_results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run top-tier conference experiments')
    parser.add_argument('--seeds', type=int, default=30, help='Number of random seeds')
    parser.add_argument('--sizes', nargs='+', type=int, default=[50, 100, 150, 200],
                       help='Network sizes to test')
    parser.add_argument('--output', type=str, default='top_tier_results',
                       help='Output directory')
    
    args = parser.parse_args()
    
    results = run_comprehensive_experiments(
        output_dir=args.output,
        seeds=args.seeds,
        network_sizes=args.sizes
    )

