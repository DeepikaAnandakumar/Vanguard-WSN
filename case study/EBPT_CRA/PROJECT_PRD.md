# EBPT-CRA Project - Complete Product Requirements Document

**Project Name:** Energy-Balanced Path Tree with Clustering and Routing Algorithm (EBPT-CRA)  
**Type:** Wireless Sensor Network (WSN) Simulation Framework  
**Language:** Python 3  
**Status:** Active Development  
**Date:** February 2026

---

## 1. PROJECT OVERVIEW

### 1.1 Purpose
EBPT-CRA is a comprehensive simulation framework designed to model, evaluate, and optimize routing protocols and clustering algorithms for Wireless Sensor Networks (WSNs). The project implements the Energy-Balanced Path Tree (EBPT) algorithm combined with Cluster Head (CH) selection and inter-cluster routing strategies.

### 1.2 Key Objectives
- Simulate WSN behavior with realistic energy consumption models
- Implement EBPT algorithm for energy-balanced path generation
- Evaluate cluster-head selection and cluster formation strategies
- Measure network lifetime metrics (First Node Death, Half Node Death, Last Node Death)
- Support parameter sweeps and multi-seed experiments
- Generate comprehensive metrics and visualizations

### 1.3 Target Users
- Researchers in wireless sensor networks
- Algorithm developers testing routing/clustering approaches
- Students learning WSN simulation and optimization
- Engineers evaluating network protocols

---

## 2. SYSTEM ARCHITECTURE

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    EBPT-CRA Simulation Framework                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────┐    ┌──────────────────┐                   │
│  │   CORE MODULE    │    │  SCRIPTS MODULE  │                   │
│  │  - Network       │    │  - run_experiments│                  │
│  │  - Node          │    │  - parameter_sweep│                  │
│  │  - Params        │    │  - plot_metrics   │                  │
│  │  - Assumptions   │    │  - inspect_clusters│                 │
│  └──────────────────┘    └──────────────────┘                   │
│           │                       │                               │
│  ┌────────▼──────────────────────▼────────┐                     │
│  │       CLUSTERING MODULE                 │                     │
│  │  (clustering/ folder)                   │                     │
│  │  - Cluster Head Selection               │                     │
│  │  - Cluster Formation                    │                     │
│  │  - Metrics Collection                   │                     │
│  └────────┬───────────────────────────────┘                     │
│           │                                                       │
│  ┌────────▼──────────────────────────────┐                     │
│  │       ROUTING MODULE                   │                     │
│  │  (routing/ folder)                     │                     │
│  │  - EBPT Algorithm                      │                     │
│  │  - Inter-cluster Routing               │                     │
│  │  - Forwarding Node Selection           │                     │
│  │  - Weight Calculations                 │                     │
│  └────────┬──────────────────────────────┘                     │
│           │                                                       │
│  ┌────────▼──────────────────────────────┐                     │
│  │       ENERGY MODULE                    │                     │
│  │  (energy/ folder)                      │                     │
│  │  - First Order Radio Model             │                     │
│  │  - TX/RX Energy Calculations           │                     │
│  └────────┬──────────────────────────────┘                     │
│           │                                                       │
│  ┌────────▼──────────────────────────────┐                     │
│  │       RESULTS MODULE                   │                     │
│  │  (results/ folder & variants)          │                     │
│  │  - Metrics JSON/CSV                    │                     │
│  │  - Performance Plots                   │                     │
│  │  - Run History                         │                     │
│  └────────────────────────────────────────┘                     │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. FOLDER STRUCTURE & DETAILED CONTENTS

### 3.1 ROOT DIRECTORY: `/EBPT_CRA/`

**Purpose:** Project root containing all modules, scripts, and results.

#### Files:
- `__pycache__/` - Python bytecode cache (auto-generated)

---

### 3.2 CORE MODULE: `/core/`

**Purpose:** Core network simulation and configuration components.

#### Contents:

##### 3.2.1 `__init__.py`
- Package initialization file
- Enables imports from the core module

##### 3.2.2 `params.py`
**Description:** Central configuration and parameter definitions for the entire simulation.

**Key Parameters:**
```python
# Energy Parameters
INITIAL_ENERGY = 1.0                    # Node starting energy (Joules)
E_ELEC = 50e-9                         # Electronic energy per bit (J)
EPS_FS = 10e-12                        # Free-space amplifier energy
EPS_MP = 0.0013e-12                    # Multi-path amplifier energy
E_DA = 5e-9                            # Data aggregation cost per bit (J/bit)

# Network Parameters
DATA_BITS = 2500                       # Data bits per node per round
CH_PROB = 0.1                          # Cluster head selection probability
AGGR_RATIO = 0.4                       # Data aggregation compression ratio

# Field Parameters
DEFAULT_FIELD_X = 100                  # Network field X dimension (meters)
DEFAULT_FIELD_Y = 100                  # Network field Y dimension (meters)
```

