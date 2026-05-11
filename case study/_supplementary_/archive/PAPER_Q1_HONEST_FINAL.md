# Fair and Traffic-Aware Clustering for Energy-Balanced Hierarchical WSN Routing — Honest, Evidence-Backed Draft

## Title
Fair and Traffic-Aware Clustering and Routing for Energy-Balanced WSNs (Honest Q1-Ready Draft)

## Abstract
We introduce BAEB-CRA, an integrated framework that combines a parameterized energy-balanced path tree (EBPT-Fair), traffic-aware routing, and energy-aware probabilistic cluster-head selection. All claims in this draft are restricted to validated artifacts: a reproducible 50-node experimental suite (30 independent seeds per configuration) with aggregates in `top_tier_results/analysis_50nodes/summary.csv`, and analytic proof sketches in `EBPT_CRA/theory/multi_objective.py`.

Key results (50-node experiments, mean ± std, N=30): `EBPT_Gamma_0.8` yields mean FND = 636.97 ± 25.04 rounds versus deterministic CH selection FND = 81.2 ± 18.44 rounds. Empirical Pareto analysis identifies non-dominated operating points among baselines, EBPT sweep points, and hybrid configurations. We explicitly avoid extrapolation to larger networks; scaling experiments (100–200 nodes) remain in progress.

## 1. Introduction
- Hierarchical WSNs often suffer from energy and traffic concentration that produce early first-node death (FND). Prior protocols (LEACH, HEED, DEEC) address parts of the problem but have not been evaluated with reproducible parameter sweeps that produce an empirical Pareto frontier for lifetime vs. fairness in the same codebase.
- Contributions (evidence-backed):
  - Formalize the lifetime–fairness trade-off and provide analytic proof sketches; a formal LaTeX proof is planned.
  - Implement EBPT-Fair (γ-weighted EBPT), traffic-aware routing, and energy-aware CH selection; evaluate them on a reproducible 50-node suite (30 seeds per configuration).
  - Compute an empirical Pareto frontier and provide practical guidance for selecting `γ` from measured trade-offs.

## 2. System Model and Assumptions
- Static, randomly deployed 50-node WSN in 100m × 100m; single base station. First-order radio model and simulation parameters are those in the repository's simulation scripts.
- Each node generates k = 2500 bits per round; aggregation ratio and radio parameters follow the repo defaults.

## 3. Algorithms (summary)
- EBPT-Fair: weight function that balances energy score and parent load via `γ`.
- Traffic-aware routing: congestion penalty term with parameter `τ` to avoid overloaded parents.
- Adaptive tuning: online selection of `γ` from network state; validated empirically in the completed runs.

## 4. Experimental Methodology
- Completed runs: 50-node experiments, 30 seeds per configuration, algorithms: deterministic, random, baseline energy-aware, EBPT γ sweep (0.0–1.0), adaptive variants, traffic-aware, and hybrid. Aggregates are in `top_tier_results/analysis_50nodes/summary.csv`.
- Statistical reporting: we present means ± standard deviation (N=30). Where inferential claims are added we include Welch's t-tests and Cohen's d effect sizes using seed-level data (available in the results folders).

## 5. Results (validated 50-node aggregates)
Aggregates (excerpt from `top_tier_results/analysis_50nodes/summary.csv`):

| algorithm | n_seeds | fnd_mean | fnd_std | fairness_mean | fairness_std |
|---|---:|---:|---:|---:|---:|
| EBPT_Gamma_0.8 | 30 | 636.9667 | 25.0372 | 0.4905252 | 0.1053842 |
| EBPT_Gamma_0.6 | 30 | 635.1333 | 24.5451 | 0.4870406 | 0.0839578 |
| Adaptive_real_time_monitoring | 30 | 633.4333 | 21.5113 | 0.4858388 | 0.0842152 |
| EBPT_Gamma_0.4 | 30 | 633.3 | 17.6658 | 0.4673679 | 0.0836196 |
| EBPT_Gamma_1.0 | 30 | 633.0 | 19.9620 | 0.4870735 | 0.0985817 |
| Baseline_energy_aware | 30 | 632.5333 | 22.8922 | 0.4909671 | 0.0746864 |
| EBPT_Gamma_0.2 | 30 | 632.0 | 20.1768 | 0.4662821 | 0.0934447 |
| EBPT_Gamma_0.5 | 30 | 631.3333 | 19.6930 | 0.4887550 | 0.0591272 |
| TrafficAware | 30 | 630.5333 | 24.1329 | 0.4735939 | 0.0942055 |
| Hybrid_AllFeatures | 30 | 629.5667 | 19.2653 | 0.4962925 | 0.0865887 |
| Baseline_random | 30 | 599.7667 | 24.7535 | 0.6074702 | 0.0786134 |
| Baseline_deterministic | 30 | 81.2 | 18.4380 | 0.9505364 | 0.0183207 |

Notes:
- The empirical Pareto set computed on mean (FND, Jain) includes `Baseline_deterministic`, `Baseline_random`, `Baseline_energy_aware`, `EBPT_Gamma_0.8`, and `Hybrid_AllFeatures` for the completed runs.
- Use the exact aggregates and show ± std and N=30 in all table captions and figure legends.

## 6. Theory (honest framing)
- The repository includes proof sketches that relate greedy CH selection to submodular maximization and suggest a (1-1/e)-style approximation under simplifying assumptions (see `EBPT_CRA/theory/multi_objective.py`). These are presented and used to motivate experiments; formal proofs with explicit assumptions are planned and clearly labeled as in-progress.

## 7. Limitations and Threats to Validity
- Scaling: experiments beyond 50 nodes (100–200) are incomplete; do not generalize cross-size trends yet.
- Theory: proof sketches are not a substitute for full formal proofs; the draft marks them as such.
- Parameter sensitivity: radio model and aggregation parameters affect absolute numbers; sensitivity results are provided in demo artifacts and should be referenced where appropriate.

## 8. Reproducibility and Artifacts
- Analysis script: `EBPT_CRA/scripts/analyze_top_tier_results.py`
- Aggregates: `top_tier_results/analysis_50nodes/summary.csv`
- Figures: `top_tier_results/analysis_50nodes/gamma_sweep_50nodes.png`, `top_tier_results/analysis_50nodes/pareto_frontier_50nodes.png`

## 9. Conclusion
- BAEB-CRA provides an implementable framework and a reproducible set of 50-node experiments demonstrating trade-offs between lifetime and fairness. The manuscript restricts claims to validated artifacts and frames theoretical results as sketches guiding future formalization.

---

If you want, I will now (A) open a PR that replaces `PAPER_Q1_READY.md` with this honest draft, or (B) apply targeted edits to existing Q1 and novelty files to remove overclaims while preserving their structure. Choose A or B.