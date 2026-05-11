# Brutal Evaluation — Project & Manuscript

This document is a concise, unvarnished evaluation of the project and the honest manuscript (`PAPER_Q1_HONEST_FINAL.md`). It prioritizes severity and fix actions.

## A. High-confidence strengths
- Reproducibility: The repo contains scripts, raw per-seed outputs, and aggregated CSVs for the 50-node suite. Aggregates are consistent and available.
- Experimental rigor (50-node): N=30 seeds per configuration is sufficient for descriptive inference and supports mean±std reporting.
- Pareto analysis: The pipeline computes Pareto frontier figures and aggregates, which are present and reproducible.
- Code & analysis integration: Analysis scripts are present to regenerate plots and CSVs.

## B. Critical issues (must-fix before top-tier submission)
1. Ambiguous theory vs. proof: The repository contains proof sketches but no self-contained formal proofs with explicit assumptions. Claiming definitive provable guarantees is unjustified. Fix: complete LaTeX proofs and include an assumptions section; until then, label these items as "sketch".
2. Mixed manuscript versions: Multiple paper files in the repo contain inconsistent claims and numbers (some claim 15 seeds / different FND values, others 30 seeds). Fix: consolidate to a single Q1-ready honest draft and remove or archive outdated drafts.
3. Statistical reporting gaps: The draft uses means±std but several claims refer to effect sizes and synergy without formal hypothesis tests. Fix: add Welch's t-tests and Cohen's d to analysis outputs and include p-values and CIs for key comparisons; deposit the seed-level CSV in supplementary material.
4. Scaling claims: The repo contains references to 100–200 node results; these are incomplete. Do not report cross-size trends until validated runs complete. Fix: either run the larger experiments or remove cross-size claims.
5. Figure provenance: Some figure captions refer to files outside the repository relative paths. Ensure all figure files used in the manuscript are in `top_tier_results/analysis_50nodes/` or `demo_results/plots/` and referenced with relative paths.

## C. Medium issues (important but not blocking)
1. Narrative "first" claims: The manuscript frequently uses "first" or absolute novelty language. Replace with "to our knowledge" or remove when prior work exists.
2. Terminology clarity: Define metrics early (FND, HND, LND); ensure consistent notation across manuscript and code.
3. Proof-of-concept reproducibility README: Add a minimal `README_reproduce.md` with step-by-step commands to reproduce the 50-node aggregates and figures.

## D. Recommended prioritized remedial plan (ordered)
1. Consolidate paper drafts: Replace `PAPER_Q1_READY.md` and `PAPER_TOP_TIER_NOVELTY.md` with honest versions or add clear header pointers to `PAPER_Q1_HONEST_FINAL.md` and `PAPER_TOP_TIER_NOVELTY_HONEST.md` (already created). (1 day)
2. Formalize theory: Complete LaTeX proofs for the approximation claim and explicitly state assumptions; include in appendix. (2–5 days depending on complexity)
3. Add statistical outputs: Modify `analyze_top_tier_results.py` or run a script to compute Welch's t-test, Cohen's d, and 95% CIs for key comparisons; add `results/stats/hypothesis_tests.csv`. (0.5–1 day)
4. Validate scaling plan: Either run the 100–200 node experiments (compute resource dependent) or remove scaling claims from the manuscript. If resources are available, run batched experiments with N=30 seeds per config and update aggregates. (variable — 1–3 days on local machine)
5. Add reproducibility README and a one-click script (PowerShell) that runs the analysis pipeline and generates figures. (0.5 day)
6. Final editorial pass: ensure all figures and numbers match CSVs, remove all "first" claims unless supported, and add limitations. (0.5–1 day)

## E. Minimal code patches to prioritize (suggested)
- `core/controller.py`: ensure `gamma` and routing parameters are passed from controller state into tree-building calls (search for hardcoded gamma or magic constants).
- `EBPT_CRA/scripts/analyze_top_tier_results.py`: append functions to compute Welch t-tests, Cohen's d, and write `hypothesis_tests.csv`.

## F. Possible risks and mitigation
- Risk: Larger-scale runs may change the Pareto frontier or relative ordering. Mitigation: mark scaling as future work and avoid claims until completed.
- Risk: Formal proof fails under realistic assumptions. Mitigation: present the strongest version of the proof under clearly stated assumptions, and present empirical validation as complementary evidence.

## G. Suggested commit plan
1. Commit 1: Add `PAPER_Q1_HONEST_FINAL.md` and `PAPER_TOP_TIER_NOVELTY_HONEST.md` (done).
2. Commit 2: Add `README_reproduce.md` with exact commands to regenerate `summary.csv` and figures.
3. Commit 3: Update analysis script to output hypothesis tests and effect sizes; regenerate figures and CSVs.
4. Commit 4: Add LaTeX appendix with full proofs (or clearly labeled proofs-in-progress if not complete).

## H. Verdict (brutal)
- Paper readiness for top-tier: **Not yet**. The 50-node artifacts are strong and reproducible, but the manuscript over-claimed theory and scaling in places. Fix the items above (theory formalization, consolidate drafts, add statistical tests, and either run scaling experiments or remove scaling claims). After these fixes, the submission would be in a defensible state.

---

I can (1) apply the recommended small code patches, (2) add the reproducibility README, and (3) run the analysis to produce hypothesis tests and updated CSVs. Which of these should I do next?