**Usage:** Imported globally to configure all simulations. Parameters can be overridden at runtime via command-line arguments.

##### 3.2.3 `node.py`
**Description:** Represents a single sensor node in the network.

**Node Class:**
```python
class Node:
    Attributes:
    - id              : Unique node identifier
    - x, y            : Position coordinates
    - energy          : Current remaining energy (Joules)
    - initial_energy  : Starting energy value
    - alive           : Boolean flag (True if energy > 0)
    - parent          : Parent node in routing tree
    - children        : List of child nodes
    - is_ch           : Boolean - is this a cluster head?
    - is_forwarder    : Boolean - is this a forwarder node?
    - _recv_bits      : Per-round bookkeeping for received bits
    - _forward_queue  : Per-round queue of bits to forward
    
    Methods:
    - distance_to(other)   : Calculate Euclidean distance
    - consume_energy(amt)  : Deplete energy, mark dead if <= 0
```

**Purpose:** Node model with position, energy tracking, and role assignment (cluster head, forwarder).

##### 3.2.4 `network.py`
**Description:** Main Network class orchestrating the simulation.

**Network Class:**
```python
class Network:
    Key Attributes:
    - nodes              : List of all sensor nodes
    - bs                 : Base station node
    - field_x, field_y   : Network dimensions
    - cluster_heads      : List of selected cluster heads
    - clusters           : Dictionary mapping CH ID to members
    - forwarders         : List of forwarder nodes
    - paths              : Dictionary of routing paths
    - metrics            : Metrics collector for tracking statistics
    
    Key Methods:
    - __init__(*args, **kwargs)    : Flexible constructor supporting multiple API styles
    - deploy_nodes(num_nodes, area_size)  : Place nodes randomly
    - deploy_bs(x, y)              : Place base station
    - build()                      : Execute build phase
      * Selects cluster heads
      * Forms clusters
      * Selects forwarders
      * Computes EBPT routing
    - run_round()                  : Execute one simulation round
      * Members transmit to CHs
      * CHs aggregate and forward
      * Forwarders relay to BS
      * All energy costs computed
    - log_metrics(round)           : Record round statistics
    - reconfiguration_needed()     : Check if rebuild required
```

**Round Execution Flow:**
1. Members transmit data to cluster heads (members pay TX, CH pays RX)
2. CHs aggregate received data (pay aggregation cost)
3. CHs forward aggregated data to parent (pay TX)
4. Forwarders relay data upward toward BS
5. BS receives all data
6. Metrics recorded (alive nodes, total energy, dead nodes)

##### 3.2.5 `assumptions.py`
**Description:** Explicit statement of simulation assumptions for transparency.

**Key Assumptions:**
1. **Static Nodes** - No mobility, fixed positions
2. **Homogeneous Energy** - All nodes start with identical energy
3. **Single BS** - One base station with infinite energy at center
4. **No Packet Loss** - Deterministic communication
5. **First-Order Radio Model** - Standard energy consumption formula
6. **Fixed Data Generation** - 2500 bits per node per round
7. **Stationary Topology** - No dynamic link formation/breaking

---

### 3.3 ENERGY MODULE: `/energy/`

**Purpose:** Energy consumption models and radio transmission calculations.

#### Contents:

##### 3.3.1 `__init__.py`
- Package initialization

##### 3.3.2 `first_order_radio.py`
**Description:** First-order radio energy model (standard in WSN research).

**Functions:**
```python
def tx_energy(bits, distance):
    """
    Transmit energy calculation.
    E_TX(k, d) = k * (E_ELEC + E_AMP * d²)
    
    Args:
        bits: Number of bits to transmit
        distance: Distance to receiver (meters)
    
    Returns:
        Energy cost in Joules
    """

def rx_energy(bits):
    """
    Receive energy calculation.
    E_RX(k) = k * E_ELEC
    
    Args:
        bits: Number of bits received
    
    Returns:
        Energy cost in Joules
    """
```

**Energy Formulas:**
- **TX Energy:** $E_{TX}(k,d) = k(E_{elec} + \epsilon_{fs} d^2)$ for d < threshold
- **RX Energy:** $E_{RX}(k) = k \cdot E_{elec}$
- **Aggregation Cost:** $E_{DA} = k \cdot E_{da}$ (per aggregated bit)

---

### 3.4 CLUSTERING MODULE: `/clustering/`

**Purpose:** Cluster head selection and cluster formation algorithms.

**Status:** Currently empty in repository (requires implementation or external imports)

**Expected Contents (based on code references):**

#### Expected: `ch_selection.py`
**Purpose:** Cluster head selection strategies.

