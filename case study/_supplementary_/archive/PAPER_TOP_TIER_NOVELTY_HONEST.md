# EBPT-CRA: Honest Novelty Statement and Evidence Summary

## Executive summary

This document is an "honest rewrite" of the novelty and claims made in the original top-tier draft. It restricts claims to statements supported by completed artifacts (50-node experiments with 30 seeds per configuration and the repository's theory sketches). Larger-scale experiments and a formal LaTeX proof write-up are explicitly noted as pending.

## What is validated (completed artifacts)

- Reproducible experimental suite for 50-node networks with 30 seeds per configuration. Aggregated results are in `top_tier_results/analysis_50nodes/summary.csv`.
- Pareto frontier computed on mean (FND, Jain fairness) from the completed runs; reported Pareto set includes `Baseline_deterministic`, `Baseline_random`, `Baseline_energy_aware`, `EBPT_Gamma_0.8`, and `Hybrid_AllFeatures`.
- Repository contains theory notes and proof sketches in `EBPT_CRA/theory/multi_objective.py` and appendix sketches in `DEMO_PAPER_Q1_COMPLETE.md`.

## Framing of contributions (evidence-backed)

1. Formalization & analysis (sketches + computational checks):
   - We present a formal multi-objective framing (lifetime vs fairness) and provide proof sketches linking greedy CH selection to submodular maximization. These are analytical sketches contained in the `theory` module; a formal LaTeX proof is planned.

2. Algorithms & empirical evaluation:
   - Adaptive parameter-tuning procedures and traffic-aware routing variants are implemented and evaluated empirically on the 50-node suite (30 seeds each). Results are reproducible via the scripts in `EBPT_CRA/scripts/`.

3. Empirical Pareto analysis:
   - We compute Pareto-optimal operating points from the completed experiments and provide guidance for choosing `γ` based on the empirical frontier.

## Key experimental numbers (50-node, 30 seeds — aggregated means ± std)

The following table reports validated aggregates from `top_tier_results/analysis_50nodes/summary.csv`.

| Algorithm | FND mean | FND std | Fairness mean | Fairness std |
|---|---:|---:|---:|---:|
| Baseline_deterministic | 81.2 | 18.438 | 0.9505 | 0.0183 |
| Baseline_random | 599.7667 | 24.7535 | 0.60747 | 0.07861 |
| Baseline_energy_aware | 632.5333 | 22.8922 | 0.49097 | 0.07469 |
| EBPT_Gamma_0.8 | 636.9667 | 25.0372 | 0.49053 | 0.10538 |
| Hybrid_AllFeatures | 629.5667 | 19.2653 | 0.49629 | 0.08659 |

Notes:
- All means and standard deviations above are computed from 30 independent seeds per configuration and are present in the repository CSV.
- The experimental claims in the paper should reference these exact aggregates (not rounded hype multipliers) and include the associated uncertainty.

## Theoretical statements — honest framing

- The repository contains a proof sketch arguing that, under simplifying modeling assumptions, greedy CH selection can be related to submodular maximization and therefore admits a (1-1/e)-style guarantee. This is presented as a sketch (see `EBPT_CRA/theory/multi_objective.py`).
- We present these as initial analytical results: useful intuition and a guide for experiments, but not as a finished formal proof. We will (a) complete a formal LaTeX proof, and (b) make explicit the assumptions required for the approximation statement.

## Limitations and open items (explicit)

- Scaling beyond 50 nodes: Larger-network (100–200 node) experiments are incomplete; no cross-size generalizations should be reported yet.
- Formal proofs: Theoretical claims in the draft beyond proof sketches must be completed before asserting definitive provable guarantees.
- Statistical claims: Where the draft used effect-size or synergy language, we recommend adding explicit hypothesis tests and effect-size reporting (Cohen's d) taken from seed-level data.

## Recommended edits to the manuscript

- Replace categorical "first/provably" language with phrases like "to our knowledge", "proof sketch", or "empirical evidence supports" where appropriate.
- Use the exact aggregate numbers from `top_tier_results/analysis_50nodes/summary.csv` in tables and figure captions, with ± std and N=30 indicated.
- Add a short "Limitations" paragraph in the Introduction and Conclusion noting incomplete scaling experiments and pending formal proofs.
- Keep the Pareto frontier figures and tables, but label them explicitly as computed from the 50-node runs.

## Suggested next actions (I can do these now)

- Apply the honest rewrite across `PAPER_TOP_TIER_NOVELTY.md` (in-place), replacing overstated claims. (I can do this and commit a patch.)
- Add an appendix section that extracts the proof sketches from `EBPT_CRA/theory/multi_objective.py` and labels them as sketches with TODO for full proofs.
- Run or re-run any statistical tests you want included (I can run scripts if you want me to execute the pipeline).

If you want, I will now (1) overwrite `PAPER_TOP_TIER_NOVELTY.md` with this honest text, or (2) apply targeted edits to the existing file leaving structure intact. Which do you prefer?
