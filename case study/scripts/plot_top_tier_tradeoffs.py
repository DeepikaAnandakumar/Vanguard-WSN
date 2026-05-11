import json
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def plot_tradeoffs(results_dir='top_tier_results'):
    """
    Plot FND vs Fairness trade-offs from top-tier results.
    """
    comp_file = f'{results_dir}/comprehensive_results.json'
    if not os.path.exists(comp_file):
        # Fallback to individual node files if comprehensive not ready
        node_file = f'{results_dir}/results_50nodes.json'
        if not os.path.exists(node_file):
            print("No results found to plot.")
            return
        with open(node_file, 'r') as f:
            data = {'experiments': {'50_nodes': json.load(f)}}
    else:
        with open(comp_file, 'r') as f:
            data = json.load(f)

    plt.figure(figsize=(10, 6))
    
    for size_key, size_data in data['experiments'].items():
        names = []
        fnds = []
        fairnesses = []
        
        for name, stats in size_data.items():
            names.append(name)
            fnds.append(stats['fnd_mean'])
            fairnesses.append(stats['fairness_mean'])
            
            # Error bars
            plt.errorbar(stats['fairness_mean'], stats['fnd_mean'], 
                        yerr=stats.get('fnd_std', 0), 
                        xerr=stats.get('fairness_std', 0),
                        fmt='o', alpha=0.5, label=None)

        # Main scatter points
        sns.scatterplot(x=fairnesses, y=fnds, hue=names, s=100)

    plt.title("EBPT-CRA: Lifetime vs Fairness Trade-off")
    plt.xlabel("Jain's Fairness Index")
    plt.ylabel("First Node Death (FND) [Rounds]")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    plt.savefig('top_tier_tradeoff_plot.png')
    print("Plot saved to top_tier_tradeoff_plot.png")

if __name__ == '__main__':
    plot_tradeoffs()