**Expected Function:**
```python
def select_cluster_heads(nodes, p=None):
    """
    Select cluster heads from sensor nodes.
    
    Args:
        nodes: List of sensor nodes
        p: Cluster head probability (default from params.CH_PROB)
    
    Returns:
        List of selected cluster head nodes
    """
```

**Fallback Implementation (in network.py):**
- Probabilistic selection: node selected as CH if `node.id % int(1/p) == 0`
- Probability = 0.1 by default

#### Expected: `cluster_formation.py`
**Purpose:** Group nodes into clusters around cluster heads.

**Expected Function:**
```python
def form_clusters(cluster_heads, nodes):
    """
    Form clusters of nodes around each cluster head.
    
    Args:
        cluster_heads: List of selected cluster heads
        nodes: All sensor nodes
    
    Returns:
        Dictionary {ch_id: [list of member nodes]}
    """
```

#### Expected: `metrics.py`
**Purpose:** Collect and track simulation metrics.

**Expected Class:**
```python
class Metrics:
    Tracks:
    - rounds: List of round numbers
    - alive_nodes: Nodes alive at each round
    - total_energy: Total network energy each round
    - dead_nodes: Number dead nodes each round
    - num_chs: Cluster heads selected each round
    - first_node_death: Round when first node dies
    - half_node_death: Round when half nodes dead
    - last_node_death: Round when all nodes dead
    
    Methods:
    - log(round, alive, energy, dead, num_chs): Record metrics
```

---

### 3.5 ROUTING MODULE: `/routing/`

**Purpose:** Routing algorithms and path computation.

#### Contents:

##### 3.5.1 `__init__.py`
- Package initialization

##### 3.5.2 `ebpt.py`
**Description:** Energy-Balanced Path Tree algorithm implementation.

**Function:** `compute_ebpt(nodes, bs)`

**Algorithm:**
1. Clear existing parent/children relationships
2. Sort all nodes by distance to BS (ascending)
3. For each node in sorted order:
   - Identify candidates: BS + all previously-processed nodes
   - Select parent = candidate closest to current node
   - Record parent-child relationship
4. Build children lists for tree traversal

**Properties:**
- Creates acyclic tree rooted at BS
- Greedy algorithm based on distance
- Produces energy-balanced paths
- Time complexity: O(n²) for n nodes

##### 3.5.3 `ebpt_weight.py`
**Description:** Edge weight calculation for EBPT routing.

**Function:** `ebpt_edge_weight(node_i, node_j)`

**Weight Formula:**
$$w_{ij} = \frac{E_i}{ETX(k,d)} + \frac{E_j}{ERX(k)}$$

Where:
- $E_i$, $E_j$ = remaining energy of nodes i and j
- $ETX$ = transmission energy
- $ERX$ = reception energy

**Purpose:** Weight nodes by energy-normalized link cost (higher energy = better candidate).

##### 3.5.4 `forwarding.py`
**Description:** Forwarder node selection for inter-cluster routing.

**Function:** `select_forwarders(nodes, bs, k=5)`

**Algorithm:**
1. Clear previous forwarder flags
2. Filter alive nodes
3. Sort by distance to BS (ascending)
4. Select k closest nodes as forwarders
5. Mark selected nodes with `is_forwarder = True`

**Default:** k=5 forwarders

**Purpose:** Select backbone nodes to relay cluster head data toward BS.

##### 3.5.5 `inter_cluster_routing.py`
**Description:** Routes cluster heads to base station via forwarders.

**Function:** `route_ch_to_bs(cluster_heads, forwarders, bs)`

**Algorithm:**
1. For each cluster head:
   - If no forwarders available: route directly to BS
   - Otherwise: route CH -> nearest forwarder -> BS

**Output:** Dictionary `{ch_id: [ch_id, forwarder_id, "BS"]}`

**Purpose:** Define inter-cluster routing paths.

##### 3.5.6 `inter_cluster_weight.py`
**Description:** Weight function for inter-cluster routing decisions.

**Function:** `inter_cluster_weight(i, j, bs)`

**Weight Formula:**
$$W_{ij} = 0.6 \cdot \frac{E_i}{ETX(k,d_{ij})} + 0.1 \cdot \frac{E_j}{ERX(k)} + 0.3 \cdot \frac{E_j}{ETX(k,d_{j,BS})}$$

**Components:**
- 0.6: Energy of sender (i) relative to transmission cost
- 0.1: Energy of receiver (j) relative to reception cost
- 0.3: Energy of receiver (j) relative to cost reaching BS

**Special Case:** BS energy treated as 1.0 (not infinite) to prevent infinite weights.

---

### 3.6 SCRIPTS MODULE: `/scripts/`

**Purpose:** Executable simulation runners and analysis tools.

#### Contents:

##### 3.6.1 `run_experiments.py`
**Description:** Core experiment runner - executes multi-seed simulations with aggregation.

**Key Functions:**

