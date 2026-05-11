# Coding & Implementation Report: Inside Vanguard-WSN
**A Software Engineering Deep-Dive into the EBPT-CRA Framework**

This report explains the coding structure, design patterns, and technical implementation techniques used to build the Vanguard-WSN simulation environment.

---

## 1. Architectural Philosophy: Modular & Object-Oriented
The Vanguard-WSN project (implemented as the `EBPT_CRA` library) is built using **Object-Oriented Programming (OOP)** principles. We have modeled the physical world of sensor networks into distinct software components.

### **1.1 The Module Breakdown**
The code is organized into specialized packages to ensure strict separation of concerns:
- **`core/`:** The engine's heart. Contains the `Network` and `Node` classes, and the `Controller` logic.
- **`routing/`:** Contains the primary algorithms, including the **EBPT** (our innovation) and baselines like PEGASIS and LEACH.
- **`energy/`:** Dedicated to the **Radio Energy Models**. This ensures that if we want to change physics (e.g., switch to a 5G model), we only edit one file.
- **`clustering/`:** Handles the selection of Cluster Heads and organizational logic.
- **`scripts/`:** Executable tools for running large-scale experiments and generating visualizations.

---

## 2. Key Coding Concepts
### **2.1 Object Modeling (The Entity-Relationship)**
- **`Node` Class:** Each instance represents a physical sensor. It manages its own state: current energy, (x, y) coordinates, and its "Alive" status. This encapsulates the physical constraints of a single device.
- **`Network` Class:** A container object that manages the "Population" of nodes. It handles deployment, BS placement, and global state tracking.
- **`Controller` (The Brain):** Implements the SDN (Software Defined Networking) logic. It performs the "Global Sort" of nodes and executes the central parent-selection logic.

### **2.2 Discrete Round Simulation**
The code does not use "Real-Time" (which is inconsistent based on CPU speed). Instead, it uses **Discrete Round Simulation**. 
- Each unit of time is a "Round."
- In each round, the code iterates through a lifecycle: **Sense -> Cluster -> Route -> Transmit -> Bookkeep.**
- **Bookkeeping:** After transmissions, the `consume_energy()` method is called for every node, subtracting the calculated radio cost from the node's `self.energy` attribute.

### **2.3 Parameter Centralization**
We use a global `params.py` file. This central registry prevents "Magic Numbers" from appearing in the middle of code. If you want to change the initial battery from 0.5J to 1.0J, you change it in one variable, and it propagates across every mathematical calculation in the system.

---

## 3. Advanced Coding Techniques Used
### **3.1 Algebraic Heuristics (Efficiency)**
Instead of using computationally heavy AI libraries (like TensorFlow), we implemented our logic using **Pure Numerical Heuristics** (via NumPy).
- **Technique:** The **Utility Index ($U_i$)** is calculated as a vectorized operation. This allows us to process thousands of rounds in seconds rather than minutes.
- **Benefit:** The code can run on low-power teacher/student laptops while still delivering "PhD-grade" results.

### **3.2 Recursive Tree Construction**
During the **EBPT** phase, the code builds a Directed Acyclic Graph (DAG).
- **Technique:** The parent-selection logic uses a "Weighted Distance Search." It iterates through candidate nodes and evaluates them against the `Gamma` factor.
- **Parent Tracking:** Every node maintains a `parent` pointer. This allows for a simple recursive traversal when calculating total path energy.

### **3.3 Monte Carlo Seeding**
To ensure statistical validity, the code uses **Seed-Based Randomization**.
- **Technique:** We run the same experiment 30 times with different random seeds.
- **Aggregation:** The code automatically takes the Mean ($\mu$) and Standard Deviation ($\sigma$) of these 30 runs. This ensures that a single "lucky" run doesn't skew our claims of 1,021% improvement.

---

## 4. Technology Stack
- **Language:** Python 3.x (For its balance of readability and scientific library support).
- **Libraries:**
    - `NumPy` & `SciPy`: For high-speed matrix calculations and distance vectors.
    - `Matplotlib`: For generating the 10 core figures and heatmaps.
    - `python-pptx`: For the automated professional presentation generation.

---

## 5. Summary
The coding structure focuses on **Robustness and Reproducibility**. By separating the "Physics" (Energy) from the "Logic" (Routing), we've created a framework that isn't just a one-off script, but a professional simulation environment capable of rigorous academic verification.
