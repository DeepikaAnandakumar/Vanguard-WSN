Fair and Traffic-Aware Clustering and Routing for Energy-Balanced WSNs
=====================================================================

## Abstract

We study the trade-off between network lifetime and energy-fairness in
hierarchical wireless sensor networks (WSNs) by extending an existing
Energy-Balanced Path Tree (EBPT) simulator with (i) a γ-parameterized
fairness term in the routing weight, (ii) optional traffic-aware
penalties, and (iii) simple adaptive controllers for γ. All claims in
this paper are restricted to completed, reproducible artifacts: a
50-node experiment suite with 30 independent seeds per configuration,
and a 100-node suite with the same algorithms and number of seeds. We
use these to compute empirical Pareto frontiers in the space of first
node death (FND) and Jain’s fairness index, and to characterize how
different algorithmic choices move along that frontier.

On 50-node networks, EBPT with energy-aware cluster-head selection and
γ-fair routing (EBPT-Fair) consistently achieves FND around 630–637
rounds (e.g., `EBPT_Gamma_0.8`: 636.97 ± 25.04 rounds, mean ± std,
N=30), versus 81.2 ± 18.44 rounds for a deterministic cluster-head
baseline. The empirical Pareto set for 50 nodes includes
`Baseline_deterministic`, `Baseline_random`, `Baseline_energy_aware`,
`EBPT_Gamma_0.8`, and `Hybrid_AllFeatures`. For 100-node networks, FND
for non-deterministic schemes remains in the 620–630 round range (e.g.,
`EBPT_Gamma_0.4`: 628.83 ± 15.25), while the deterministic baseline
degrades further (61.9 ± 13.22). We provide proof sketches for
approximation and scaling behavior in a separate theory module but
deliberately label them as sketches; all quantitative statements in this
paper are backed directly by the JSON/CSV artifacts in
`top_tier_results/`.

## 1 Introduction

### 1.1 Problem and setting

Hierarchical WSNs remain a standard architecture for large-scale
monitoring, but they are prone to **energy and traffic concentration**
around cluster heads and nodes near the base station. This often leads
to an early **First Node Death (FND)** even when total network energy
remains high. EBPT-style routing attempts to balance path cost using
residual energy and distance, but cluster-head selection and
intermediate routing decisions still have a large effect on where
traffic and energy are concentrated.

In this project we focus on a **single, well-instrumented simulator**
and ask:

- How do EBPT variants that incorporate explicit fairness and
  traffic-awareness behave on a common, reproducible benchmark?
- What lifetime–fairness trade-offs emerge empirically, and which
  operating points are Pareto-optimal?

Rather than claiming entirely new protocols, our goal is to provide a
**clean, reproducible empirical study** of these trade-offs within one
codebase, supported by initial theoretical sketches and transparent
limitations.

### 1.2 Contributions (evidence-backed)

This work makes the following contributions, all of which are directly
supported by the code and data in the repository:

1. **Empirical multi-objective study of EBPT-based routing.**  
   We extend an EBPT simulator with a γ-parameterized fairness term in
   the routing weight, traffic-aware penalties, and simple adaptive
   controllers, then run a reproducible 50-node × 30-seed and
   100-node × 30-seed experiment suite.

2. **Pareto-frontier characterization for lifetime vs fairness.**  
   Using `EBPT_CRA/scripts/analyze_top_tier_results.py` on the saved
   JSON outputs, we compute empirical Pareto frontiers (FND vs. Jain’s
   index) and identify non-dominated operating points among deterministic,
   random, energy-aware, EBPT-γ, adaptive, traffic-aware, and hybrid
   variants.

3. **Scaling snapshot from 50 to 100 nodes.**  
   Without extrapolating to larger sizes, we compare 50-node and
   100-node summaries for the same set of algorithms and show that
   EBPT-Fair and related variants maintain FND ≈ 620–640 rounds while
   fairness degrades as topology becomes denser.