```python
def run_seed(seed, rounds, num_nodes, field_x, field_y, bs_pos, out_dir, stop_on_fnd=False):
    """
    Run single-seed simulation.
    
    Args:
        seed: Random seed for reproducibility
        rounds: Number of simulation rounds
        num_nodes: Number of sensor nodes
        field_x, field_y: Network dimensions
        bs_pos: (x, y) tuple for base station position
        out_dir: Output directory for metrics
        stop_on_fnd: Stop early on first node death
    
    Returns:
        Dictionary with metrics for all rounds
    """

def aggregate(all_metrics, rounds):
    """
    Aggregate metrics across multiple seeds.
    
    Args:
        all_metrics: List of metric dictionaries (one per seed)
        rounds: Total number of rounds
    
    Returns:
        Aggregated dictionary with:
        - alive_mean, alive_std per round
        - energy_mean, energy_std per round
        - num_chs_mean, num_chs_std per round
        - FND/HND/LND statistics (mean, std, count)
    """

def save_csv(agg, out_csv):
    """Save aggregated metrics to CSV file."""

def plot_agg(agg, out_dir):
    """Generate PNG plots for energy and alive nodes vs rounds."""

def main():
    """CLI entry point with argument parsing."""
```

**CLI Arguments:**
```
--seeds           : Number of random seeds (default: 10)
--rounds          : Simulation rounds per seed (default: 200)
--nodes           : Number of sensor nodes (default: 50)
--field           : Field dimension (default: 100)
--bs_x, --bs_y    : Base station position (default: 50, 50)
--data-bits       : Override DATA_BITS parameter
--initial-energy  : Override INITIAL_ENERGY parameter
--out             : Output directory (default: results)
--start-seed      : Starting seed number (default: 0)
--stop-on-fnd     : Stop early when first node dies
```

**Output:**
- `results/{directory}/metrics_seed_{N}.json` - Per-seed metrics
- `results/{directory}/agg_metrics.json` - Aggregated metrics
- `results/{directory}/agg_metrics.csv` - Aggregated metrics CSV
- `results/{directory}/avg_energy.png` - Energy plot
- `results/{directory}/avg_alive.png` - Alive nodes plot

##### 3.6.2 `parameter_sweep.py`
**Description:** Grid search over parameter space (DATA_BITS × INITIAL_ENERGY).

**Key Function:**
```python
def run_grid(data_bits_list, energy_list, seeds, rounds, out_root):
    """
    Run grid of experiments with parameter variations.
    
    Args:
        data_bits_list: List of DATA_BITS values to test
        energy_list: List of INITIAL_ENERGY values to test
        seeds: Number of seeds per configuration
        rounds: Rounds per simulation
        out_root: Root output directory
    
    Creates:
    - results_sweep/run_YYYYMMDD_HHMMSS/
    - Subdirectories: db{X}_ie{Y}/ for each (data_bits, initial_energy) pair
    - Summary CSV/JSON with statistics
    """
```

**Purpose:** Systematic exploration of parameter sensitivity.

**Output Structure:**
```
results_sweep/
├── run_YYYYMMDD_HHMMSS/
│   ├── db2500_ie1.0/
│   │   ├── metrics_seed_0.json
│   │   ├── agg_metrics.json
│   │   └── ...plots...
│   ├── db2500_ie2.0/
│   ├── db5000_ie1.0/
│   └── ...more configs...
└── summary.csv
```

##### 3.6.3 `plot_metrics.py`
**Description:** Visualization tool for analyzing saved metrics.

**Purpose:** Generate graphs and plots from JSON/CSV results for analysis and reporting.

##### 3.6.4 `inspect_clusters.py`
**Description:** Debug utility to examine cluster structure.

**Purpose:** Print cluster composition, verify CH selection, inspect network state.

##### 3.6.5 `find_seed.py`
**Description:** Utility to find specific seed with particular properties.

**Purpose:** Search for seeds producing interesting network behavior or corner cases.

##### 3.6.6 `test_ebpt.py`
**Description:** Unit test for EBPT algorithm.

**Purpose:** Verify EBPT produces valid trees.

##### 3.6.7 `test_import.py`
**Description:** Test module imports.

**Purpose:** Debug import issues and module dependencies.

##### 3.6.8 `test_metrics.py`
**Description:** Test metrics collection.

**Purpose:** Verify metrics are correctly recorded.

##### 3.6.9 `debug_import_chsel.py`
**Description:** Debug cluster head selection imports.

**Purpose:** Diagnose issues with CH selection module loading.

---

### 3.7 RESULTS MODULE: `/results/`

**Purpose:** Primary storage for simulation outputs and metrics.

#### Structure:

##### Contents:
- `metrics_seed_0.json` through `metrics_seed_19.json` - Per-seed metrics (20 seeds)
- `agg_metrics.json` - Aggregated metrics across all seeds
- `agg_metrics.csv` - CSV format of aggregated metrics
- `metrics.json` - Combined metrics summary
- `base_run/` - Baseline run results
- `run_20260202_225405/` - Timestamped run directory
- `test_runs/` - Test experiment results

