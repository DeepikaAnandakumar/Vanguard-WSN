
import os
import json
import matplotlib.pyplot as plt
import numpy as np

RESULTS_DIR = 'paper_results'
OUTPUT_DIR = 'submission_paper/paper_assets'
os.makedirs(OUTPUT_DIR, exist_ok=True)

metrics_map = {
    'Vanguard': {'label': 'Vanguard-WSN', 'color': 'red', 'style': '-'},
    'LEACH-MultiHop': {'label': 'LEACH (Baseline)', 'color': 'blue', 'style': '--'},
    'HEED-MultiHop': {'label': 'HEED', 'color': 'green', 'style': '-.'},
    'PEGASIS': {'label': 'PEGASIS', 'color': 'orange', 'style': ':'}
}

def load_data():
    data = {}
    for name in metrics_map.keys():
        path = os.path.join(RESULTS_DIR, f"{name}.json")
        if os.path.exists(path):
            with open(path, 'r') as f:
                raw = json.load(f)
                data[name] = raw
    return data

def average_metrics(raw_data):
    """Averages list of dicts into single dict of lists"""
    avg_data = {}
    for name, seed_list in raw_data.items():
        if not seed_list: continue
        
        # Assume all seeds have same max rounds for simplicity, or handle different lengths
        # We'll use the length of the first seed as reference or max length
        max_len = max(len(s['rounds']) for s in seed_list)
        
        avg_metrics = {
            'rounds': [],
            'alive': [],
            'energy': [],
            'throughput': []
        }
        
        for r_idx in range(max_len):
            r_val = r_idx # Assuming continuous rounds
            alive_sum = 0
            energy_sum = 0
            through_sum = 0
            count = 0
            
            for seed in seed_list:
                if r_idx < len(seed['rounds']):
                    alive_sum += seed['alive'][r_idx]
                    energy_sum += seed['energy'][r_idx]
                    through_sum += seed['throughput'][r_idx] # This is per-round
                    count += 1
                else:
                    # Simulation ended (dead), assume 0 alive, 0 energy? 
                    # If dead, energy might be residual (non-zero) or 0.
                    # Use last value? No, assume consistency.
                    pass
            
            if count > 0:
                avg_metrics['rounds'].append(r_val)
                avg_metrics['alive'].append(alive_sum / count)
                avg_metrics['energy'].append(energy_sum / count)
                avg_metrics['throughput'].append(through_sum / count)
                
        # Cummulative throughput
        avg_metrics['throughput_cum'] = np.cumsum(avg_metrics['throughput']).tolist()
        
        avg_data[name] = avg_metrics
    return avg_data

def plot_lifetime(avg_data):
    plt.figure(figsize=(10, 6))
    for name, data in avg_data.items():
        props = metrics_map.get(name, {})
        plt.plot(data['rounds'], data['alive'], 
                 label=props.get('label', name),
                 color=props.get('color'),
                 linestyle=props.get('style'),
                 linewidth=2)
                 
    plt.xlabel('Rounds')
    plt.ylabel('Number of Alive Nodes')
    plt.title('Network Lifetime Comparison')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'lifetime_comparison.png'), dpi=300)
    plt.close()

def plot_energy(avg_data):
    plt.figure(figsize=(10, 6))
    for name, data in avg_data.items():
        props = metrics_map.get(name, {})
        plt.plot(data['rounds'], data['energy'], 
                 label=props.get('label', name),
                 color=props.get('color'),
                 linestyle=props.get('style'),
                 linewidth=2)
                 
    plt.xlabel('Rounds')
    plt.ylabel('Total Residual Energy (J)')
    plt.title('Energy Consumption over Time')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'energy_comparison.png'), dpi=300)
    plt.close()

def plot_throughput(avg_data):
    plt.figure(figsize=(10, 6))
    for name, data in avg_data.items():
        props = metrics_map.get(name, {})
        plt.plot(data['rounds'], data['throughput_cum'], 
                 label=props.get('label', name),
                 color=props.get('color'),
                 linestyle=props.get('style'),
                 linewidth=2)
                 
    plt.xlabel('Rounds')
    plt.ylabel('Total Data Packets Received (bits)')
    plt.title('Network Throughput')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'throughput_comparison.png'), dpi=300)
    plt.close()

def main():
    raw = load_data()
    if not raw:
        print("No data found in", RESULTS_DIR)
        return
        
    avg = average_metrics(raw)
    
    plot_lifetime(avg)
    plot_energy(avg)
    plot_throughput(avg)
    
    print(f"Plots saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
