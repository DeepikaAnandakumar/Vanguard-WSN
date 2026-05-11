
import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import argparse

# Ensure we can import run_seed from run_experiments
sys.path.append(os.path.dirname(__file__))
try:
    from run_experiments import run_seed, aggregate
except ImportError:
    # If running from root
    sys.path.append(os.path.join(os.getcwd(), 'scripts'))
    from run_experiments import run_seed, aggregate

def run_sensitivity(out_dir, seeds=5, rounds=600):
    locations = {
        'Center (50, 50)': (50, 50),
        'Corner (0, 0)': (0, 0),
        'External (50, 150)': (50, 150)
    }

    results = {} # Label -> Aggregated Metrics

    print(f"Running Sensitivity Analysis (Seeds={seeds}, Rounds={rounds})...")

    for label, pos in locations.items():
        print(f"\n--- Testing Sink Location: {label} ---")
        label_safe = label.replace(' ', '_').replace('(', '').replace(')', '').replace(',', '')
        run_folder = os.path.join(out_dir, label_safe)
        os.makedirs(run_folder, exist_ok=True)
        
        all_metrics = []
        for s in range(seeds):
            # Using standard params: 50 nodes, 100x100 field
            # We can expose these as args if needed, but keeping standard for sensitivity is fine
            m = run_seed(seed=s, rounds=rounds, num_nodes=50, field_x=100, field_y=100, bs_pos=pos, out_dir=run_folder)
            all_metrics.append(m)
            
        agg = aggregate(all_metrics, rounds)
        results[label] = agg

    # Plotting
    plot_sensitivity(results, out_dir)

def plot_sensitivity(results, out_dir):
    labels = list(results.keys())
    # Extract Last Node Dead (LND) mean and std
    means = []
    stds = []
    
    for label in labels:
        agg = results[label]
        lnd = agg['LND']
        means.append(lnd['mean'] if lnd['mean'] is not None else 0)
        stds.append(lnd['std'] if lnd['std'] is not None else 0)

    x = np.arange(len(labels))
    width = 0.5 

    plt.figure(figsize=(8, 6))
    bars = plt.bar(x, means, width, yerr=stds, capsize=5, color=['#3498db', '#e74c3c', '#9b59b6'], alpha=0.8)
    
    plt.ylabel('Network Lifetime (Last Node Dead)', fontsize=12)
    plt.title('Impact of Sink Location on Network Lifetime', fontsize=14)
    plt.xticks(x, labels, fontsize=11)
    
    # Add values on top
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 5, f"{int(yval)}", ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    
    out_file = os.path.join(out_dir, 'sensitivity_sink_location.png')
    plt.savefig(out_file, dpi=300)
    print(f"\nSaved Sensitivity Plot: {out_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default='master_results_sensitivity')
    parser.add_argument('--seeds', type=int, default=3) # Low seeds for quick verification
    parser.add_argument('--rounds', type=int, default=400) # Enough to kill nodes? Maybe 600 if standard
    args = parser.parse_args()
    
    run_sensitivity(args.out, args.seeds, args.rounds)
