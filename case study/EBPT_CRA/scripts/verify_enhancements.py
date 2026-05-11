
import os
import sys
# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import shutil
from core.network import Network
from core.controller import Controller
import core.params as params

def run_test(strategy_name, rounds=10):
    print(f"--- Running Verification for Strategy: {strategy_name} ---")
    
    # Create Network
    net = Network(n=20, field_x=100, field_y=100, bs_pos=(50, 50))
    
    # Configure Controller Strategy
    net.controller.routing_strategy = strategy_name
    
    net.build()
    
    for r in range(rounds):
        # Re-build network to adapt to new Load/Energy states (Dynamic Routing)
        net.controller.build_network()
        
        net.run_round()
        net.log_metrics(r)
        
        if net.alive_nodes() == 0:
            print("All nodes dead early.")
            break
            
    # Check Metrics
    last_jain = net.metrics.jains_index[-1] if net.metrics.jains_index else 0
    alive = net.alive_nodes()
    
    # Analyze Load Distribution
    loads = [n.load for n in net.nodes if net._is_alive(n)]
    # Filter out leaf nodes (0 load) to see fairness among relay nodes? 
    # Or just print raw to show user why J is low.
    relay_loads = [l for l in loads if l > 0]
    
    print(f"Strategy: {strategy_name}, Rounds: {rounds}, Alive: {alive}, Last Jain Index: {last_jain:.4f}")
    print(f"Loads (Top 10): {sorted(loads, reverse=True)[:10]} ...")
    print(f"Relay Nodes: {len(relay_loads)} / {len(loads)}")
    
    if len(net.metrics.jains_index) > 0:
         print("SUCCESS: Fairness Index recorded.")
    else:
         print("FAILURE: No Fairness Index recorded.")
         
    return net.metrics

if __name__ == "__main__":
    ROUNDS = 20
    # Test 1: EBPT (with Load Balancing)
    run_test("EBPT", ROUNDS)
    
    # Test 2: Traffic Aware
    run_test("TRAFFIC_AWARE", ROUNDS)
    
    # Test 3: QoS
    run_test("QOS", ROUNDS)
    
    print("\nVerification Complete.")