4. **Theory sketches aligned with code.**  
   We provide a small theory helper module
   (`EBPT_CRA/theory/multi_objective.py`) that encodes the optimization
   problem, Pareto helper routines, and informal sketches of possible
   approximation and scaling results. We explicitly label these as
   *sketches* and avoid treating them as proved theorems in the paper.

Throughout, we emphasize **reproducibility**: every number in this paper
is traceable to `top_tier_results/results_50nodes.json`,
`results_100nodes.json`, and their analysis CSVs.

## 2 System model and assumptions

We adopt the system model already implemented in the EBPT-CRA simulator:

- **Topology:** Static, randomly deployed WSN in a 100 m × 100 m field,
  with a single base station at the center.
- **Nodes:** Homogeneous energy budget (e.g. 0.5 J per node for the
  top-tier runs), with optional heterogeneity disabled in the main
  experiments.
- **Radio model:** Standard first-order radio model, with
  \( E_{\mathrm{TX}}(k,d) = k(E_{\mathrm{elec}} + \varepsilon_{\mathrm{fs}} d^2) \)
  for the distances considered, and
  \( E_{\mathrm{RX}}(k) = k E_{\mathrm{elec}} \). Parameters follow
  `core/params.py`.
- **Traffic model:** Each node generates a fixed-sized packet per round
  (e.g. 2500 bits), cluster heads aggregate with a fixed compression
  ratio, and there is no packet loss or interference.
- **Lifetime metrics:** we record **FND** (first node death), **HND**
  (half nodes dead), and **LND** (last node death), but focus primarily
  on FND as the main lifetime metric.
- **Fairness metric:** Jain’s fairness index over a per-node `load`
  measure derived from forwarded bits, as implemented in
  `core/network.py`.

These assumptions are typical for first-order WSN studies and are made
explicit here to avoid overclaiming generality.

## 3 Algorithms

We briefly summarize the algorithmic components; full code is in the
`EBPT_CRA` package.

### 3.1 EBPT and EBPT-Fair (γ-weighted)

The EBPT routing baseline computes a rooted tree toward the base station
by ordering nodes by distance to the BS and, for each node, selecting a
parent among the BS and nodes closer to the BS. The parent is chosen to
maximize an energy-aware weight (see `routing/ebpt_weight.py`), and
children lists are maintained for traversal.

EBPT-Fair introduces a **fairness parameter γ** into the weight:

- Parent candidacy and selection use a weight that combines residual
  energy, distance, and a load term.  
- The γ parameter controls how strongly existing `load` is penalized in
  the weight, making heavily loaded parents less attractive when
  γ > 0.

Different γ values (0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0) define different
EBPT-Fair configurations in the experiment suite
(`EBPT_Gamma_0.0` … `EBPT_Gamma_1.0`).

### 3.2 Cluster-head strategies and baselines

We evaluate three main cluster-head (CH) strategies:

- **Baseline_deterministic:** deterministic ID-based CH selection, used
  only as a weak baseline to highlight how bad simple choices can be.
- **Baseline_random:** per-node CH selection with fixed probability, no
  energy-awareness.
- **Baseline_energy_aware:** energy-weighted probabilistic CH selection,
  already studied in the separate EBPT-CRA paper; here it serves as a
  stronger internal baseline.

These are combined with EBPT(-Fair) routing and additional options below
to form a grid of algorithms.

### 3.3 Traffic-aware and hybrid variants

`routing/traffic_aware_enhanced.py` adds an **experimental traffic term**
to the EBPT weight:

- A simple `TrafficModel` tracks historical traffic load per node and
  produces a congestion level in [0,1].
- The final weight for a candidate parent divides the EBPT-Fair energy
  score by \( 1 + \tau \cdot \mathrm{Congestion} \), where τ is a
  traffic weight parameter.

We evaluate:

- **TrafficAware:** EBPT-Fair with traffic-awareness enabled and a
  fixed τ.
