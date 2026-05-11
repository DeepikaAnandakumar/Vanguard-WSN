"""
ASSUMPTIONS FOR EBPT-CRA IMPLEMENTATION

1. Static Nodes:
- Sensor nodes are randomly deployed in a rectangular region.
- Nodes and Base Station (BS) are stationary.
- BS is located at the center of the network.

2. Homogeneous Energy:
- All sensor nodes start with identical initial energy.
- Initial energy E0 = 1.0 Joule.

3. Single Base Station:
- Only one BS exists.
- BS has infinite energy and does not deplete.

4. No Mobility:
- Node positions do not change during simulation.

5. No Packet Loss:
- Communication is deterministic.
- Energy consumption follows first-order radio model.
- No interference, collision, or stochastic loss modeled.

6. Data Generation:
- Each node generates 2500 bits per round.
- Cluster Heads perform data aggregation with 0.4 compression ratio.
"""
