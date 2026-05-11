Table 1:
| Feature Classification | LEACH (2000) | HEED (2004) | PEGASIS (2002) | Vanguard-WSN (Proposed) |
| Primary Objective | Load Rotation | Energy balancing | Distance Minimization | Utility Maximization |
| Selection Logic | Probabilistic T(n) | Iterative Energy Probability. | Greedy Closest Neighbour | Deterministic Composite |
| Topology Structure | Star (Single-Hop) | Star/Cluster | Linear Chain | Energy-Balanced Path Tree (EBPT) |
| Heterogeneity | None (Homogeneous) | Initial Energy Only | None | Adaptive Traffic & Energy Aware |
| Computational Cost | Very Low O(1) | High (message flood) | Medium (chain build) | Low (O(N) distributed) |
| Failure Recovery | None (Wait for round) | Iterative Re-cluster | Full Re-build | Local Self-Healing (O(1)) |
| Scalability | Poor (<100m) | Medium | Poor (High Delay) | High (Multi hop capable) |

Table 2:
| Parameter | Value | Description |
| Network Size |  | Monitoring field dimensions |
| Node Count ( N ) |  | Number of sensor nodes |
| Base Station |  | Centrally located sink |
| Initial Energy  ) |  | Battery capacity per node |
| Control Packet Size |  | Overhead messages () |
| Data Packet Size |  | Sensed data payload |
|  |  | Electronics energy (Tx/Rx) |
|  |  | Free-space amplifier coefficient () |
|  |  | Multipath amplifier coefficient () |
|  |  | Data aggregation cost |
| Seeds |  | Random seeds for statistical averaging |

Table 3:
| Metric | LEACH | HEED | PEGASIS | Vanguard-WSN | Improvement (%) |
| FND (Rounds) | 97.3 ± 4 | 210.5 ± 12 | 145.2 ± 8 | 993.1 ± 15 | 1,021% |
| HND (Rounds) | 115.2 ± 3 | 245.8 ± 10 | 310.4 ± 15 | 1,150.4 ± 20 | 998% |
| Fairness (J) | 0.96 | 0.68 | 0.55 | 0.15 | Trade-off |
| Total Packets | 12,400 | 28,500 | 18,900 | 118,500 | 955% |
| Throughput (kbps) | 4.2 | 8.1 | 6.5 | 42.3 | 907% |

