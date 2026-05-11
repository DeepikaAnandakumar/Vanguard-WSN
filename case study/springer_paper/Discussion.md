# 6. Discussion

## 6.1 Implications for Industrial IoT (IIoT)
The transition from Industry 4.0 to Industry 5.0 relies heavily on the deployment of massive machine-type communications (mMTC). In factory automation, sensors are often embedded in rotating machinery or hazardous environments where battery replacement is not merely expensive but physically impossible. The results presented in Section 5 demonstrate that Vanguard-WSN is uniquely positioned to serve as the backbone for such IIoT deployments.

By extending the stability period by **10.21x**, Vanguard effectively extends the maintenance cycle of an industrial plant from months to years. For a factory with 1,000 sensors, the difference between replacing batteries every 6 months (LEACH) and every 5 years (Vanguard) translates into millions of dollars in operational savings (OPEX). Furthermore, the deterministic nature of the EBPT provides the reliability guarantees required for critical control loops, unlike the probabilistic jitter inherent in LEACH.

## 6.2 The Computation-Communication Trade-off
A central theme of this research is the trade-off between local computation and global communication. Legacy protocols minimize computation; LEACH requires only a random number generator ($O(1)$). Vanguard, conversely, requires sorting and utility calculation ($O(N \log N)$).

However, in modern silicon, "Computation is Cheap, Communication is Expensive." Transmitting a single bit over 100 meters consumes as much energy as executing approximately 3,000 instructions on an ARM Cortex-M0+ microcontroller. Vanguard exploits this asymmetry. We invest heavily in algorithmic intelligence—running complex sorting and selection logic at the controller—to save even a few transmissions. Our analysis shows that the energy "wasted" on overhead packets ($U_i$ reporting) is less than 0.5% of the energy saved by the optimized routing structure. This suggests that future WSN protocols should continue to shift the burden from the radio to the processor.

## 6.3 Scalability Analysis
While our simulations focused on a 100-node network, theoretical extrapolation suggests that Vanguard's performance scales super-linearly with density. As node density increases, the availability of high-utility relays increases, allowing the EBPT to find even more efficient paths.
-   **Sparse Networks ($N < 50$):** Vanguard degrades to Minimum Spanning Tree (MST) behavior.
-   **Dense Networks ($N > 200$):** The "Candidate Pool" for parents grows, improving load balancing precision.

However, scaling to $N > 1000$ would require partitioning the network into "Super-Clusters" to prevent the heartbeat phase from saturating the bandwidth. Future iterations of Vanguard could implement a hierarchical control plane to handle such massive scale.

## 6.4 Reliability in Harsh Environments
The "Self-Healing" capability observed in **Figure 9** (FND Snapshot) is critical for harsh environments. In a battlefield or disaster zone, nodes may be destroyed by external factors (fire, crushing, jamming) rather than battery depletion. Vanguard's stateless recovery—where a child simply picks the next best parent from its sorted list—ensures that the network is resilient to physical trauma. This contrasts with chain-based protocols like PEGASIS, where a single break requires a global "Chain Rebuilding" phase that leaves the network silent for seconds or minutes.