- **Hybrid_AllFeatures:** EBPT-Fair with both traffic-awareness and
  a simple adaptive controller that can adjust γ/traffic weight based
  on a coarse network state.

The purpose of these variants is to probe how such tweaks move points
along the empirical Pareto frontier; we do not claim they are globally
optimal or entirely novel compared to all prior traffic-aware routing.

## 4 Experimental methodology

All main results are produced by the following pipeline:

1. **Run simulations:**  
   `EBPT_CRA/scripts/run_top_tier_experiments.py` with:

   - 50 and 100 nodes,
   - 30 seeds per algorithm,
   - 1000-round cap per simulation,
   - the experiment set defined in that script (baselines, γ sweep,
     adaptive, traffic-aware, hybrid).

   This yields `top_tier_results/results_50nodes.json` and
   `results_100nodes.json`.

2. **Analyze aggregates:**  
   `EBPT_CRA/scripts/analyze_top_tier_results.py` with:

   - `--input top_tier_results/results_50nodes.json --outdir top_tier_results/analysis_50nodes`
   - `--input top_tier_results/results_100nodes.json --outdir top_tier_results/analysis_100nodes`

   This script:

   - Recomputes mean/std from per-seed data,
   - Writes `summary.csv`,
   - Produces γ-sweep and Pareto-frontier PNGs,
   - Writes `hypothesis_tests.csv` with pairwise Welch tests and
     Cohen’s d for FND.

3. **Figures and tables:**  
   The paper directly reads from `summary.csv` and
   `hypothesis_tests.csv` for tables and significance statements and
   references the generated PNGs for figures.

We report all lifetime metrics as **mean ± standard deviation** over
30 seeds. For inferential statements we rely on Welch’s t-tests from the
analysis script and report p-values qualitatively (e.g., p < 10⁻¹²) when
effects are extremely strong.

## 5 Results: 50-node experiments

Table 1 summarizes the 50-node, 30-seed results from
`top_tier_results/analysis_50nodes/summary.csv` for the most relevant
algorithms.

**Table 1 – 50-node lifetime and fairness (N=30, mean ± std).**

| algorithm                  | FND (rounds)    | Jain fairness       |
|---------------------------|-----------------|---------------------|
| Baseline_deterministic    | 81.20 ± 18.44   | 0.951 ± 0.018       |
| Baseline_random           | 599.77 ± 24.75  | 0.607 ± 0.079       |
| Baseline_energy_aware     | 632.53 ± 22.89  | 0.491 ± 0.075       |
| EBPT_Gamma_0.2            | 632.00 ± 20.18  | 0.466 ± 0.093       |
| EBPT_Gamma_0.4            | 633.30 ± 17.67  | 0.467 ± 0.084       |
| EBPT_Gamma_0.5            | 631.33 ± 19.69  | 0.489 ± 0.059       |
| EBPT_Gamma_0.6            | 635.13 ± 24.55  | 0.487 ± 0.084       |
| EBPT_Gamma_0.8            | 636.97 ± 25.04  | 0.491 ± 0.105       |
| EBPT_Gamma_1.0            | 633.00 ± 19.96  | 0.487 ± 0.099       |
| Adaptive_real_time_monitoring | 633.43 ± 21.51 | 0.486 ± 0.084   |
| Adaptive_balanced         | 629.27 ± 25.88  | 0.443 ± 0.084       |
| Adaptive_long_term_coverage | 628.63 ± 23.41 | 0.464 ± 0.085    |
| TrafficAware              | 630.53 ± 24.13  | 0.474 ± 0.094       |
| Hybrid_AllFeatures        | 629.57 ± 19.27  | 0.496 ± 0.087       |

### 5.1 Lifetime improvements and baselines

The deterministic CH baseline performs poorly: FND ≈ 81 rounds, with a
relatively small standard deviation but an extremely low absolute
lifetime. All non-deterministic strategies (random, energy-aware,
EBPT-Fair, adaptive, traffic-aware, hybrid) yield FND in a narrow band
around 630–637 rounds.

