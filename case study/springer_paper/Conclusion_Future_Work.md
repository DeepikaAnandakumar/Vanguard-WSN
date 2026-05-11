# 7. Conclusion and Future Directions

## 7.1 Summary of Contributions
This paper presented Vanguard-WSN, a novel routing framework designed to challenge the "Energy Hole Problem" that has plagued Wireless Sensor Networks for two decades. Unlike legacy protocols that rely on probabilistic heuristics or greedy local optimization, Vanguard introduces a holistic, utility-driven approach to network management.

Our primary contribution, the **Energy-Balanced Path Tree (EBPT)**, successfully decouples the roles of sensing and relaying, assigning the burden of multi-hop communication only to those nodes most capable of bearing it. The simulation results confirm that this structural innovation yields a **10.21x increase in network stability (FND)** compared to the industry-standard LEACH protocol. Furthermore, by achieving a **94% correlation with the Theoretical God-Line**, Vanguard demonstrates that distributed algorithms can approximate global optimality without the need for computationally prohibitive linear programming solvers.

We conclude that for mission-critical applications—where the failure of a single node signifies the failure of the mission—Vanguard-WSN offers the most robust and sustainable architecture available in current literature.

## 7.2 Detailed Roadmap for Future Research

### 7.2.1 Integration with Mobile Sinks (UAVs)
The current implementation assumes a static Base Station. In future iterations, we propose deploying Unmanned Aerial Vehicles (UAVs) or autonomous ground robots as "Data Mules." By physically moving the sink to areas of high energy density (or low traffic), the network could theoretically achieve infinite lifetime, limited only by the UAV's flight time. We plan to extend the Utility Index ($U_i$) to account for "Sink Proximity Forecasts," allowing nodes to buffer data until a sink approach is imminent.

### 7.2.2 6G and Non-Terrestrial Networks (NTN)
With the advent of 6G and mega-constellations like Starlink and Kuiper, the role of WSNs is expanding beyond terrestrial limits. Future work will investigate **Direct-to-Satellite IoT** connectivity. Vanguard's clustering logic could be adapted to select "Super-CHs" capable of high-power uplink transmissions to Low Earth Orbit (LEO) satellites, bypassing terrestrial gateways entirely. This would enable truly global sensor networks in maritime or polar environments.

### 7.2.3 Cross-Layer Security via Blockchain
Centralized control introduces a single point of failure and a target for Denial-of-Service (DoS) attacks. We propose integrating a lightweight, permissioned blockchain (e.g., IOTA Tangle) onto the Cluster Heads. By recording routing metrics on an immutable ledger, the network could detect and isolate "Black Hole" attacks where malicious nodes advertise false energy levels to attract and drop packets.

### 7.2.4 Energy Harvesting Adaptation
Finally, the current model assumes a finite battery supply. We aim to adapt the $U_i$ function for **Energy Harvesting WSNs (EH-WSNs)** equipped with solar or piezoelectric harvesters. In such a scenario, a node's "utility" would be a function of its *energy intake rate* rather than just its residual capacity, fundamentally altering the optimal routing strategy from conservation to maximize throughput.
