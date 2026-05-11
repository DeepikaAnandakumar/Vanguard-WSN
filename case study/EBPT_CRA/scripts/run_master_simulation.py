
import os
import sys
import json
import csv
import argparse
import matplotlib.pyplot as plt
from statistics import mean, stdev

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.network import Network
import core.params as params

ALGORITHMS = [
    "EBPT",
    "EBPT_LOAD_BALANCED",
    "TRAFFIC_AWARE",
    "QOS"
]

# Map algorithm names to folder names
ALGO_FOLDER_MAP = {
    "EBPT": "ebpt",
    "EBPT_LOAD_BALANCED": "load_balanced",
    "TRAFFIC_AWARE": "traffic_aware",
    "QOS": "qos"
}

# Map algorithm names to display names for plots
ALGO_DISPLAY_MAP = {
    "EBPT": "EBPT",
    "EBPT_LOAD_BALANCED": "Load Balanced",
    "TRAFFIC_AWARE": "Traffic Aware",
    "QOS": "QoS"
}

def run_single_simulation(algorithm, seed, config, ch_strategy="deterministic"):
    print(f"  [Algorithm: {algorithm}] [CH: {ch_strategy}] Seed: {seed} Started...")
    import random
    random.seed(seed)
    
    # Override params if specified
    if config.get('data_bits') is not None:
        params.DATA_BITS = config['data_bits']
    if config.get('initial_energy') is not None:
        params.INITIAL_ENERGY = config['initial_energy']
    
    net = Network(n=config['nodes'], field_x=100, field_y=100, bs_pos=(50, 50))
    # Override Energy if needed (use config energy or params)
    energy_val = config.get('energy') or config.get('initial_energy') or params.INITIAL_ENERGY
    for n in net.nodes:
        n.initial_energy = energy_val
        n.energy = energy_val
        
    net.controller.routing_strategy = algorithm
    net.controller.ch_strategy = ch_strategy  # Pass CH strategy
    net.build()
    
    metrics = {
        "rounds": [],
        "alive": [],
        "energy": [],
        "fairness": [],
        "hop_count": [] # TODO: Hop count metric
    }
    
    for r in range(config['rounds']):
        # Dynamic Rebuilding for Load Balancing
        net.controller.build_network()
        
        net.run_round()
        net.log_metrics(r)
        
        metrics["rounds"].append(r)
        metrics["alive"].append(net.alive_nodes())
        metrics["energy"].append(sum(n.energy for n in net.nodes if net._is_alive(n)))
        
        jain = net.metrics.jains_index[-1] if net.metrics.jains_index else 0
        metrics["fairness"].append(jain)
        
        if net.alive_nodes() == 0:
            break
            
    # Calculate Lifetime Metrics
    fnd = next((r for r, a in zip(metrics["rounds"], metrics["alive"]) if a < config['nodes']), metrics["rounds"][-1])
    # HND: < 50% nodes
    hnd = next((r for r, a in zip(metrics["rounds"], metrics["alive"]) if a <= config['nodes']/2), metrics["rounds"][-1])
    lnd = metrics["rounds"][-1] if metrics["alive"][-1] == 0 else "Alive"
    if lnd == "Alive": lnd = config['rounds'] # Treat survival as max rounds
    
    # Calculate steady-state fairness (only after FND)
    # Fairness before FND is artificially high (all nodes alive)
    if metrics["fairness"] and fnd < len(metrics["fairness"]):
        steady_state_fairness = mean(metrics["fairness"][fnd:])
    else:
        steady_state_fairness = mean(metrics["fairness"]) if metrics["fairness"] else 0
    
    print(f"  [Algorithm: {algorithm}] [CH: {ch_strategy}] Seed: {seed} Finished. FND: {fnd}, LND: {lnd}")
    
    summary = {
        "FND": fnd,
        "HND": hnd,
        "LND": lnd,
        "avg_fairness": steady_state_fairness
    }
    
    return metrics, summary

def generate_comparative_plots(all_data, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    # We need to average metrics across seeds for plotting
    strategies = list(all_data.keys())
    
    # 1. Alive Nodes Comparison
    plt.figure(figsize=(10, 6))
    for strat in strategies:
        # Average alive curves
        seeds_data = all_data[strat]
        # Align lengths (fill with 0 if ended early? or stop at min length?)
        # Let's assume all ran to max rounds or death. Death = 0 alive.
        # We need to compute mean per round.
        rounds_set = sorted(list(set(r for seed in seeds_data for r in seed['metrics']['rounds'])))
        avg_alive = []
        for r in rounds_set:
            path_vals = []
            for seed in seeds_data:
                m = seed['metrics']
                if r in m['rounds']:
                    idx = m['rounds'].index(r)
                    path_vals.append(m['alive'][idx])
                else:
                    path_vals.append(0) # Assumed dead if not in rounds
            avg_alive.append(mean(path_vals))
            
        display_name = ALGO_DISPLAY_MAP.get(strat, strat)
        plt.plot(rounds_set, avg_alive, label=display_name)

    plt.xlabel("Rounds")
    plt.ylabel("Alive Nodes")
    plt.title(f"Network Lifetime Comparison (Avg of {len(seeds_data)} seeds)")
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, "alive_compare.png"))
    plt.close()
    
    # 2. Energy Comparison
    plt.figure(figsize=(10, 6))
    for strat in strategies:
        seeds_data = all_data[strat]
        rounds_set = sorted(list(set(r for seed in seeds_data for r in seed['metrics']['rounds'])))
        avg_energy = []
        for r in rounds_set:
            path_vals = []
            for seed in seeds_data:
                m = seed['metrics']
                if r in m['rounds']:
                    idx = m['rounds'].index(r)
                    path_vals.append(m['energy'][idx])
                else:
                    path_vals.append(0) 
            avg_energy.append(mean(path_vals))
            
        display_name = ALGO_DISPLAY_MAP.get(strat, strat)
        plt.plot(rounds_set, avg_energy, label=display_name)

    plt.xlabel("Rounds")
    plt.ylabel("Total Energy (J)")
    plt.title("Energy Consumption Comparison")
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, "energy_compare.png"))
    plt.close()

    # 3. Fairness Comparison
    plt.figure(figsize=(10, 6))
    for strat in strategies:
        # Fairness
        seeds_data = all_data[strat]
        rounds_set = sorted(list(set(r for seed in seeds_data for r in seed['metrics']['rounds'])))
        avg_fair = []
        for r in rounds_set:
            path_vals = []
            for seed in seeds_data:
                m = seed['metrics']
                if r in m['rounds']:
                    idx = m['rounds'].index(r)
                    path_vals.append(m['fairness'][idx])
                else:
                    path_vals.append(0)
            avg_fair.append(mean(path_vals))
            
        display_name = ALGO_DISPLAY_MAP.get(strat, strat)
        plt.plot(rounds_set, avg_fair, label=display_name)

    plt.xlabel("Rounds")
    plt.ylabel("Jain's Fairness Index")
    plt.title("Fairness Comparison")
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, "fairness_compare.png"))
    plt.close()

