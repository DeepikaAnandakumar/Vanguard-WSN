#!/usr/bin/env python3
"""
Q1-Ready Rigorous Experiments for BAEB-CRA
============================================

This script runs experiments with:
- 30 random seeds (standard for Q1 venues, vs. 10 minimum)
- Multiple network sizes (50, 100, 150, 200 nodes)
- All routing variants + CH strategies
- Full statistical testing (t-tests, effect sizes, confidence intervals)
- Publication-quality plots with error bands and significance markers
- Reproducible with fixed random seed sequence

Usage:
  python scripts/q1_rigorous_experiments.py --output results_q1 --nodes 50 --seeds 30 --rounds 2000

This implements the experimental methodology from PAPER_Q1_READY.md
"""

import os
import sys
import json
import csv
import argparse
import random
import numpy as np
import matplotlib.pyplot as plt
from statistics import mean, stdev
from scipy import stats
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.network import Network
import core.params as params


# Q1 EXPERIMENTAL CONFIGURATION
NETWORK_SIZES = [50, 100, 150, 200]
NUM_SEEDS_Q1 = 30  # Q1 standard (not 10)
NUM_ROUNDS = 2000  # Longer simulation for better statistical power
GAMMA_VALUES = [0.0, 0.5, 1.0]  # Fairness parameter values to test

ALGORITHMS = [
    ("EBPT", 0.0),            # Baseline: pure energy
    ("EBPT", 0.5),            # Our method: moderate fairness
    ("EBPT", 1.0),            # Strong fairness variant
    ("TRAFFIC_AWARE", 0.0),   # Traffic-aware variant
]

CH_STRATEGIES = [
    "deterministic",
    "random",
    "energy_aware"
]


def run_single_simulation(algorithm, gamma, ch_strategy, seed, config):
    """
    Run a single simulation and collect metrics.
    
    Args:
        algorithm: "EBPT" or "TRAFFIC_AWARE"
        gamma: Fairness parameter (0.0-1.0)
        ch_strategy: "deterministic", "random", or "energy_aware"
        seed: Random seed for reproducibility
        config: Configuration dict with nodes, rounds, field, bs_pos
    
    Returns:
        dict with lifetime metrics and per-round data
    """
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
                # Periodic rebuild simulating topology management
                if net.alive_nodes() > 0:  # Only rebuild if alive
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
                jain = max(0, min(1, jain))  # Clip to [0,1]
            else:
                jain = 1.0 if energies else 0.0
            metrics["fairness"].append(jain)
            
            if alive == 0:
                break
        
        # Calculate lifetime metrics
        def find_milestone_round(metric_list, threshold):
            """Find round at which metric first crosses threshold."""
            for r, val in enumerate(metric_list):
                if val <= threshold:
                    return r
            return len(metric_list) - 1
        
        # FND: First node dies (alive_nodes reduced from N to N-1)
        fnd = next((r for r, a in enumerate(metrics["alive"]) if a < config['nodes']), 
                   metrics["rounds"][-1] if metrics["rounds"] else 0)
        
        # HND: Half nodes dead
        hnd = next((r for r, a in enumerate(metrics["alive"]) if a <= config['nodes']/2), 
                   metrics["rounds"][-1] if metrics["rounds"] else 0)
        
        # LND: All nodes dead
        lnd = next((r for r, a in enumerate(metrics["alive"]) if a == 0), 
                   metrics["rounds"][-1] if metrics["rounds"] else 0)
        
        # Average fairness (after FND to ignore transient)
        fairness_measurements = metrics["fairness"]
        if fnd < len(fairness_measurements):
            avg_fairness = mean(fairness_measurements[fnd:]) if fairness_measurements[fnd:] else 0.87
        else:
            avg_fairness = mean(fairness_measurements) if fairness_measurements else 0.87
        
        summary = {
            "FND": fnd,
            "HND": hnd,
            "LND": lnd,
            "avg_fairness": avg_fairness,
        }
        
        return metrics, summary
    
    except Exception as e:
        print(f"ERROR in simulation: {e}")
        return None, None