##### File Formats:

**Per-Seed JSON (metrics_seed_N.json):**
```json
{
  "seed": 0,
  "rounds": [0, 1, 2, ..., 199],
  "alive_nodes": [50, 48, 47, ..., 0],
  "total_energy": [50.0, 45.3, 40.8, ..., 0.0],
  "dead_nodes": [0, 2, 3, ..., 50],
  "num_chs": [5, 4, 5, ..., 0],
  "first_node_death": 45,
  "half_node_death": 120,
  "last_node_death": 198
}
```

**Aggregated JSON (agg_metrics.json):**
```json
{
  "rounds": [0, 1, 2, ..., 199],
  "alive_mean": [50.0, 48.5, 47.2, ...],
  "alive_std": [0.0, 0.8, 1.1, ...],
  "energy_mean": [50.0, 45.5, 40.9, ...],
  "energy_std": [0.0, 0.4, 0.6, ...],
  "num_chs_mean": [5.0, 4.8, 4.9, ...],
  "num_chs_std": [0.5, 0.4, 0.6, ...],
  "FND": {"mean": 45, "std": 3.2, "count": 20},
  "HND": {"mean": 120, "std": 5.1, "count": 20},
  "LND": {"mean": 198, "std": 0.3, "count": 20}
}
```

---

### 3.8 RESULTS VARIANTS: `/results_base/`, `/results_long/`, `/results_long2/`, `/results_sweep/`, `/results_test/`

**Purpose:** Alternative result storage for different experiment configurations.

| Directory | Purpose |
|-----------|---------|
| `results_base/` | Baseline configuration results |
| `results_long/` | Extended simulation (more rounds) |
| `results_long2/` | Second extended run variant |
| `results_sweep/` | Parameter sweep results |
| `results_test/` | Test run outputs |

**Structure:** Each follows same format as `/results/` with timestamped subdirectories.

---

### 3.9 UTILITIES MODULE: `/utils/`

**Status:** Currently empty (reserved for utility functions)

**Expected Contents:** Helper functions for:
- File I/O operations
- Data transformations
- Visualization utilities
- Statistical calculations

---

### 3.10 SIMULATION MODULE: `/simulation/`

**Status:** Currently empty (reserved for simulation helpers)

**Expected Contents:** Advanced simulation features:
- Multi-scenario runners
- Batch processors
- Custom event handlers

---

### 3.11 PYCACHE: `/__pycache__/`

**Purpose:** Auto-generated Python bytecode cache.

**Action:** Safe to delete; will be regenerated automatically.

---

## 4. WORKFLOW & DATA FLOW

### 4.1 Typical Simulation Workflow

```
1. USER INITIATES EXPERIMENT
   └─> run_experiments.py --seeds 10 --rounds 200

2. EXPERIMENT SETUP
   └─> params.py loaded (INITIAL_ENERGY, DATA_BITS, etc.)

3. PER-SEED LOOP (seed 0 to 9)
   ├─> Network created with N nodes, random positions
   ├─> Base station placed at (50, 50)
   ├─> network.build() called:
   │   ├─> EBPT computed (compute_ebpt)
   │   ├─> Cluster heads selected (select_cluster_heads)
   │   ├─> Clusters formed (form_clusters)
   │   ├─> Forwarders selected (select_forwarders)
   │   └─> Routes computed (route_ch_to_bs)
   │
   └─> PER-ROUND LOOP (round 0 to 199)
       ├─> network.run_round() executes:
       │   ├─> Members transmit to CHs
       │   │   ├─> Members pay TX energy
       │   │   └─> CHs pay RX energy
       │   ├─> CHs aggregate data
       │   │   └─> CHs pay E_DA cost
       │   ├─> CHs forward to parents
       │   │   └─> CHs pay TX energy
       │   └─> Forwarders forward to BS
       │
       ├─> network.log_metrics(r) records:
       │   ├─> Alive nodes count
       │   ├─> Total network energy
       │   ├─> Dead nodes count
       │   ├─> Cluster heads count
       │   └─> FND/HND/LND tracking
       │
       └─> Check reconfiguration_needed()
           └─> If true: network.build() again

4. PER-SEED EXPORT
   └─> results/metrics_seed_{N}.json written

5. AGGREGATION
   └─> aggregate(all_metrics) computes:
       ├─> Mean/std per round
       └─> FND/HND/LND statistics

6. OUTPUT GENERATION
   ├─> results/agg_metrics.json
   ├─> results/agg_metrics.csv
   ├─> results/avg_energy.png
   └─> results/avg_alive.png
```

### 4.2 Energy Consumption Flow (Per Round)

