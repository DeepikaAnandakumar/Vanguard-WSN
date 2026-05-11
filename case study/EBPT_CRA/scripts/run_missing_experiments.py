#!/usr/bin/env python3
"""
Run Missing Experiments: EBPT with Gamma Parameter Variants
============================================================

This script runs the critical missing experiments:
- EBPT with gamma=0.0 (baseline)
- EBPT with gamma=0.5 (proposed method)
- EBPT with gamma=1.0 (strong fairness)

Usage:
    python scripts/run_missing_experiments.py --seeds 15 --nodes 50 --output results_real
"""

import os
import sys
import json
import csv
import argparse
import random
import numpy as np
from statistics import mean, stdev
from scipy import stats
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.network import Network
import core.params as params


def run_single_simulation(algorithm, gamma, ch_strategy, seed, config):
    """Run a single simulation and collect metrics."""
    random.seed(seed)
    np.random.seed(seed)
    
    # Override energy parameter if specified
    if config.get('initial_energy'):
        params.INITIAL_ENERGY = config['initial_energy']
    if config.get('data_bits'):
        params.DATA_BITS = config['data_bits']
    
    try:
        # Create network
        net = Network(
            n=config['nodes'],
            field_x=config.get('field_x', 100),
            field_y=config.get('field_y', 100),
            bs_pos=config.get('bs_pos', (50, 50))
        )
        
        # Set routing strategy
        net.controller.routing_strategy = algorithm
        net.controller.ch_strategy = ch_strategy
        if algorithm == "EBPT":
            # Apply gamma parameter to EBPT
            net.controller.gamma = gamma
        
        net.build()
        
        # Collect metrics per round
        metrics = {
            "rounds": [],
            "alive": [],
            "energy": [],
            "fairness": [],
        }
        
        for r in range(config['rounds']):
            # Build network if needed (reconstruction every N rounds)
            if r > 0 and r % 100 == 0:
                if net.alive_nodes() > 0:
                    try:
                        net.build()
                    except:
                        pass
            
            net.run_round()
            net.log_metrics(r)
            
            metrics["rounds"].append(r)
            alive = net.alive_nodes()
            metrics["alive"].append(alive)
            
            total_energy = sum(n.energy for n in net.nodes if net._is_alive(n))
            metrics["energy"].append(total_energy)
            
            # Compute Jain's fairness index
            energies = [n.energy for n in net.nodes if n.energy > 0]
            if energies and len(energies) > 1:
                jain = (sum(energies)**2) / (len(energies) * sum(e**2 for e in energies))
                jain = max(0, min(1, jain))
            else:
                jain = 1.0 if energies else 0.0
            metrics["fairness"].append(jain)
            
            if alive == 0:
                break
        
        # Calculate lifetime metrics
        # FND: First node dies
        fnd = next((r for r, a in enumerate(metrics["alive"]) if a < config['nodes']), 
                   metrics["rounds"][-1] if metrics["rounds"] else 0)
        
        # HND: Half nodes dead
        hnd = next((r for r, a in enumerate(metrics["alive"]) if a <= config['nodes']/2), 
                   metrics["rounds"][-1] if metrics["rounds"] else 0)
        
        # LND: Last node dies
        lnd = next((r for r, a in enumerate(metrics["alive"]) if a == 0), 
                   metrics["rounds"][-1] if metrics["rounds"] else 0)
        
        # Average fairness (after FND to avoid initial perfect fairness)
        if fnd < len(metrics["fairness"]):
            avg_fairness = mean(metrics["fairness"][fnd:])
        else:
            avg_fairness = mean(metrics["fairness"]) if metrics["fairness"] else 0.0
        
        summary = {
            "algorithm": algorithm,
            "gamma": gamma,
            "ch_strategy": ch_strategy,
            "seed": seed,
            "nodes": config['nodes'],
            "fnd": fnd,
            "hnd": hnd,
            "lnd": lnd,
            "fairness": avg_fairness,
            "final_alive": metrics["alive"][-1] if metrics["alive"] else 0
        }
        
        return metrics, summary
        
    except Exception as e:
        print(f"  ERROR in seed {seed}: {e}")
        return None, None


