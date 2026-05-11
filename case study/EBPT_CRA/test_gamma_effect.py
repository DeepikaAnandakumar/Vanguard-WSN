#!/usr/bin/env python3
"""Quick test to verify gamma parameter has effect on tree structure"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from core.network import Network
from core.controller import Controller
import random

# Create two identical networks
random.seed(42)
net1 = Network(n=20, field_x=100, field_y=100, bs_pos=(50, 50))
net1.controller = Controller(net1, routing_strategy="EBPT", gamma=0.0)
net1.build()

random.seed(42)  # Same seed
net2 = Network(n=20, field_x=100, field_y=100, bs_pos=(50, 50))
net2.controller = Controller(net2, routing_strategy="EBPT", gamma=1.0)
net2.build()

# Compare tree structures
print("Gamma=0.0 tree structure:")
loads_g0 = {}
for n in net1.nodes:
    if n.parent and n.parent.id != 'BS':
        pid = n.parent.id
        loads_g0[pid] = loads_g0.get(pid, 0) + 1

for pid, load in sorted(loads_g0.items()):
    print(f"  Node {pid}: {load} children")

print("\nGamma=1.0 tree structure:")
loads_g1 = {}
for n in net2.nodes:
    if n.parent and n.parent.id != 'BS':
        pid = n.parent.id
        loads_g1[pid] = loads_g1.get(pid, 0) + 1

for pid, load in sorted(loads_g1.items()):
    print(f"  Node {pid}: {load} children")

# Check if structures differ
if loads_g0 != loads_g1:
    print("\n✓ Trees are DIFFERENT - gamma is working!")
else:
    print("\n✗ Trees are IDENTICAL - gamma has no effect")

# Check max load
max_load_g0 = max(loads_g0.values()) if loads_g0 else 0
max_load_g1 = max(loads_g1.values()) if loads_g1 else 0
print(f"\nMax children per node:")
print(f"  Gamma=0.0: {max_load_g0}")
print(f"  Gamma=1.0: {max_load_g1}")
if max_load_g1 < max_load_g0:
    print("✓ Gamma=1.0 produces more balanced tree (lower max load)")