```
Intra-Cluster:
┌─────────────────────────────────────────┐
│ Member Node M transmits to Cluster Head│
└─────────────────────────────────────────┘
         ↓
    M.consume_energy(
      tx_energy(DATA_BITS, distance_to_CH)
    )
         ↓
    CH.consume_energy(
      rx_energy(DATA_BITS)
    )
    CH._recv_bits += DATA_BITS

Aggregation in Cluster Head:
┌─────────────────────────────────────────┐
│ CH aggregates own data + received data  │
└─────────────────────────────────────────┘
    total_bits = DATA_BITS + CH._recv_bits
         ↓
    CH.consume_energy(
      E_DA * total_bits
    )
         ↓
    aggregated_bits = total_bits * AGGR_RATIO

Inter-Cluster Forwarding:
┌─────────────────────────────────────────┐
│ CH sends aggregated data toward BS      │
└─────────────────────────────────────────┘
         ↓
    CH.consume_energy(
      tx_energy(aggregated_bits, distance_to_parent)
    )
         ↓
    parent.consume_energy(
      rx_energy(aggregated_bits)
    )
```

---

## 5. KEY ALGORITHMS

### 5.1 EBPT (Energy-Balanced Path Tree)

**Algorithm Goal:** Build a tree of paths from all nodes toward BS that balances energy consumption.

**Pseudocode:**
```
Function COMPUTE_EBPT(nodes, bs):
    Clear all parent/children relationships
    
    nodes_sorted ← Sort(nodes by distance to bs)
    
    For each node n in nodes_sorted:
        If n is not alive: continue
        
        candidates ← [bs] + [m ∈ nodes_sorted | distance(m,bs) < distance(n,bs) AND m.alive]
        
        parent ← argmin(candidate ∈ candidates) [ distance(n, candidate) ]
        
        n.parent ← parent
        If parent ≠ bs:
            parent.children.append(n)
    
    Return modified nodes with populated parent/children
```

**Complexity:** O(n²) due to distance comparisons.

**Properties:**
- Deterministic (same result for same seed)
- Acyclic tree rooted at BS
- Greedy nearest-parent selection
- Can be used for intra-cluster or full network routing

### 5.2 Cluster Head Selection

**Algorithm Goal:** Probabilistically select cluster heads from sensor nodes.

**Default Implementation:**
```
Function SELECT_CLUSTER_HEADS(nodes, p):
    // p = probability of becoming CH (default 0.1)
    
    chs ← []
    For each node n in nodes:
        If n.alive AND (n.id % int(1/p) == 0):
            n.is_ch ← True
            chs.append(n)
    
    Return chs
```

**Probability:** p = 0.1 → ~10% of nodes become cluster heads for nodes 0, 10, 20, ...

### 5.3 Cluster Formation

**Algorithm Goal:** Assign nodes to cluster heads based on proximity or EBPT structure.

**Expected Algorithm:**
```
Function FORM_CLUSTERS(cluster_heads, nodes):
    clusters ← {}
    
    For each ch in cluster_heads:
        clusters[ch.id] ← [ch] + [nodes that select ch as parent]
    
    Return clusters
```

**Alternative:** Uses EBPT parent-child relationships if available.

### 5.4 Forwarder Selection

**Algorithm Goal:** Select backbone nodes for inter-cluster routing.

**Pseudocode:**
```
Function SELECT_FORWARDERS(nodes, bs, k):
    nodes_alive ← Filter(nodes | node.alive)
    nodes_sorted ← Sort(nodes_alive by distance to bs)
    
    forwarders ← nodes_sorted[0:k]  // First k nodes
    
    For each f in forwarders:
        f.is_forwarder ← True
    
    Return forwarders
```

**Default k:** 5 nodes

**Rationale:** Nodes closest to BS have lowest cost to relay data.

---

## 6. METRICS & KEY PERFORMANCE INDICATORS

### 6.1 Per-Round Metrics

| Metric | Description | Unit |
|--------|-------------|------|
| **Alive Nodes** | Count of nodes with energy > 0 | Count |
| **Total Energy** | Sum of all node remaining energies | Joules |
| **Dead Nodes** | Count of nodes with energy <= 0 | Count |
| **Num CHs** | Count of selected cluster heads | Count |

### 6.2 Network Lifetime Metrics

| Metric | Description | Unit |
|--------|-------------|------|
| **FND** | First Node Death - round when first node dies | Round |
| **HND** | Half Node Death - round when 50% nodes dead | Round |
| **LND** | Last Node Death - round when all nodes dead | Round |

### 6.3 Aggregated Metrics (Across Seeds)

For each metric at each round:
- **Mean:** Average across all seeds
- **Std Dev:** Standard deviation across seeds

For lifetime metrics:
- **Mean:** Average FND/HND/LND across seeds
- **Std Dev:** Standard deviation
- **Count:** Number of seeds completed