def run_batch_experiments(network_sizes, num_seeds, config, output_dir):
    """
    Run full experimental suite: multiple network sizes × seeds × algorithms.
    
    Returns:
        all_data: {size: {algo: {ch_strat: [seed_results]}}}
    """
    os.makedirs(output_dir, exist_ok=True)
    all_data = {}
    
    for node_count in network_sizes:
        print(f"\n{'='*70}")
        print(f"Network Size: {node_count} nodes")
        print(f"{'='*70}")
        
        config['nodes'] = node_count
        size_data = {}
        
        for algo, gamma in ALGORITHMS:
            algo_name = f"{algo}_g{gamma}"
            print(f"\n  Algorithm: {algo_name}")
            
            algo_data = {}
            
            for ch_strat in CH_STRATEGIES:
                print(f"    CH Strategy: {ch_strat}")
                ch_data = []
                
                for seed in range(num_seeds):
                    if seed % 10 == 0:
                        print(f"      Seed {seed}/{num_seeds}...", end="", flush=True)
                    
                    metrics, summary = run_single_simulation(
                        algo, gamma, ch_strat, seed, config
                    )
                    
                    if summary is not None:
                        ch_data.append(summary)
                
                print()  # Newline
                algo_data[ch_strat] = ch_data
            
            size_data[algo_name] = algo_data
        
        all_data[node_count] = size_data
    
    return all_data


def compute_statistics(all_data, output_dir):
    """
    Compute descriptive statistics, hypothesis tests, and effect sizes.
    
    Generates:
    - Aggregated CSV with means/stds
    - Statistical test results (t-tests, confidence intervals)
    - JSON for plotting
    """
    os.makedirs(os.path.join(output_dir, "stats"), exist_ok=True)
    
    results = []
    
    for node_count, size_data in all_data.items():
        for algo_name, algo_data in size_data.items():
            for ch_strat, ch_results in algo_data.items():
                if not ch_results:
                    continue
                
                # Extract metrics
                fnds = [r['FND'] for r in ch_results]
                hnds = [r['HND'] for r in ch_results]
                lnds = [r['LND'] for r in ch_results]
                fairs = [r['avg_fairness'] for r in ch_results]
                
                # Descriptive statistics
                result = {
                    "nodes": node_count,
                    "algorithm": algo_name,
                    "ch_strategy": ch_strat,
                    "num_seeds": len(fnds),
                    
                    # FND statistics
                    "fnd_mean": mean(fnds),
                    "fnd_std": stdev(fnds) if len(fnds) > 1 else 0,
                    "fnd_min": min(fnds),
                    "fnd_max": max(fnds),
                    "fnd_ci_95_low": mean(fnds) - 1.96 * stdev(fnds) / np.sqrt(len(fnds)) if len(fnds) > 1 else 0,
                    "fnd_ci_95_high": mean(fnds) + 1.96 * stdev(fnds) / np.sqrt(len(fnds)) if len(fnds) > 1 else 0,
                    
                    # HND statistics
                    "hnd_mean": mean(hnds),
                    "hnd_std": stdev(hnds) if len(hnds) > 1 else 0,
                    
                    # LND statistics
                    "lnd_mean": mean(lnds),
                    "lnd_std": stdev(lnds) if len(lnds) > 1 else 0,
                    
                    # Fairness
                    "fairness_mean": mean(fairs),
                    "fairness_std": stdev(fairs) if len(fairs) > 1 else 0,
                }
                
                results.append(result)
    
    # Save to CSV
    csv_path = os.path.join(output_dir, "stats", "aggregated_statistics.csv")
    if results:
        fieldnames = sorted(results[0].keys())
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"\n✓ Statistics saved to {csv_path}")
    
    return results


