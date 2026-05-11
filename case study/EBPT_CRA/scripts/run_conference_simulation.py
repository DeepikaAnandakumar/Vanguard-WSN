
import os
import sys
import json
import csv
import matplotlib.pyplot as plt
from statistics import mean

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.network import Network
import core.params as params

def run_simulation(strategy_name, num_nodes, rounds, seed=42):
    print(f"Running simulation for strategy: {strategy_name}")
    import random
    random.seed(seed)
    
    net = Network(n=num_nodes, field_x=100, field_y=100, bs_pos=(50, 50))
    net.controller.routing_strategy = strategy_name
    net.build()
    
    metrics = {
        "rounds": [],
        "alive": [],
        "energy": [],
        "fairness": []
    }
    
    for r in range(rounds):
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
            
    return metrics

def save_conference_results(results, output_dir="final_results"):
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Save Raw Data
    with open(os.path.join(output_dir, "raw_data.json"), "w") as f:
        json.dump(results, f, indent=4)
        
    # 2. Generate Plots
    strategies = list(results.keys())
    
    # Plot 1: Alive Nodes (Lifetime)
    plt.figure(figsize=(10, 6))
    for strat in strategies:
        plt.plot(results[strat]["rounds"], results[strat]["alive"], label=strat)
    plt.xlabel("Rounds")
    plt.ylabel("Alive Nodes")
    plt.title("Network Lifetime Comparison")
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, "network_lifetime.png"))
    plt.close()
    
    # Plot 2: Total Residual Energy
    plt.figure(figsize=(10, 6))
    for strat in strategies:
        plt.plot(results[strat]["rounds"], results[strat]["energy"], label=strat)
    plt.xlabel("Rounds")
    plt.ylabel("Total Residual Energy (J)")
    plt.title("Energy Consumption Comparison")
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, "total_energy.png"))
    plt.close()
    
    # Plot 3: Jain's Fairness Index
    plt.figure(figsize=(10, 6))
    for strat in strategies:
        plt.plot(results[strat]["rounds"], results[strat]["fairness"], label=strat)
    plt.xlabel("Rounds")
    plt.ylabel("Jain's Fairness Index")
    plt.title("Load Balancing Fairness Comparison")
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, "fairness_index.png"))
    plt.close()
    
    # 3. Save Summary Table
    with open(os.path.join(output_dir, "summary_table.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Strategy", "FND (First Node Death)", "LND (Last Node Death)", "Avg Fairness"])
        
        for strat in strategies:
            rounds = results[strat]["rounds"]
            alive = results[strat]["alive"]
            fairness = results[strat]["fairness"]
            
            # Estimate FND
            fnd = next((r for r, a in zip(rounds, alive) if a < alive[0]), "N/A")
            lnd = rounds[-1] if alive[-1] == 0 else "Alive"
            avg_fair = mean(fairness)
            
            writer.writerow([strat, fnd, lnd, f"{avg_fair:.4f}"])

if __name__ == "__main__":
    strategies = ["EBPT", "TRAFFIC_AWARE", "QOS"]
    all_results = {}
    
    # Configuration
    NUM_NODES = 50
    ROUNDS = 200 # Increased rounds to see full lifetime
    
    for strat in strategies:
        all_results[strat] = run_simulation(strat, NUM_NODES, ROUNDS)
        
    save_conference_results(all_results)
    print("Conference results generated in 'final_results/'")