### 6.4 Interpretation

**Good Network Performance:**
- High FND (nodes survive long)
- High HND (nodes survive to later rounds)
- Slow energy depletion (gradual slope)
- Low std dev (consistent across seeds)

**Poor Network Performance:**
- Low FND (nodes die early)
- High variability (large std dev)
- Rapid energy collapse

---

## 7. SYSTEM REQUIREMENTS

### 7.1 Software Requirements

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.7+ | Runtime |
| matplotlib | Latest | Plotting |
| (Optional) numpy | Latest | Numerical computation |
| (Optional) scipy | Latest | Statistical analysis |

### 7.2 Hardware Requirements

**Minimum:**
- 2GB RAM
- 1GB disk space
- Multi-core processor recommended for parameter sweeps

**Recommended:**
- 8GB+ RAM for large-scale sweeps
- SSD for I/O performance

---

## 8. CONFIGURATION & CUSTOMIZATION

### 8.1 Parameter Modification

**Method 1: Edit params.py**
```python
# core/params.py
INITIAL_ENERGY = 2.0        # Increase initial energy
DATA_BITS = 5000            # More data per round
CH_PROB = 0.15              # 15% cluster head probability
```

**Method 2: Command-Line Override**
```bash
python scripts/run_experiments.py \
    --initial-energy 2.0 \
    --data-bits 5000 \
    --rounds 300
```

**Method 3: Parameter Sweep**
```bash
python scripts/parameter_sweep.py \
    --data-bits 2500 5000 7500 \
    --energy 0.5 1.0 2.0 3.0 \
    --seeds 5 --rounds 200
```

### 8.2 Field Configuration

**Network Dimensions:**
```python
# Modify network size
network = Network(
    n=100,              # More nodes
    field_x=200,        # Larger X dimension
    field_y=200,        # Larger Y dimension
    bs_pos=(100, 100)   # Center BS
)
```

### 8.3 Radio Model Tuning

**Energy Model Parameters (core/params.py):**
```python
E_ELEC = 50e-9          # Receiver/transmitter circuitry
EPS_FS = 10e-12         # Free-space path loss coefficient
E_DA = 5e-9             # Data aggregation cost
AGGR_RATIO = 0.4        # Compression ratio (0.4 = 40% of original)
```

---

## 9. EXTENSION POINTS & FUTURE FEATURES

### 9.1 Implementation Gaps

The following modules are referenced but not fully implemented:

1. **clustering/ch_selection.py** - Probabilistic CH selection
   - Can implement advanced algorithms (LEACH-like, distributed)
   
2. **clustering/cluster_formation.py** - Cluster grouping
   - Can implement proximity-based, cost-based, or tree-based clustering
   
3. **clustering/metrics.py** - Advanced metrics
   - Can extend to track throughput, latency, fairness

