# Vanguard-WSN: Mathematical Formula Sheet
**The Core Equations of the EBPT-CRA Framework**

This document summarizes all the critical mathematical formulations used for selection, routing, and energy modeling in the project.

---

## 1. Node Selection Logic
### **1.1 The Utility Index ($U_i$)**
Used to evaluate the fitness of a node to act as a Cluster Head or Relay.
$$U_i = \alpha \cdot \frac{E_{res,i}}{E_{init}} + \beta \cdot \frac{N_{neigh,i}}{N_{max}}$$
*   **$E_{res,i}$**: Residual energy of node $i$.
*   **$N_{neigh,i}$**: Number of neighbors (local density).
*   **$\alpha, \beta$**: Weighting factors (typically $0.6$ and $0.4$).

### **1.2 The Elite Set ($\mathcal{S}_{elite}$)**
Nodes are only considered if they surpass the network average utility.
$$\mathcal{S}_{elite} = \{ n_i \mid U_i \geq \mu(U) \}$$

---

## 2. Energy-Balanced Path Tree (EBPT)
### **2.1 Parent Selection Criterion**
A node $i$ selects a parent $j$ from candidates $\mathcal{C}_i$ that are closer to the sink.
$$\text{Parent}(i) = \arg\max_{j \in \mathcal{C}_i} \left( E_{res,j} - \gamma \cdot \text{Load}_j \right)$$
*   **$\gamma$ (Gamma Factor)**: The "Fairness Knob" that balances energy usage vs. load distribution.
*   **$\text{Load}_j$**: The current number of child nodes relying on node $j$.

### **2.2 Acyclic Constraint**
To prevent loops, the candidate set is strictly distance-bounded:
$$\mathcal{C}_i = \{ n_j \mid \text{dist}(n_j, BS) < \text{dist}(n_i, BS) \}$$

---

## 3. First-Order Radio Energy Model
### **3.1 Transmission Cost ($E_{Tx}$)**
The cost to transmit a $k$-bit message over distance $d$:
$$E_{Tx}(k, d) = \begin{cases} k \cdot E_{elec} + k \cdot \epsilon_{fs} \cdot d^2, & d < d_0 \\ k \cdot E_{elec} + k \cdot \epsilon_{mp} \cdot d^4, & d \geq d_0 \end{cases}$$
*   **$E_{elec}$**: Electronics energy ($50\text{ nJ/bit}$).
*   **$\epsilon_{fs}$**: Free space model (low distance).
*   **$\epsilon_{mp}$**: Multi-path model (high distance).
*   **$d_0$**: Threshold distance ($87\text{ m}$).

### **3.2 Receiving Cost ($E_{Rx}$)**
The cost to receive a $k$-bit message:
$$E_{Rx}(k) = k \cdot E_{elec}$$

---

## 4. Performance Metrics
### **4.1 Network Stability (FND)**
$\text{Round of First Node Death}$. This is our primary KPI.

### **4.2 Jain’s Fairness Index ($J$)**
Measures how evenly energy is being depleted across the network.
$$J = \frac{(\sum E_{consumed,i})^2}{n \cdot \sum (E_{consumed,i}^2)}$$

### **4.3 Theoretical God-Line (LP Bound)**
Computed via Linear Programming to find the maximum possible lifetime for a specific topology:
$$\max \sum T_p \quad \text{s.t.} \quad \sum_p \text{cost}_{i,p} \cdot T_p \leq E_{init,i}$$