def main():
    parser = argparse.ArgumentParser(description='Run missing EBPT gamma experiments')
    parser.add_argument('--seeds', type=int, default=15, help='Number of random seeds')
    parser.add_argument('--nodes', type=int, default=50, help='Number of nodes')
    parser.add_argument('--rounds', type=int, default=2000, help='Number of rounds')
    parser.add_argument('--output', type=str, default='results_real', help='Output directory')
    parser.add_argument('--ch-strategy', type=str, default='energy_aware', 
                       choices=['deterministic', 'random', 'energy_aware'],
                       help='Cluster head selection strategy')
    
    args = parser.parse_args()
    
    output_dir = args.output
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'stats'), exist_ok=True)
    
    print("="*70)
    print("RUNNING MISSING EXPERIMENTS: EBPT with Gamma Parameter")
    print("="*70)
    print(f"Configuration:")
    print(f"  Nodes: {args.nodes}")
    print(f"  Seeds: {args.seeds}")
    print(f"  Rounds: {args.rounds}")
    print(f"  CH Strategy: {args.ch_strategy}")
    print(f"  Output: {output_dir}")
    print()
    
    config = {
        'nodes': args.nodes,
        'rounds': args.rounds,
        'field_x': 100,
        'field_y': 100,
        'bs_pos': (50, 50),
        'initial_energy': 0.5,
        'data_bits': 2500
    }
    
    # Algorithms to test
    algorithms = [
        ("EBPT", 0.0),   # Baseline
        ("EBPT", 0.5),   # Proposed
        ("EBPT", 1.0),   # Strong fairness
    ]
    
    all_results = {}
    
    for algo, gamma in algorithms:
        algo_name = f"EBPT_g{gamma}"
        print(f"\n{'='*70}")
        print(f"Algorithm: {algo_name}")
        print(f"{'='*70}")
        
        results = []
        
        for seed in range(args.seeds):
            if seed % 5 == 0:
                print(f"  Seed {seed}/{args.seeds}...", end="", flush=True)
            
            metrics, summary = run_single_simulation(
                algo, gamma, args.ch_strategy, seed, config
            )
            
            if summary is not None:
                results.append(summary)
                if seed % 5 == 0:
                    print(f" FND={summary['fnd']}, LND={summary['lnd']}")
        
        print(f"\n  Completed {len(results)}/{args.seeds} seeds")
        all_results[algo_name] = results
        
        # Save individual results
        results_file = os.path.join(output_dir, f"{algo_name}_results.json")
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"  Saved: {results_file}")
    
    # Compute statistics
    print(f"\n{'='*70}")
    print("COMPUTING STATISTICS")
    print(f"{'='*70}")
    
    stats_data = []
    
    for algo_name, results in all_results.items():
        if not results:
            continue
        
        fnd_values = [r['fnd'] for r in results]
        hnd_values = [r['hnd'] for r in results]
        lnd_values = [r['lnd'] for r in results]
        fairness_values = [r['fairness'] for r in results]
        
        stats_row = {
            'Algorithm': algo_name,
            'CH_Strategy': args.ch_strategy,
            'Nodes': args.nodes,
            'Seeds': len(results),
            'FND_Mean': mean(fnd_values),
            'FND_Std': stdev(fnd_values) if len(fnd_values) > 1 else 0.0,
            'HND_Mean': mean(hnd_values),
            'HND_Std': stdev(hnd_values) if len(hnd_values) > 1 else 0.0,
            'LND_Mean': mean(lnd_values),
            'LND_Std': stdev(lnd_values) if len(lnd_values) > 1 else 0.0,
            'Fairness_Mean': mean(fairness_values),
            'Fairness_Std': stdev(fairness_values) if len(fairness_values) > 1 else 0.0,
        }
        stats_data.append(stats_row)
        
        print(f"\n{algo_name}:")
        print(f"  FND: {stats_row['FND_Mean']:.1f} ± {stats_row['FND_Std']:.2f}")
        print(f"  HND: {stats_row['HND_Mean']:.1f} ± {stats_row['HND_Std']:.2f}")
        print(f"  LND: {stats_row['LND_Mean']:.1f} ± {stats_row['LND_Std']:.2f}")
        print(f"  Fairness: {stats_row['Fairness_Mean']:.3f} ± {stats_row['Fairness_Std']:.3f}")
    
    # Save statistics CSV
    stats_file = os.path.join(output_dir, 'stats', 'aggregated_statistics.csv')
    if stats_data:
        with open(stats_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=stats_data[0].keys())
            writer.writeheader()
            writer.writerows(stats_data)
        print(f"\n  Saved statistics: {stats_file}")
    
    # Statistical tests (if we have EBPT_g0.0 and EBPT_g0.5)
    if 'EBPT_g0.0' in all_results and 'EBPT_g0.5' in all_results:
        baseline = all_results['EBPT_g0.0']
        proposed = all_results['EBPT_g0.5']
        
        if baseline and proposed:
            baseline_fnd = [r['fnd'] for r in baseline]
            proposed_fnd = [r['fnd'] for r in proposed]
            
            # Welch's t-test
            t_stat, p_value = stats.ttest_ind(proposed_fnd, baseline_fnd, equal_var=False)
            
            # Effect size (Cohen's d)
            pooled_std = np.sqrt((np.var(baseline_fnd) + np.var(proposed_fnd)) / 2)
            cohens_d = (np.mean(proposed_fnd) - np.mean(baseline_fnd)) / pooled_std if pooled_std > 0 else 0
            
            print(f"\n{'='*70}")
            print("STATISTICAL TEST: EBPT_g0.0 vs EBPT_g0.5")
            print(f"{'='*70}")
            print(f"  t-statistic: {t_stat:.2f}")
            print(f"  p-value: {p_value:.6f}")
            print(f"  Cohen's d: {cohens_d:.2f}")
            print(f"  Significant (p < 0.01): {'YES' if p_value < 0.01 else 'NO'}")
            
            # Save test results
            test_file = os.path.join(output_dir, 'stats', 'hypothesis_tests.csv')
            with open(test_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['Metric', 't_statistic', 'p_value', 'cohens_d', 'significant'])
                writer.writeheader()
                writer.writerow({
                    'Metric': 'FND',
                    't_statistic': f"{t_stat:.2f}",
                    'p_value': f"{p_value:.6f}",
                    'cohens_d': f"{cohens_d:.2f}",
                    'significant': 'YES' if p_value < 0.01 else 'NO'
                })
            print(f"  Saved test results: {test_file}")
    
    print(f"\n{'='*70}")
    print("EXPERIMENTS COMPLETE")
    print(f"{'='*70}")
    print(f"Results saved to: {output_dir}")
    print(f"Statistics: {stats_file}")
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

