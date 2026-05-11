
import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json

def plot_tradeoff(data_dirs, out_file):
    """
    Plots Fairness Index vs Average Hop Count (Delay Proxy).
    Expects data_dirs to act as labels for different algorithms/configurations.
    
    Args:
        data_dirs: dict mapping { 'Algorithm Label': 'path/to/results/agg_metrics.csv' }
    """
    plt.figure(figsize=(10, 6))
    
    markers = ['o', 's', '^', 'D', 'v', 'p']
    colors = sns.color_palette("husl", len(data_dirs))
    
    for idx, (label, path) in enumerate(data_dirs.items()):
        if not os.path.exists(path):
            print(f"Warning: Path not found: {path} for {label}")
            continue
            
        df = pd.read_csv(path)
        
        # We want a single point per algorithm representing its behavior? 
        # Or a trajectory over rounds?
        # The user requested "Plot all algorithms on one graph." for Trade-off.
        # Usually this is a scatter plot of average performance over the stable period.
        
        # Taking the mean of the metrics over the rounds where the network is alive and stable
        # Filtering rounds where alive_mean > 0
        df_stable = df[df['alive_mean'] > 0]
        
        avg_fairness = df_stable['jain_mean'].mean()
        avg_delay = df_stable['hops_mean'].mean()
        
        marker = markers[idx % len(markers)]
        
        # Scatter point
        plt.scatter(avg_delay, avg_fairness, s=200, label=label, marker=marker, color=colors[idx], edgecolors='k', zorder=5)
        
        # Optional: Add error bars or confidence ellipses if desired, but single point is cleaner for trade-off
        
    plt.xlabel('Average Hop Count (Delay Proxy)', fontsize=12)
    plt.ylabel("Jain's Fairness Index", fontsize=12)
    plt.title('Design Trade-off: Fairness vs Delay', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(title="Algorithm", fontsize=10)
    plt.ylim(0, 1.1) 
    # plt.xlim(left=0) # Let autoscaling handle x-axis but ensure it starts reasonably
    
    # Add annotations for clarity?
    # plt.text(...)
    
    plt.tight_layout()
    plt.savefig(out_file, dpi=300)
    print(f"Saved Trade-off plot to {out_file}")


def plot_stress_lifetime(stress_result_path, out_file):
    """
    Plots Alive Nodes vs Rounds for the stress scenario.
    Expected to show divergence between algorithms if we had multiple.
    Currently we might only have one 'stress' run unless we run multiple config versions.
    
    If passing multiple result paths, we overlay them.
    """
    # For now, let's assume we might overlay multiple stress runs (e.g. diff algorithms)
    # similar to trade-off 
    pass 

def plot_stress_comparison(data_dirs, out_file):
    plt.figure(figsize=(10, 6))
    
    # Linestyles to distinguish
    linestyles = ['-', '--', '-.', ':']
    
    for idx, (label, path) in enumerate(data_dirs.items()):
        if not os.path.exists(path):
            print(f"Warning: Path not found: {path} for {label}")
            continue
            
        df = pd.read_csv(path)
        
        plt.plot(df['round'], df['alive_mean'], label=label, linewidth=2, linestyle=linestyles[idx % len(linestyles)])
        
    plt.xlabel('Round', fontsize=12)
    plt.ylabel('Alive Nodes', fontsize=12)
    plt.title('Network Lifetime under Stress Scenario', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_file, dpi=300)
    print(f"Saved Stress Lifetime plot to {out_file}")

# For verification/demo purposes, we'll allow running this on existing results
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--tradeoff-out', default='tradeoff_plot.png')
    parser.add_argument('--stress-out', default='stress_lifetime.png')
    
    # We expect arguments like --algo1 name=path --algo2 name=path ...
    # But simpler: --inputs name1=path1 name2=path2 ...
    parser.add_argument('--inputs', nargs='+', help="List of inputs in format Name=Path/to/agg_metrics.csv")
    
    args = parser.parse_args()
    
    if args.inputs:
        inputs = {}
        for item in args.inputs:
            k, v = item.split('=', 1)
            inputs[k] = v
            
        plot_tradeoff(inputs, args.tradeoff_out)
        plot_stress_comparison(inputs, args.stress_out)
    else:
        print("Please provide inputs via --inputs Name=Path/To/Csv ...")
