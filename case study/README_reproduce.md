
# EBPT-CRA: Reproducibility Guide

This guide details the exact steps to reproduce the 50-node simulation results, including the Linear Programming (LP) Upper Bound comparison and statistical significance tests.

## Prerequisites
- Python 3.8+
- Required Libraries: `numpy`, `scipy`, `networkx`, `pandas`

## Directory Structure
Ensure your directory looks like this:
```
/case study
  /EBPT_CRA
    /core
    /clustering
    /routing
    /theory
    /scripts
  /num_results (Generated)
```

## Step 1: Run the Experiments
Execute the main simulation script. This will run 5 seeds for a 50-node network with a simulation limit of 5000 rounds.

**Command (PowerShell):**
```powershell
$env:PYTHONPATH=".\EBPT_CRA"; python EBPT_CRA/scripts/run_num_experiments.py
```

**What this does:**
1.  Calculates the LP Upper Bound using `scipy.optimize.linprog`.
2.  Runs the following algorithms:
    -   **HEED_Clustered**: Classic clustering baseline.
    -   **PEGASIS**: Chain-based routing baseline.
    -   **EBPT_Flat**: Distributed Gradient Routing (Proposed).
    -   **EBPT_Clustered**: Hybrid approach.
    -   **LEACH_EnergyAware**: Random clustering baseline.
3.  Saves raw per-seed results to `num_results/raw_results_50.csv`.
4.  Saves aggregated statistics to `num_results/num_results_50.json`.

## Step 2: Statistical Analysis
Once the experiments are complete (or even partially complete), run the analysis script to generate hypothesis tests (Welch's t-test) and effect sizes (Cohen's d).

**Command:**
```powershell
python EBPT_CRA/scripts/analyze_results.py num_results/raw_results_50.csv
```

**Output:**
-   Console table showing t-statistics, p-values, and Cohen's d for all algorithms vs. HEED.
-   `num_results/hypothesis_tests_50.csv`: Detailed statistical report.

## Step 3: Verify Claims
Check `num_results/num_results_50.json` and `num_results/hypothesis_tests_50.csv`.
-   **Optimality**: EBPT_Flat FND should be closer to the LP Bound (>60%) than HEED (~50%).
-   **Significance**: p-value for EBPT vs HEED should be < 0.05.

## Configuration
To modify experiment parameters (e.g., number of nodes, sensing range), edit `EBPT_CRA/core/params.py` or the `network_config` dictionary in `EBPT_CRA/scripts/run_num_experiments.py`.