def generate_statistical_table(all_data, output_dir):
    rows = []
    for strat, seeds_data in all_data.items():
        # collect summaries
        fnds = [s['summary']['FND'] for s in seeds_data]
        lnds = [s['summary']['LND'] for s in seeds_data]
        fairs = [s['summary']['avg_fairness'] for s in seeds_data]
        
        # Use display name for table
        display_name = ALGO_DISPLAY_MAP.get(strat, strat)
        row = {
            "Algorithm": display_name,
            "FND_Mean": mean(fnds), "FND_Std": stdev(fnds) if len(fnds)>1 else 0,
            "LND_Mean": mean(lnds), "LND_Std": stdev(lnds) if len(lnds)>1 else 0,
            "Fairness_Mean": mean(fairs), "Fairness_Std": stdev(fairs) if len(fairs)>1 else 0
        }
        rows.append(row)
        
    with open(os.path.join(output_dir, "statistical_validation.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Algorithm", "FND_Mean", "FND_Std", "LND_Mean", "LND_Std", "Fairness_Mean", "Fairness_Std"
        ])
        writer.writeheader()
        writer.writerows(rows)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--nodes', type=int, default=50) # Range: 50, 100, 150
    parser.add_argument('--rounds', type=int, default=1000) # Req: 1000+
    parser.add_argument('--seeds', type=int, default=10) # Req: >= 10
    parser.add_argument('--energy', type=float, default=None, help='Override energy (deprecated, use --initial-energy)')
    parser.add_argument('--initial-energy', type=float, default=None, help='Override INITIAL_ENERGY for experiments')
    parser.add_argument('--data-bits', type=int, default=None, help='Override DATA_BITS for experiments')
    parser.add_argument('--out', type=str, default='master_results', help='Output directory')
    args = parser.parse_args()
    
    config = vars(args)
    # Use initial_energy if provided, otherwise fall back to energy
    if config.get('initial_energy') is None and config.get('energy') is not None:
        config['initial_energy'] = config['energy']
    
    # CLI Safety Checks
    warnings = []
    if config.get('data_bits') and config['data_bits'] > 100000:
        warnings.append(f"⚠ WARNING: DATA_BITS={config['data_bits']} is very large (>100k). Network will likely die within a few rounds.")
    if config.get('initial_energy') and config['initial_energy'] < 0.01:
        warnings.append(f"⚠ WARNING: INITIAL_ENERGY={config['initial_energy']} is very small (<0.01 J). Nodes will die almost immediately.")
    if config.get('initial_energy') and config['initial_energy'] > 100:
        warnings.append(f"⚠ WARNING: INITIAL_ENERGY={config['initial_energy']} is very large (>100 J). Simulation may run for excessive rounds.")
    
    if warnings:
        print("\n".join(warnings))
        try:
            ans = input("\nProceed anyway? [y/N]: ").strip().lower()
            if ans not in ('y', 'yes'):
                print("Aborted by user.")
                return
        except KeyboardInterrupt:
            print("\nAborted by user.")
            return
    
    print("Starting Master Simulation with config:", config)
    if config.get('data_bits'):
        print(f'Overriding DATA_BITS -> {config["data_bits"]}')
    if config.get('initial_energy'):
        print(f'Overriding INITIAL_ENERGY -> {config["initial_energy"]}')
    
    output_dir = args.out
    os.makedirs(output_dir, exist_ok=True)
    
    all_data = {}
    
    for algo in ALGORITHMS:
        print(f"\nEvaluating Algorithm: {algo}")
        algo_data = []
        # Use folder mapping
        folder_name = ALGO_FOLDER_MAP.get(algo, algo.lower())
        algo_dir = os.path.join(output_dir, folder_name)
        os.makedirs(algo_dir, exist_ok=True)
        
        for s in range(args.seeds):
            m, summ = run_single_simulation(algo, s, config)
            algo_data.append({'seed': s, 'metrics': m, 'summary': summ})
            
            # Save per-seed metrics
            with open(os.path.join(algo_dir, f"seed_{s}.json"), "w") as f:
                json.dump(m, f)
                
        all_data[algo] = algo_data
        
    print("\n--- Generating Final Comparative Outputs ---")
    generate_comparative_plots(all_data, os.path.join(output_dir, "comparison"))
    generate_statistical_table(all_data, os.path.join(output_dir, "comparison"))
    
    print(f"Master Simulation Complete. Check '{output_dir}/'")

if __name__ == "__main__":
    main()
