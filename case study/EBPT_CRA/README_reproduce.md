Reproducing the 50-node analysis

This file describes how to reproduce the validated 50-node aggregates and hypothesis tests used in the honest manuscript.

Prerequisites
- Python 3.8+ installed and on PATH
- Packages: numpy, scipy, matplotlib, pandas
  You can install with:

```powershell
python -m pip install -r requirements.txt
```

Quick commands (PowerShell)

```powershell
# From repository root
python EBPT_CRA/scripts/analyze_top_tier_results.py --input top_tier_results/results_50nodes.json --outdir top_tier_results/analysis_50nodes --expected-seeds 30
```

Outputs created
- `top_tier_results/analysis_50nodes/summary.csv` (aggregated means ± std)
- `top_tier_results/analysis_50nodes/gamma_sweep_50nodes.png`
- `top_tier_results/analysis_50nodes/pareto_frontier_50nodes.png`
- `top_tier_results/analysis_50nodes/hypothesis_tests.csv` (pairwise Welch t-tests and Cohen's d for FND)

Notes
- If you want to re-run the full simulations, run `EBPT_CRA/scripts/run_top_tier_experiments.py` (this can be time-consuming). The analysis script reads the saved `results_50nodes.json` artifacts and performs recomputation and hypothesis testing without re-running simulations.
