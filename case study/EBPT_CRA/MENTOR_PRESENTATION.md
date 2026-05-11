# EBPT Project — Mentor Presentation Guide

> **Purpose:** Step-by-step guide to run the project, interpret graphs, and present key results.

---

## 1. Project Overview

**EBPT (Energy-Balanced Path-Based Routing)** for Wireless Sensor Networks with Cluster-Rotating Architecture (CRA).

**Algorithms Compared:**
| Algorithm | Description |
|-----------|-------------|
| **EBPT** | Energy-balanced path selection |
| **Load Balanced** | EBPT + load-aware forwarding |
| **Traffic Aware** | EBPT + traffic-aware relay selection |
| **QoS** | Shortest-path (min-hop) routing — stress scenario |

**Key Question:** Does EBPT maintain fairness when QoS (strict shortest-path) routing is applied?

---

## 2. Prerequisites

- **Python 3.8+**
- **Dependencies:** `matplotlib`, `numpy` (standard scientific Python stack)

To install if needed:
```bash
pip install matplotlib numpy
```

---

## 3. How to Run the Project

### Step 1 — Navigate to Project Root
```bash
cd "d:\SEM 6\CNproject\EBPT_CRA"
```

### Step 2 — Run Master Simulation (Full Experiment)

This runs **4 algorithms × 10 seeds** and generates all comparison graphs:

```bash
python scripts/run_master_simulation.py --seeds 10 --rounds 800 --data-bits 10000 --initial-energy 0.40 --out master_results_final_strong
```

**Parameters Explained:**
| Parameter | Value | Meaning |
|-----------|-------|---------|
| `--seeds` | 10 | Number of random seeds for statistical validity |
| `--rounds` | 800 | Simulation rounds (until network dies or max reached) |
| `--data-bits` | 10000 | Data payload per round (bits) |
| `--initial-energy` | 0.40 | Initial energy per node (Joules) |
| `--out` | master_results_final_strong | Output folder name |

### Step 3 — Output Location

Results are written to:
```
master_results_final_strong/
├── ebpt/          ← per-seed JSON metrics
├── load_balanced/
├── traffic_aware/
├── qos/
└── comparison/    ← GRAPHS AND TABLES
    ├── alive_compare.png
    ├── energy_compare.png
    ├── fairness_compare.png
    └── statistical_validation.csv
```

**Typical runtime:** ~5–15 minutes depending on hardware.

---

## 4. Graph Interpretation — What Each Plot Shows

### 4.1 `alive_compare.png` — Network Lifetime

**X-axis:** Rounds  
**Y-axis:** Number of alive nodes

**What to say:**
- All curves start at 50 (all nodes alive).
- **QoS** (shortest-path) curve drops first → first node death (FND) happens earlier (~round 11 vs ~round 20 for EBPT).
- QoS curve reaches zero faster → shorter Last Node Death (LND).
- EBPT, Load Balanced, and Traffic Aware overlap because they share the same energy-balanced path construction — only QoS uses different (shortest-path) routing.

**Takeaway:** QoS reduces network lifetime; EBPT-based algorithms extend it.

---

### 4.2 `energy_compare.png` — Total Energy Consumption

**X-axis:** Rounds  
**Y-axis:** Total energy remaining in network (Joules)

**What to say:**
- Curves show total energy left across all alive nodes.
- **QoS** depletes energy faster → steeper slope.
- EBPT-based algorithms consume energy more evenly, so total energy lasts longer.
- This supports the claim that energy-aware routing distributes load better and prolongs network life.

**Takeaway:** QoS concentrates traffic → faster energy drain; EBPT spreads it.

---

### 4.3 `fairness_compare.png` — Jain’s Fairness Index

**X-axis:** Rounds  
**Y-axis:** Jain’s Fairness Index (0 = unfair, 1 = perfectly fair)

**What to say:**
- Fairness measures how evenly energy is consumed across nodes.
- All algorithms stay **high** (≈0.97) — fairness does **not** collapse.
- QoS is slightly lower (~0.97 vs ~0.96) but still good.
- The important point: **fairness does not collapse** under QoS because the underlying path construction is still energy-aware; QoS only changes relay selection, not the fundamental path structure.

**Takeaway:** EBPT maintains high fairness even under QoS stress. This is the main robustness result.

---

## 5. Statistical Table — `statistical_validation.csv`

| Algorithm | FND Mean | LND Mean | Fairness Mean |
|-----------|----------|----------|---------------|
| EBPT | 20.1 | 613.3 | 0.977 |
| Load Balanced | 20.1 | 613.3 | 0.977 |
| Traffic Aware | 20.1 | 613.3 | 0.977 |
| QoS | 10.9 | 560.1 | 0.966 |

**Metrics:**
- **FND (First Node Death):** Round when first node dies — earlier = worse.
- **LND (Last Node Death):** Round when last node dies — higher = longer lifetime.
- **Fairness:** Steady-state Jain’s index (after FND) — higher = more balanced.

---

## 6. Key Messages for Mentor

1. **Main result:** EBPT maintains high fairness (~0.97) even when QoS (shortest-path) routing is applied, at the cost of reduced network lifetime.
2. **Robustness:** Energy-balanced path construction prevents fairness collapse.
3. **Methodology:** 10 seeds, steady-state fairness (post-FND), standard first-order radio model.
4. **Conservative claim:** Not “QoS is unfair” — rather “EBPT remains fair under QoS stress.”

---

## 7. Quick Demo Commands (Copy-Paste)

```bash
# Navigate
cd "d:\SEM 6\CNproject\EBPT_CRA"

# Run full experiment (uses same config as final paper)
python scripts/run_master_simulation.py --seeds 10 --rounds 800 --data-bits 10000 --initial-energy 0.40 --out master_results_final_strong

# View results
# Open: master_results_final_strong/comparison/alive_compare.png
# Open: master_results_final_strong/comparison/energy_compare.png
# Open: master_results_final_strong/comparison/fairness_compare.png
# Open: master_results_final_strong/comparison/statistical_validation.csv
```

---

## 8. Optional — Shorter Test Run

For a quicker demo (fewer seeds, fewer rounds):
```bash
python scripts/run_master_simulation.py --seeds 3 --rounds 300 --out quick_test
```
Results in `quick_test/comparison/`. Less statistically robust but faster.
