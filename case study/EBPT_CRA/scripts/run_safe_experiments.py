#!/usr/bin/env python3
"""
Safe experiments with reasonable parameters and energy-aware CH selection.
Compares deterministic vs energy-aware CH selection.
"""
import os
import sys
import json
import csv
import matplotlib.pyplot as plt
from statistics import mean, stdev
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.network import Network
import core.params as params

def run_single_simulation(ch_strategy, seed, num_rounds=1000, num_nodes=50):
    """Run a single simulation with specified CH strategy."""
    print(f"  CH Strategy: {ch_strategy}, Seed: {seed} Started...")
    random.seed(seed)
    
    # Use safe defaults: 4000 bits/round, 0.5 J initial energy
    params.DATA_BITS = 4000
    params.INITIAL_ENERGY = 0.5
    params.CH_PROB = 0.05
    
    net = Network(n=num_nodes, field_x=100, field_y=100, bs_pos=(50, 50))
    
    # Set controller strategy
    net.controller.ch_strategy = ch_strategy
    net.build()
    
    metrics = {
        "rounds": [],
        "alive_nodes": [],
        "total_energy": [],
        "dead_nodes": [],
        "num_chs": [],
        "jains_index": [],
        "avg_hops": []
    }
    
    for r in range(num_rounds):
        net.controller.build_network()
        net.run_round()
        net.log_metrics(r)
        
        metrics["rounds"].append(r)
        metrics["alive_nodes"].append(net.alive_nodes())
        metrics["total_energy"].append(sum(n.energy for n in net.nodes if net._is_alive(n)))
        metrics["dead_nodes"].append(len(net.nodes) - net.alive_nodes())
        metrics["num_chs"].append(sum(1 for ch in (net.cluster_heads or []) if net._is_alive(ch)))
        jain = net.metrics.jains_index[-1] if net.metrics.jains_index else 1.0
        metrics["jains_index"].append(jain)
        avg_hops = net.metrics.average_hop_count[-1] if hasattr(net.metrics, 'average_hop_count') and net.metrics.average_hop_count else 0.0
        metrics["avg_hops"].append(avg_hops)
        
        if net.alive_nodes() == 0:
            print(f"  CH Strategy: {ch_strategy}, Seed: {seed} - Network dead at round {r}")
            break
    
    # Calculate lifetime metrics
    fnd = net.metrics.first_node_death if net.metrics.first_node_death is not None else num_rounds
    hnd = net.metrics.half_node_death if net.metrics.half_node_death is not None else num_rounds
    lnd = net.metrics.last_node_death if net.metrics.last_node_death is not None else num_rounds
    
    print(f"  CH Strategy: {ch_strategy}, Seed: {seed} Finished. FND: {fnd}, HND: {hnd}, LND: {lnd}")
    
    summary = {
        "FND": fnd,
        "HND": hnd,
        "LND": lnd,
        "avg_jains": mean(metrics["jains_index"]) if metrics["jains_index"] else 0.0
    }
    
    return metrics, summary