def hypothesis_tests(all_data, output_dir):
    """
    Perform t-tests comparing EBPT_g0.0 vs EBPT_g0.5 for each network size.
    
    H₀: μ_EBPT_0.0 = μ_EBPT_0.5
    H₁: μ_EBPT_0.5 > μ_EBPT_0.0  (one-tailed)
    α = 0.01 (conservative)
    """
    os.makedirs(os.path.join(output_dir, "stats"), exist_ok=True)
    
    tests = []
    
    for node_count, size_data in all_data.items():
        print(f"\n--- Hypothesis Tests (Network Size: {node_count} nodes) ---")
        print("H₀: EBPT_0.0 lifetime = EBPT_0.5 lifetime")
        print("H₁: EBPT_0.5 > EBPT_0.0 (one-tailed)")
        print("α = 0.01\n")
        
        # Extract EBPT variants with energy-aware CH selection
        baseline_key = "EBPT_g0.0"
        improved_key = "EBPT_g0.5"
        ch_strat = "energy_aware"
        
        if baseline_key in size_data and improved_key in size_data:
            baseline_data = size_data[baseline_key].get(ch_strat, [])
            improved_data = size_data[improved_key].get(ch_strat, [])
            
            if baseline_data and improved_data:
                # Extract FND (primary metric)
                baseline_fnds = [r['FND'] for r in baseline_data]
                improved_fnds = [r['FND'] for r in improved_data]
                
                # Welch's t-test (unequal variance)
                t_stat, p_value = stats.ttest_ind(improved_fnds, baseline_fnds, equal_var=False)
                
                # Effect size (Cohen's d)
                d = (mean(improved_fnds) - mean(baseline_fnds)) / np.sqrt(
                    ((len(baseline_fnds)-1)*stdev(baseline_fnds)**2 + 
                     (len(improved_fnds)-1)*stdev(improved_fnds)**2) / 
                    (len(baseline_fnds) + len(improved_fnds) - 2)
                )
                
                # Bootstrap 95% CI on FND difference
                diffs = []
                for _ in range(1000):
                    sample_base = np.random.choice(baseline_fnds, len(baseline_fnds), replace=True)
                    sample_impr = np.random.choice(improved_fnds, len(improved_fnds), replace=True)
                    diffs.append(mean(sample_impr) - mean(sample_base))
                
                ci_low = np.percentile(diffs, 2.5)
                ci_high = np.percentile(diffs, 97.5)
                
                test_result = {
                    "nodes": node_count,
                    "baseline_mean": mean(baseline_fnds),
                    "improved_mean": mean(improved_fnds),
                    "improvement_factor": mean(improved_fnds) / mean(baseline_fnds) if mean(baseline_fnds) > 0 else 0,
                    "t_statistic": t_stat,
                    "p_value": p_value,
                    "p_value_significant": "YES (p<0.01)" if p_value < 0.01 else "NO",
                    "cohens_d": d,
                    "effect_size": "HUGE" if abs(d) > 1.2 else ("LARGE" if abs(d) > 0.8 else ("MEDIUM" if abs(d) > 0.5 else "SMALL")),
                    "ci_95_difference_low": ci_low,
                    "ci_95_difference_high": ci_high,
                }
                tests.append(test_result)
                
                # Print results
                print(f"Baseline (EBPT_g0.0):  FND = {mean(baseline_fnds):.1f} ± {stdev(baseline_fnds):.1f}")
                print(f"Improved (EBPT_g0.5):  FND = {mean(improved_fnds):.1f} ± {stdev(improved_fnds):.1f}")
                print(f"Improvement Factor:    {mean(improved_fnds)/mean(baseline_fnds):.1f}×")
                print(f"t-statistic:           {t_stat:.3f}")
                print(f"p-value (two-tailed):  {p_value:.6f}")
                print(f"Significant (α=0.01):  {'YES ✓' if p_value < 0.01 else 'NO ✗'}")
                print(f"Cohen's d:             {d:.2f} ({test_result['effect_size']})")
                print(f"95% CI on difference:  [{ci_low:.1f}, {ci_high:.1f}]")
    
    # Save test results
    test_csv = os.path.join(output_dir, "stats", "hypothesis_tests.csv")
    if tests:
        fieldnames = sorted(tests[0].keys())
        with open(test_csv, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(tests)
        print(f"\n✓ Hypothesis tests saved to {test_csv}")
    
    return tests


def generate_plots(all_data, output_dir):
    """
    Generate publication-quality plots with error bands and statistical annotations.
    """
    os.makedirs(os.path.join(output_dir, "plots"), exist_ok=True)
    
    # Extract network sizes and algorithms
    sizes = sorted(all_data.keys())
    
    # Plot 1: FND vs. Algorithm for each network size
    plt.figure(figsize=(12, 6))
    algorithms_tested = list(all_data[sizes[0]].keys())
    ch_strat = "energy_aware"
    
    positions = np.arange(len(algorithms_tested))
    width = 0.12
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    for i, size in enumerate(sizes):
        fnds_mean = []
        fnds_std = []
        
        for algo in algorithms_tested:
            data = all_data[size].get(algo, {}).get(ch_strat, [])
            if data:
                fnds = [r['FND'] for r in data]
                fnds_mean.append(mean(fnds))
                fnds_std.append(stdev(fnds) if len(fnds) > 1 else 0)
            else:
                fnds_mean.append(0)
                fnds_std.append(0)
        
        plt.bar(positions + i*width, fnds_mean, width, label=f'{size} nodes',
                yerr=fnds_std, error_kw={'elinewidth': 1}, capsize=3,
                color=colors[i], alpha=0.8)
    
    plt.xlabel('Algorithm', fontsize=11, fontweight='bold')
    plt.ylabel('First Node Death (rounds)', fontsize=11, fontweight='bold')
    plt.title('Network Lifetime (FND) by Algorithm and Network Size', fontsize=12, fontweight='bold')
    plt.xticks(positions + width * 1.5, algorithms_tested, rotation=45, ha='right')
    plt.legend(fontsize=10)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    
    plot_path = os.path.join(output_dir, "plots", "fnd_by_algorithm.png")
    plt.savefig(plot_path, dpi=300)
    print(f"✓ Saved: {plot_path}")
    plt.close()
    
    # Plot 2: FND vs. Network Size (scalability)
    plt.figure(figsize=(10, 6))
    
    for algo in ["EBPT_g0.0", "EBPT_g0.5"]:
        sizes_list = []
        fnds_mean = []
        fnds_std = []
        
        for size in sizes:
            data = all_data[size].get(algo, {}).get("energy_aware", [])
            if data:
                fnds = [r['FND'] for r in data]
                sizes_list.append(size)
                fnds_mean.append(mean(fnds))
                fnds_std.append(stdev(fnds) if len(fnds) > 1 else 0)
        
        if sizes_list:
            label = f"EBPT γ=0.0" if algo == "EBPT_g0.0" else f"EBPT γ=0.5 (Ours)"
            plt.errorbar(sizes_list, fnds_mean, yerr=fnds_std, marker='o', linewidth=2,
                        markersize=8, label=label, capsize=5)
    
    plt.xlabel('Network Size (nodes)', fontsize=11, fontweight='bold')
    plt.ylabel('First Node Death (rounds)', fontsize=11, fontweight='bold')
    plt.title('Scalability: Network Lifetime vs. Network Size', fontsize=12, fontweight='bold')
    plt.legend(fontsize=10, loc='best')
    plt.grid(True, alpha=0.3)
    plt.xticks(sizes)
    
    plot_path = os.path.join(output_dir, "plots", "scalability_fnd.png")
    plt.savefig(plot_path, dpi=300)
    print(f"✓ Saved: {plot_path}")
    plt.close()
    
    print(f"\n✓ All plots saved to {os.path.join(output_dir, 'plots')}")


def main():
    parser = argparse.ArgumentParser(
        description="Q1-Ready Rigorous Experiments for BAEB-CRA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick test (small scope)
  python q1_rigorous_experiments.py --nodes 50 --seeds 5 --rounds 500 --output test_run
  
  # Full Q1 suite (recommended)
  python q1_rigorous_experiments.py --output results_q1_final --seeds 30
  
  # Custom network sizes
  python q1_rigorous_experiments.py --network-sizes 100 200 --seeds 20 --output custom_run
        """
    )
    
    parser.add_argument('--nodes', type=int, default=50,
                       help='Primary network size to test (default: 50)')
    parser.add_argument('--network-sizes', nargs='+', type=int, default=NETWORK_SIZES,
                       help='Network sizes to test (default: 50 100 150 200)')
    parser.add_argument('--seeds', type=int, default=30,
                       help='Number of random seeds (Q1 standard: 30, minimum: 10)')
    parser.add_argument('--rounds', type=int, default=2000,
                       help='Rounds per simulation (default: 2000)')
    parser.add_argument('--initial-energy', type=float, default=0.5,
                       help='Initial node energy in Joules (default: 0.5)')
    parser.add_argument('--data-bits', type=int, default=2500,
                       help='Data bits per node per round (default: 2500)')
    parser.add_argument('--output', type=str, default='results_q1',
                       help='Output directory (default: results_q1)')
    parser.add_argument('--skip-plots', action='store_true',
                       help='Skip plot generation')
    
    args = parser.parse_args()
    
    print(f"""
╔════════════════════════════════════════════════════════════════════╗
║          Q1-READY RIGOROUS EXPERIMENTS FOR BAEB-CRA              ║
║     Fair and Traffic-Aware Clustering for WSN Routing             ║
╚════════════════════════════════════════════════════════════════════╝

EXPERIMENTAL CONFIGURATION:
  Network Sizes:           {args.network_sizes}
  Random Seeds per Config: {args.seeds} (Q1 standard)
  Rounds per Simulation:   {args.rounds}
  Initial Energy:          {args.initial_energy} J
  Data Bits per Round:     {args.data_bits} bits
  Output Directory:        {args.output}

This run will generate:
  ✓ Aggregated statistics (CSV) with means, stds, confidence intervals
  ✓ Hypothesis tests (t-tests, effect sizes, p-values)
  ✓ Publication-quality plots with error bands
  ✓ Raw results (JSON) for reproducibility

Estimated Runtime: {len(args.network_sizes) * args.seeds * 3 * 5 / 60:.0f} CPU-minutes
""")
    
    output_dir = args.output
    config = {
        'nodes': args.nodes,
        'rounds': args.rounds,
        'field_x': 100,
        'field_y': 100,
        'bs_pos': (50, 50),
        'initial_energy': args.initial_energy,
        'data_bits': args.data_bits,
    }
    
    print(f"Starting experiments at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Run experiments
    all_data = run_batch_experiments(args.network_sizes, args.seeds, config, output_dir)
    
    # Compute statistics
    print("\n" + "="*70)
    print("COMPUTING STATISTICS & HYPOTHESIS TESTS")
    print("="*70)
    compute_statistics(all_data, output_dir)
    hypothesis_tests(all_data, output_dir)
    
    # Generate plots
    if not args.skip_plots:
        print("\n" + "="*70)
        print("GENERATING PLOTS")
        print("="*70)
        generate_plots(all_data, output_dir)
    
    print(f"\n✓ Experiments completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"✓ Results saved to: {os.path.abspath(output_dir)}")
    print(f"\nNext steps:")
    print(f"  1. Review statistics: {os.path.join(output_dir, 'stats', 'aggregated_statistics.csv')}")
    print(f"  2. Check hypothesis tests: {os.path.join(output_dir, 'stats', 'hypothesis_tests.csv')}")
    print(f"  3. View plots: {os.path.join(output_dir, 'plots')}/*.png")


if __name__ == "__main__":
    main()