From `hypothesis_tests.csv`:

- Comparisons between `Baseline_deterministic` and any EBPT/energy-aware
  variant yield enormous t-statistics (|t| ≫ 50) and p-values far below
  10⁻¹², confirming that **the improvement over the deterministic
  baseline is statistically overwhelming**.
- Comparisons among the EBPT-Fair γ values (0.2, 0.4, 0.5, 0.6, 0.8,
  1.0) have small |t|-values and p-values well above 0.05, indicating
  that **within this band, no single γ is clearly superior in FND** at
  50 nodes.

In other words, once we move away from deterministic CHs, the choice of
γ in [0.2, 0.8] only mildly perturbs FND, while fairness varies more
noticeably.

### 5.2 Empirical Pareto frontier (50 nodes)

Using the Pareto logic in `analyze_top_tier_results.py`, we identify the
set of non-dominated points in the (fairness, FND) plane. For 50 nodes,
the empirical Pareto set includes:

- `Baseline_deterministic`: very high fairness, but extremely low FND.
- `Baseline_random`: improved FND at the cost of fairness.
- `Baseline_energy_aware`: high FND with moderate fairness.
- `EBPT_Gamma_0.8`: the best FND among EBPT-Fair points, with similar
  fairness to other γ in [0.4, 1.0].
- `Hybrid_AllFeatures`: slightly lower FND than `EBPT_Gamma_0.8` but
  slightly higher fairness.

These points are highlighted in
`top_tier_results/analysis_50nodes/pareto_frontier_50nodes.png`, which
plots mean FND vs mean fairness with error bars.

### 5.3 Fairness behavior

Fairness (Jain’s index) ranges from ≈0.44 to ≈0.95 across algorithms.
Qualitatively:

- Deterministic CHs are **very fair** in terms of residual-energy
  distribution, but this comes with an unacceptable sacrifice in
  lifetime.
- Random and energy-aware baselines sit in a mid-range of fairness,
  with `Baseline_random` exhibiting the highest fairness among
  non-deterministic schemes.
- EBPT-Fair γ sweeps and the hybrid variants cluster around fairness
  ≈ 0.46–0.50, illustrating that **lifetime improvements can be
  obtained without collapsing fairness**, but also that fine-grained
  tuning of γ shifts fairness more than it shifts FND in this regime.

## 6 Results: scaling snapshot to 100 nodes

To begin addressing scaling behavior, we repeat the same experiment grid
for **100-node networks** and analyze
`top_tier_results/analysis_100nodes/summary.csv`.

**Table 2 – 100-node lifetime and fairness (N=30, mean ± std).**

| algorithm               | FND (rounds)    | Jain fairness       |
|------------------------|-----------------|---------------------|
| Baseline_deterministic | 61.90 ± 13.22   | 0.954 ± 0.013       |
| Baseline_random        | 566.23 ± 26.83  | 0.463 ± 0.078       |
| Baseline_energy_aware  | 620.10 ± 18.30  | 0.362 ± 0.079       |
| EBPT_Gamma_0.0         | 624.07 ± 25.92  | 0.344 ± 0.072       |
| EBPT_Gamma_0.2         | 624.77 ± 24.08  | 0.343 ± 0.082       |
| EBPT_Gamma_0.4         | 628.83 ± 15.25  | 0.379 ± 0.081       |
| EBPT_Gamma_0.5         | 628.30 ± 17.95  | 0.389 ± 0.092       |
| EBPT_Gamma_0.6         | 627.07 ± 15.77  | 0.364 ± 0.079       |
| EBPT_Gamma_0.8         | 618.97 ± 18.63  | 0.343 ± 0.075       |
| EBPT_Gamma_1.0         | 622.57 ± 14.56  | 0.333 ± 0.070       |
| Adaptive_balanced      | 627.80 ± 16.27  | 0.374 ± 0.079       |
| Adaptive_long_term_coverage | 625.97 ± 16.75 | 0.354 ± 0.077  |
| Adaptive_real_time_monitoring | 624.87 ± 14.88 | 0.354 ± 0.088 |
| TrafficAware           | 622.83 ± 17.52  | 0.364 ± 0.092       |
| Hybrid_AllFeatures     | 627.40 ± 15.28  | 0.368 ± 0.079       |