def generate_plots(all_data, output_dir):
    """Generate comparison plots."""
    os.makedirs(output_dir, exist_ok=True)
    
    strategies = list(all_data.keys())
    colors = {'deterministic': 'blue', 'energy_aware': 'green', 'random': 'orange'}
    
    # 1. Network Lifetime (Alive Nodes vs Rounds)
    plt.figure(figsize=(12, 6))
    for strat in strategies:
        seeds_data = all_data[strat]
        all_rounds = sorted(set(r for seed in seeds_data for r in seed['metrics']['rounds']))
        avg_alive = []
        std_alive = []
        
        for r in all_rounds:
            vals = []
            for seed in seeds_data:
                if r in seed['metrics']['rounds']:
                    idx = seed['metrics']['rounds'].index(r)
                    vals.append(seed['metrics']['alive_nodes'][idx])
                else:
                    vals.append(0)
            avg_alive.append(mean(vals))
            std_alive.append(stdev(vals) if len(vals) > 1 else 0)
        
        color = colors.get(strat, 'black')
        plt.plot(all_rounds, avg_alive, label=f'{strat} (n={len(seeds_data)})', linewidth=2, color=color)
        plt.fill_between(all_rounds, 
                         [a - s for a, s in zip(avg_alive, std_alive)],
                         [a + s for a, s in zip(avg_alive, std_alive)],
                         alpha=0.2, color=color)
    
    plt.xlabel("Rounds", fontsize=12)
    plt.ylabel("Alive Nodes", fontsize=12)
    plt.title("Network Lifetime Comparison (Avg ± Std across seeds)", fontsize=14)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "01_alive_nodes_vs_rounds.png"), dpi=150)
    plt.close()
    
    # 2. Energy Consumption
    plt.figure(figsize=(12, 6))
    for strat in strategies:
        seeds_data = all_data[strat]
        all_rounds = sorted(set(r for seed in seeds_data for r in seed['metrics']['rounds']))
        avg_energy = []
        
        for r in all_rounds:
            vals = []
            for seed in seeds_data:
                if r in seed['metrics']['rounds']:
                    idx = seed['metrics']['rounds'].index(r)
                    vals.append(seed['metrics']['total_energy'][idx])
                else:
                    vals.append(0)
            avg_energy.append(mean(vals))
        
        color = colors.get(strat, 'black')
        plt.plot(all_rounds, avg_energy, label=strat, linewidth=2, color=color)
    
    plt.xlabel("Rounds", fontsize=12)
    plt.ylabel("Total Energy (J)", fontsize=12)
    plt.title("Energy Consumption Over Time", fontsize=14)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "02_energy_vs_rounds.png"), dpi=150)
    plt.close()
    
    # 3. Fairness (Jain's Index)
    plt.figure(figsize=(12, 6))
    for strat in strategies:
        seeds_data = all_data[strat]
        all_rounds = sorted(set(r for seed in seeds_data for r in seed['metrics']['rounds']))
        avg_jains = []
        
        for r in all_rounds:
            vals = []
            for seed in seeds_data:
                if r in seed['metrics']['rounds']:
                    idx = seed['metrics']['rounds'].index(r)
                    vals.append(seed['metrics']['jains_index'][idx])
                else:
                    vals.append(1.0)
            avg_jains.append(mean(vals))
        
        color = colors.get(strat, 'black')
        plt.plot(all_rounds, avg_jains, label=strat, linewidth=2, color=color)
    
    plt.xlabel("Rounds", fontsize=12)
    plt.ylabel("Jain's Fairness Index", fontsize=12)
    plt.title("Load Fairness Over Time", fontsize=14)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "03_jains_fairness.png"), dpi=150)
    plt.close()
    
    # 4. Lifetime Metrics Comparison (Bar Chart)
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    fnd_data = {s: [seed['summary']['FND'] for seed in all_data[s]] for s in strategies}
    hnd_data = {s: [seed['summary']['HND'] for seed in all_data[s]] for s in strategies}
    lnd_data = {s: [seed['summary']['LND'] for seed in all_data[s]] for s in strategies}
    
    x_pos = range(len(strategies))
    
    # FND
    fnd_means = [mean(fnd_data[s]) for s in strategies]
    fnd_stds = [stdev(fnd_data[s]) if len(fnd_data[s]) > 1 else 0 for s in strategies]
    axes[0].bar(x_pos, fnd_means, yerr=fnd_stds, capsize=5, color=[colors.get(s, 'gray') for s in strategies])
    axes[0].set_ylabel("Rounds", fontsize=11)
    axes[0].set_title("First Node Death (FND)", fontsize=12)
    axes[0].set_xticks(x_pos)
    axes[0].set_xticklabels(strategies, rotation=15)
    axes[0].grid(True, alpha=0.3, axis='y')
    
    # HND
    hnd_means = [mean(hnd_data[s]) for s in strategies]
    hnd_stds = [stdev(hnd_data[s]) if len(hnd_data[s]) > 1 else 0 for s in strategies]
    axes[1].bar(x_pos, hnd_means, yerr=hnd_stds, capsize=5, color=[colors.get(s, 'gray') for s in strategies])
    axes[1].set_ylabel("Rounds", fontsize=11)
    axes[1].set_title("Half Node Death (HND)", fontsize=12)
    axes[1].set_xticks(x_pos)
    axes[1].set_xticklabels(strategies, rotation=15)
    axes[1].grid(True, alpha=0.3, axis='y')
    
    # LND
    lnd_means = [mean(lnd_data[s]) for s in strategies]
    lnd_stds = [stdev(lnd_data[s]) if len(lnd_data[s]) > 1 else 0 for s in strategies]
    axes[2].bar(x_pos, lnd_means, yerr=lnd_stds, capsize=5, color=[colors.get(s, 'gray') for s in strategies])
    axes[2].set_ylabel("Rounds", fontsize=11)
    axes[2].set_title("Last Node Death (LND)", fontsize=12)
    axes[2].set_xticks(x_pos)
    axes[2].set_xticklabels(strategies, rotation=15)
    axes[2].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "04_lifetime_metrics_comparison.png"), dpi=150)
    plt.close()

