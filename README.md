# Vanguard-WSN: A Utility-Driven Energy-Balanced Path Tree Framework for Maximizing Wireless Sensor Network Lifetime

## Project Overview

This repository contains the complete implementation of the Vanguard-WSN framework, a novel routing protocol for Wireless Sensor Networks (WSNs) that addresses the Energy Hole problem. The framework introduces a Composite Utility Index (Ui) for deterministic cluster head selection and an Energy-Balanced Path Tree (EBPT) with adaptive load-balancing to achieve near-theoretical network lifetime bounds.

### Key Features
- **Deterministic Utility-Based Selection**: Replaces random protocols with energy-aware cluster head selection.
- **Energy-Balanced Path Tree (EBPT)**: Adaptive multi-hop routing that prevents hotspot formation.
- **Comprehensive Simulations**: Tested on 50-node and 100-node networks with 30+ trials.
- **Benchmarking**: Compares against LEACH, HEED, PEGASIS, and theoretical LP-bounds.
- **Performance**: Achieves 92% of theoretical lifetime (R²=0.94), 10.21× FND improvement over LEACH.
- **Complexity**: O(N log N) time, suitable for low-power microcontrollers.

## Authors and Contributors
- **Deepika Anandakumar** (Lead Developer) - [DeepikaAnandakumar](https://github.com/DeepikaAnandakumar)
- **Aishvarya Govindaraju** (Collaborator) - [AishvairyaGovindaraju](https://github.com/AishvairyaGovindaraju)
- **Gayatri Kanagaraj** (Collaborator) - [GayaktriKanagaraj](https://github.com/GayaktriKanagaraj)
- **Anjana A** (Collaborator)

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Reproducibility](#reproducibility)
- [Project Structure](#project-structure)
- [Results](#results)
- [Contributing](#contributing)
- [License](#license)
- [References](#references)

## Installation

### Prerequisites
- Python 3.8+
- Required packages: `numpy`, `scipy`, `networkx`, `pandas`, `matplotlib`

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/DeepikaAnandakumar/Vanguard-WSN.git
   cd Vanguard-WSN
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running Simulations
Navigate to the EBPT_CRA directory and run experiments:

```bash
cd case study/EBPT_CRA
python scripts/run_num_experiments.py  # For 50-node simulations
```

For 100-node simulations, modify parameters in the scripts.

### Generating the Paper
Use the LaTeX generation scripts:

```bash
python create_ieee_latex.py
```

This produces the IEEE-formatted paper with embedded results.

## Reproducibility

Follow the detailed guide in [README_reproduce.md](case study/README_reproduce.md) for exact steps to reproduce simulation results, including LP-bounds and statistical tests.

### Key Scripts
- `run_num_experiments.py`: Main simulation runner.
- `analyze_results.py`: Statistical analysis and hypothesis testing.
- `generate_paper_data.py`: Data preparation for paper figures.

## Project Structure

```
Vanguard-WSN/
├── case study/
│   ├── EBPT_CRA/              # Core framework
│   │   ├── core/              # Network simulation core
│   │   ├── clustering/        # CH selection algorithms
│   │   ├── routing/           # Routing protocols (EBPT, LEACH, etc.)
│   │   ├── energy/            # Energy dissipation models
│   │   ├── theory/            # LP-bounds and proofs
│   │   ├── scripts/           # Experiment runners
│   │   └── simulation/        # Simulation utilities
│   ├── _supplementary_/       # Results and analysis
│   │   ├── top_tier_results/  # Simulation results (50/100 nodes)
│   │   └── num_results_final/ # Numerical results
│   ├── num_results/           # Raw simulation outputs
│   ├── ch_strategy_comparison/# Comparison results
│   └── README_reproduce.md    # Reproducibility guide
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Results

### Key Metrics (100-node Network)
- **First Node Death (FND)**: 993.1 rounds (vs. LEACH: 97.3)
- **Packet Success Ratio**: 98.4%
- **Fairness Index**: Adaptive balancing
- **Correlation with LP-Bound**: R²=0.94

See `_supplementary_/top_tier_results/` for full datasets.

### Figures
- Network stability curves
- Energy dissipation heatmaps
- Comparative death curves
- Pareto frontiers

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -m 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request.

### Collaborators
- Deepika Anandakumar
- Aishvarya Govindaraju
- Gayatri Kanagaraj

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## References

[1] Heinzelman, W. R., et al. (2000). Energy-efficient communication protocol for wireless microsensor networks. *Proceedings of the 33rd Hawaii International Conference on System Sciences*.

[2] Younis, O., & Fahmy, S. (2004). HEED: A hybrid, energy-efficient, distributed clustering approach for ad hoc sensor networks. *IEEE Transactions on Mobile Computing*.

[3] Lindsey, S., & Raghavendra, C. S. (2002). PEGASIS: Power-efficient gathering in sensor information systems. *Proceedings of IEEE Aerospace Conference*.

And additional references as in the paper.

---

For questions or issues, contact the authors via GitHub.