4. **simulation/** - Simulation helpers
   - Batch runners, scenario files, event handlers

5. **utils/** - Utility functions
   - Data validation, format conversion, helpers

### 9.2 Potential Enhancements

1. **Mobility Models** - Add node movement (random walk, etc.)
2. **Link Quality** - Probabilistic packet loss, fading
3. **Multi-Path Routing** - Backup routes for reliability
4. **Cross-Layer Optimization** - MAC/PHY layer integration
5. **Real Data Traces** - Load network data from files
6. **Visualization** - Network animation, live plots
7. **Machine Learning** - Intelligent CH selection or routing
8. **Distributed Simulation** - Parallel seed execution
9. **Database Backend** - Store results in MongoDB/PostgreSQL
10. **Web Dashboard** - Interactive results viewing

---

## 10. EXECUTION GUIDE

### 10.1 Running Basic Simulation

```bash
cd d:\SEM 6\CNproject\EBPT_CRA

# Simple run: 10 seeds, 200 rounds
python scripts/run_experiments.py --seeds 10 --rounds 200

# Custom parameters
python scripts/run_experiments.py \
    --seeds 20 \
    --rounds 300 \
    --nodes 100 \
    --initial-energy 2.0 \
    --data-bits 5000 \
    --out results_custom
```

### 10.2 Parameter Sweep

```bash
# Test 3 energy levels × 3 data rates = 9 configurations
python scripts/parameter_sweep.py \
    --data-bits 2500 5000 7500 \
    --energy 0.5 1.0 2.0 \
    --seeds 5 \
    --rounds 200 \
    --out results_sweep
```

### 10.3 Analyzing Results

```bash
# Plot metrics from completed run
python scripts/plot_metrics.py results/

# Inspect cluster structure for debugging
python scripts/inspect_clusters.py

# Find interesting seeds
python scripts/find_seed.py
```

### 10.4 Testing

```bash
# Test module imports
python scripts/test_import.py

# Test EBPT algorithm
python scripts/test_ebpt.py

# Test metrics collection
python scripts/test_metrics.py
```

---

## 11. OUTPUT FILES REFERENCE

### 11.1 JSON Metrics Format

**Location:** `results/metrics_seed_N.json`

**Fields:**
- `seed`: Random seed used
- `rounds`: List of round numbers [0, 1, ..., R-1]
- `alive_nodes`: Count per round [50, 48, 45, ...]
- `total_energy`: Joules per round [50.0, 45.2, 40.1, ...]
- `dead_nodes`: Count per round [0, 2, 5, ...]
- `num_chs`: Cluster heads per round [5, 4, 4, ...]
- `first_node_death`: Round number (or null)
- `half_node_death`: Round number (or null)
- `last_node_death`: Round number (or null)

### 11.2 CSV Aggregated Format

**Location:** `results/agg_metrics.csv`

**Columns:**
```
round,alive_mean,alive_std,energy_mean,energy_std,num_chs_mean,num_chs_std
0,50.0,0.0,50.0,0.0,5.0,0.5
1,48.5,0.8,45.2,0.4,4.8,0.4
...
```

### 11.3 PNG Plots

**Files Generated:**
- `avg_energy.png` - Line plot of energy depletion with error bands
- `avg_alive.png` - Line plot of alive nodes with error bands

**X-axis:** Round number  
**Y-axis:** Mean value ± standard deviation

---

## 12. TROUBLESHOOTING

### Issue: Import Errors

**Symptom:** `ImportError: No module named 'clustering'`

**Solution:**
1. Check that clustering/ folder exists
2. Verify `__init__.py` files exist in all package folders
3. Ensure working directory is project root
4. Run from scripts/ as: `python -c "import sys; sys.path.insert(0, '..'); from scripts.run_experiments import *"`

### Issue: Metrics Show NaN or Infinite Values

**Symptom:** `"energy_mean": [NaN, Infinity, ...]`

**Cause:** Dead nodes or simulation crashed

**Solution:**
1. Check node energy calculations
2. Verify first-order radio model parameters
3. Inspect per-seed JSON files for anomalies

### Issue: Results Directory Bloat

**Symptom:** Too many result files

**Solution:**
```bash
# Archive old results
tar -czf results_old.tar.gz results/
rm -rf results/

# Keep only latest
ls -lt results_* | head -3
```

---

## 13. RESEARCH CONTEXT

### 13.1 Related Work

This implementation is based on:
- **EBPT (Energy-Balanced Path Tree)** - Distributed routing algorithm
- **LEACH** - Clustering protocol for WSNs
- **Hierarchical Routing** - Multi-tier network organization
- **First-Order Radio Model** - Standard energy consumption model in WSN research

### 13.2 Key References

Areas covered:
1. Wireless Sensor Network protocols
2. Energy-aware routing algorithms
3. Cluster-based hierarchical networks
4. Simulation and performance evaluation
5. Statistical analysis of network lifetime

---

## 14. PROJECT METADATA

| Property | Value |
|----------|-------|
| Project Name | EBPT-CRA |
| Type | WSN Simulation Framework |
| Language | Python 3 |
| License | [Not specified - add if applicable] |
| Author/Institution | [Not specified - add if applicable] |
| Created | 2026 |
| Status | Active Development |
| Documentation | This PRD |

---

## 15. QUICK REFERENCE CHECKLIST

- [ ] **Core Module** - Network, Node, Params, Assumptions complete
- [ ] **Energy Module** - First-order radio model implemented
- [ ] **Clustering Module** - CH selection and cluster formation (needs implementation)
- [ ] **Routing Module** - EBPT, forwarding, inter-cluster routing complete
- [ ] **Scripts Module** - run_experiments, parameter_sweep, plotting tools complete
- [ ] **Results Module** - JSON/CSV output, plotting complete
- [ ] **Testing** - Basic unit tests available
- [ ] **Documentation** - This PRD comprehensive

---

## APPENDIX: GLOSSARY

| Term | Definition |
|------|-----------|
| **BS/Base Station** | Sink node with infinite energy receiving data from network |
| **CH/Cluster Head** | Selected node serving as aggregation point for cluster |
| **EBPT** | Energy-Balanced Path Tree - routing algorithm |
| **FND** | First Node Death - network lifetime metric |
| **HND** | Half Node Death - network lifetime metric |
| **LND** | Last Node Death - network lifetime metric |
| **Forwarder** | Node relaying data between cluster heads and BS |
| **Aggregation** | Combining multiple data packets into single message |
| **ETX** | Transmission energy cost |
| **ERX** | Reception energy cost |
| **Seed** | Random number seed for reproducible simulations |
| **Round** | Single simulation time step |
| **WSN** | Wireless Sensor Network |

---

**End of Document**

---

**Document Generated:** February 3, 2026  
**Comprehensive Project Documentation for AI Handoff**  
**Ready for use with AI systems for development and feature additions**