def generate_table(all_data, output_dir):
    """Generate statistical summary table."""
    rows = []
    for strat in sorted(all_data.keys()):
        seeds_data = all_data[strat]
        fnds = [s['summary']['FND'] for s in seeds_data]
        hnds = [s['summary']['HND'] for s in seeds_data]
        lnds = [s['summary']['LND'] for s in seeds_data]
        jains = [s['summary']['avg_jains'] for s in seeds_data]
        
        row = {
            "CH_Strategy": strat,
            "Seeds": len(seeds_data),
            "FND_Mean": round(mean(fnds), 2),
            "FND_Std": round(stdev(fnds) if len(fnds) > 1 else 0, 2),
            "HND_Mean": round(mean(hnds), 2),
            "HND_Std": round(stdev(hnds) if len(hnds) > 1 else 0, 2),
            "LND_Mean": round(mean(lnds), 2),
            "LND_Std": round(stdev(lnds) if len(lnds) > 1 else 0, 2),
            "Fairness_Mean": round(mean(jains), 4),
            "Fairness_Std": round(stdev(jains) if len(jains) > 1 else 0, 4),
        }
        rows.append(row)
    
    with open(os.path.join(output_dir, "summary_statistics.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else [])
        writer.writeheader()
        writer.writerows(rows)

def main():
    output_dir = "master_results_safe"
    os.makedirs(output_dir, exist_ok=True)
    
    num_seeds = 10
    num_rounds = 1000
    num_nodes = 50
    
    print(f"Running Safe Experiments (parameters: {num_nodes} nodes, {num_rounds} rounds, {num_seeds} seeds)")
    print(f"Parameters: DATA_BITS=4000, INITIAL_ENERGY=0.5, CH_PROB=0.05")
    print()
    
    all_data = {}
    strategies = ['deterministic', 'energy_aware', 'random']
    
    for strategy in strategies:
        print(f"\nEvaluating CH Strategy: {strategy}")
        strategy_data = []
        
        for seed in range(num_seeds):
            m, summ = run_single_simulation(strategy, seed, num_rounds, num_nodes)
            strategy_data.append({'seed': seed, 'metrics': m, 'summary': summ})
            
            # Save per-seed metrics
            seed_dir = os.path.join(output_dir, strategy)
            os.makedirs(seed_dir, exist_ok=True)
            with open(os.path.join(seed_dir, f"seed_{seed}.json"), "w") as f:
                json.dump(m, f)
        
        all_data[strategy] = strategy_data
    
    print(f"\n--- Generating Outputs ---")
    plots_dir = os.path.join(output_dir, "plots")
    generate_plots(all_data, plots_dir)
    generate_table(all_data, output_dir)
    
    print(f"✓ Safe experiments complete!")
    print(f"  Output directory: {output_dir}/")
    print(f"  Plots saved to: {plots_dir}/")
    print(f"  Summary table: {output_dir}/summary_statistics.csv")

if __name__ == "__main__":
    main()