### 6.1 Cross-size trends (50 → 100 nodes)

Comparing Tables 1 and 2, we observe:

- **Deterministic baseline:** FND decreases from 81.2 ± 18.44 (50 nodes)
  to 61.9 ± 13.22 (100 nodes), while fairness stays ≈0.95. As the
  network grows, deterministic CHs become even less acceptable in
  lifetime terms.
- **Non-deterministic schemes:** FND for random, energy-aware, EBPT-Fair
  γ, adaptive, traffic-aware, and hybrid variants remains in a narrow
  566–637 round band at 50 nodes and 566–629 at 100 nodes. In other
  words, **FND does not collapse** when doubling the network size from
  50 to 100 for these algorithms.
- **Fairness:** fairness decreases for non-deterministic schemes when
  going from 50 to 100 nodes (e.g., `Baseline_energy_aware`: 0.491 →
  0.362; `Baseline_random`: 0.607 → 0.463; EBPT-Fair γ variants all
  move downward). This is consistent with increased contention and more
  skewed traffic structures in larger topologies.

From `analysis_100nodes/hypothesis_tests.csv`, the γ-sweep results again
show:

- Strong, highly significant improvements in FND for any EBPT-based
  variant versus `Baseline_deterministic`.
- No statistically significant FND differences among EBPT-Fair γ values
  in [0.0, 0.6] at 100 nodes; only γ=0.8 shows a modest degradation in
  FND with p ≈ 0.03 when compared to γ=0.4.

The 100-node Pareto frontier (see
`analysis_100nodes/pareto_frontier_50nodes.png`) includes
`Baseline_deterministic`, `Baseline_random`, `EBPT_Gamma_0.4`, and
`EBPT_Gamma_0.5`, mirroring the 50-node behavior but with an overall
shift toward lower fairness values.

### 6.2 Limitations of scaling evidence

We deliberately **do not extrapolate** beyond 100 nodes:

- 150- and 200-node comprehensive runs are not yet fully vetted and are
  not used here.
- The scaling heuristics in `theory/multi_objective.py` are treated as
  sketches, not empirical facts.

The safe conclusion from the current data is that, for this simulator
and parameter set, EBPT-Fair-style algorithms **maintain high FND in
both 50- and 100-node networks**, while fairness degrades with size;
deterministic CH selection is unacceptable at either size.

## 7 Theory sketches and alignment

The theory helper module
`EBPT_CRA/theory/multi_objective.py` contains:

- A formal multi-objective problem *statement* for FND and fairness.
- Utilities for computing empirical Pareto frontiers and γ-selection
  from experimental data.
- Two explicit **sketches**:
  - An approximation-ratio sketch that borrows the structure of
    submodular maximization arguments.
  - A scalability sketch that hypothesizes \( \mathrm{FND}(n) \approx
    \Theta(n^\alpha) \) under certain topologies.

We stress:

- These are **not proved theorems** for the concrete, dynamic model
  implemented in the simulator.
- The code comments have been updated to mark them as sketches and to
  describe the missing assumptions that would need to be established
  (e.g., definition and submodularity of a lifetime set function).

The role of these sketches in the paper is strictly to **motivate**
experiments and to outline directions for future formal work; all
concrete numerical claims come from the JSON/CSV artifacts described
earlier.

## 8 Limitations and threats to validity

We summarize the main limitations explicitly:

- **Baselines outside this codebase.**  
  We do not implement or compare against classic WSN protocols such as
  HEED, PEGASIS, TLEACH, or more recent (post-2020) hierarchical
  schemes. All baselines are **internal** to this codebase
  (deterministic, random, energy-aware, EBPT-Fair, adaptive,
  traffic-aware, hybrid). As a result, we make no performance claims
  relative to the broader literature.

