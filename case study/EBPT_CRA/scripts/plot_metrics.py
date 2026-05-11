"""Plot metrics produced by main.py

Generates:
 - results/energy_vs_rounds.png
 - results/alive_vs_rounds.png

Also prints a short numeric table (FND, HND, LND).
"""
import os, json
import sys
try:
    import matplotlib.pyplot as plt
except Exception as e:
    print('matplotlib not installed. Install with `pip install matplotlib`')
    raise

METRICS_FILE = os.path.join('results', 'metrics.json')
if not os.path.exists(METRICS_FILE):
    print('No metrics file found at', METRICS_FILE)
    sys.exit(1)

with open(METRICS_FILE, 'r') as f:
    m = json.load(f)

rounds = m.get('rounds', list(range(len(m.get('alive_nodes', [])))))
alive = m.get('alive_nodes', [])
total_energy = m.get('total_energy', [])

# Ensure lengths match the rounds list
if len(rounds) != len(alive):
    rounds = list(range(len(alive)))

os.makedirs('results', exist_ok=True)

# Energy vs rounds
plt.figure()
plt.plot(rounds, total_energy, marker='o')
plt.xlabel('Round')
plt.ylabel('Total Residual Energy (J)')
plt.title('Total Energy vs Rounds')
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join('results','energy_vs_rounds.png'))
print('Wrote results/energy_vs_rounds.png')

# Alive nodes vs rounds
plt.figure()
plt.plot(rounds, alive, marker='o')
plt.xlabel('Round')
plt.ylabel('Alive Nodes')
plt.title('Alive Nodes vs Rounds')
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join('results','alive_vs_rounds.png'))
print('Wrote results/alive_vs_rounds.png')

# Print numeric summary
print('\n--- Numerical Summary ---')
print('FND:', m.get('first_node_death'))
print('HND:', m.get('half_node_death'))
print('LND / Network Lifetime:', m.get('last_node_death'))

# Quick sanity checks and guidance
if not total_energy:
    print('\nWARNING: total_energy is empty. Ensure `network.log_metrics` is called each round.')
if not alive:
    print('\nWARNING: alive_nodes is empty. Ensure metrics are being logged correctly.')

print('\nDone.')