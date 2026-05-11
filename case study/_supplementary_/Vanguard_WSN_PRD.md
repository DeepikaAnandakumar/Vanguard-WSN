# Product Requirements Document (PRD)
**Project Name:** Vanguard-WSN (Utility-Driven Energy-Balanced Routing Protocol)  
**Version:** 1.0  
**Status:** Final  
**Date:** February 11, 2026  

---

## 1. Executive Summary
Vanguard-WSN is an advanced routing protocol designed for Wireless Sensor Networks (WSNs). It aims to solve the critical "Energy Hole Problem" where nodes near the Base Station (BS) die prematurely due to excessive relaying traffic. By introducing a utility-based Cluster Head (CH) selection mechanism and an adaptive inter-cluster routing algorithm, Vanguard-WSN significantly extends network longevity compared to legacy protocols like LEACH and HEED.

## 2. Problem Statement
*   **The Energy Hole:** In multi-hop WSNs, nodes closer to the sink carry a disproportionately high traffic load, leading to early depletion.
*   **Inefficient Clustering:** Existing probabilistic selection (e.g., LEACH) ignores residual energy and local density, choosing weak nodes as leaders.
*   **Static Routing:** Fixed routing paths fail to adapt to dynamic energy changes in the network topology.

## 3. Goals & Objectives
*   **Maximize Stability Period:** Extend the First Node Death (FND) epoch by at least 40% compared to LEACH-MultiHop.
*   **Load Balancing:** Distribute energy consumption evenly across the network field.
*   **Scalability:** Support dense deployments ($N=100+$ nodes) without significant degradation in control overhead.
*   **Theoretical Rigor:** Benchmark performance against a mathematically derived Linear Programming (LP) upper bound.

## 4. Key Features
### 4.1 Utility-Based CH Selection
*   **Description:** Deterministic selection of Cluster Heads based on a composite "Utility" score.
*   **Formula:** $U_i = \alpha (E_{res}/E_{max}) + \beta (1/(1+\text{deg}))$.
*   **Customer Benefit:** Ensures only the fittest nodes (high energy, optimal density) become leaders.

### 4.2 Energy-Balanced Path Tree (EBPT)
*   **Description:** Dynamic construction of a routing tree rooted at the BS.
*   **Mechanism:** Routes are chosen based on a cost function that penalizes low-energy nodes, adjustable via an aging factor $\lambda$.
*   **Customer Benefit:** Prevents the formation of hotspots and bypasses dying nodes automatically.

### 4.3 Theoretical "God Line" Benchmark
*   **Description:** A linear programming formulation to calculate the absolute theoretical maximum lifetime.
*   **Customer Benefit:** Provides a verifiable standard to measure protocol efficiency (Optimality Gap).

## 5. Technical Requirements
*   **Simulation Environment:** Python 3.9+ (Custom Discrete Event Simulator).
*   **Energy Model:** First-Order Radio Model ($E_{elec}=50nJ/bit$, $\epsilon_{fs}=10pJ/bit/m^2$).
*   **Network Topology:** $100m \times 100m$ field, Centroid Base Station.
*   **Traffic Model:** Constant Bit Rate (CBR), periodic data aggregation.

## 6. Success Metrics (KPIs)
| Metric | Target Value | Measured Value (v1.0) | Status |
| :--- | :--- | :--- | :--- |
| **First Node Death (FND)** | > 150 Rounds | 165 Rounds | ✅ Passed |
| **Improvement vs LEACH** | > 40% | +54.2% | ✅ Passed |
| **Network Throughput** | > 1.5x LEACH | ~1.8x | ✅ Passed |
| **Comp. Complexity** | $O(N)$ per round | $O(N)$ | ✅ Passed |

## 7. Assumptions & Constraints
*   Nodes are stationary after deployment.
*   Base Station has unlimited power and computational resources.
*   Links are symmetric and nodes are location-aware (via GPS or RSSI).

## 8. Future Roadmap
*   **v1.1:** Mobile Sink support to further distribute load.
*   **v1.2:** Hardware implementation on ZigBee/LoRa modules.
*   **v2.0:** Machine Learning-based prediction for $\lambda$ parameter tuning.