- **Network sizes.**  
  The fully validated experiment suites are for **50** and **100**
  nodes. While the infrastructure supports larger sizes, we do not use
  incomplete 150/200-node runs in this paper and avoid extrapolating
  trends beyond 100 nodes.

- **Traffic and channel model.**  
  Traffic is deterministic and uniform; the radio model does not include
  fading, interference, or realistic MAC behavior. This is adequate for
  isolating algorithmic effects in a first-order setting but limits the
  ecological validity.

- **Fairness metric.**  
  We use Jain’s index on a load proxy defined in `core/network.py`.
  Other notions of fairness (e.g., energy-weighted or application-level
  metrics) are not explored here.

- **Absence of formal proofs.**  
  All theoretical content is work-in-progress and presented as sketches.
  We do not rely on any unproved bound for our conclusions.

These limitations mean that, while the **internal comparison and
reproducibility** are strong, the **novelty and breadth of validation**
remain modest relative to the very top-tier standards discussed in the
earlier brutal evaluation document.

## 9 Reproducibility and artifacts

To reproduce all numbers and figures in this paper:

1. Install Python and the dependencies listed in `requirements.txt`.
2. From the repository root, run:

   ```bash
   # 50-node and 100-node experiment suites (already run in this repo)
   python EBPT_CRA/scripts/run_top_tier_experiments.py --sizes 50 100 --seeds 30 --output top_tier_results

   # Analysis for 50 nodes
   python EBPT_CRA/scripts/analyze_top_tier_results.py \
       --input top_tier_results/results_50nodes.json \
       --outdir top_tier_results/analysis_50nodes \
       --expected-seeds 30

   # Analysis for 100 nodes
   python EBPT_CRA/scripts/analyze_top_tier_results.py \
       --input top_tier_results/results_100nodes.json \
       --outdir top_tier_results/analysis_100nodes \
       --expected-seeds 30
   ```

3. The key artifacts used in this paper are then:

   - `top_tier_results/analysis_50nodes/summary.csv`
   - `top_tier_results/analysis_50nodes/hypothesis_tests.csv`
   - `top_tier_results/analysis_50nodes/gamma_sweep_50nodes.png`
   - `top_tier_results/analysis_50nodes/pareto_frontier_50nodes.png`
   - `top_tier_results/analysis_100nodes/summary.csv`
   - `top_tier_results/analysis_100nodes/hypothesis_tests.csv`
   - `top_tier_results/analysis_100nodes/gamma_sweep_50nodes.png`
   - `top_tier_results/analysis_100nodes/pareto_frontier_50nodes.png`

Every table entry and qualitative claim in Sections 5–6 is traceable to
these files.

## 10 Conclusion

We have presented a carefully instrumented, fully reproducible empirical
study of EBPT-based hierarchical WSN routing under fairness and
traffic-aware extensions. On 50-node and 100-node networks, a broad
family of EBPT-Fair, adaptive, traffic-aware, and hybrid configurations
achieve FND around 620–640 rounds, dramatically improving over a naive
deterministic CH baseline, while spanning a range of fairness values.
The empirical Pareto frontiers at 50 and 100 nodes highlight internal
trade-offs among these variants and provide practical guidance for
choosing γ and related parameters in this specific simulator.

We deliberately **do not** claim fundamental algorithmic breakthroughs
or new theorems. Instead, the value of this work lies in its **honest
alignment between code, data, and text**, and in the fact that all
results can be reproduced by running a small number of clearly
documented scripts. Future work includes implementing external baselines
(e.g., HEED, PEGASIS, TLEACH, recent IoT routing schemes), extending the
experiment suite to larger networks and more realistic traffic/channel
models, and turning the theory sketches in `theory/multi_objective.py`
into fully proved, assumption-explicit theorems.

