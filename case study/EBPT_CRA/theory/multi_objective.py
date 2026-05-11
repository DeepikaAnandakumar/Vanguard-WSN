"""
Multi-objective analysis helpers for WSN lifetime–fairness trade-offs.

This module provides a **pragmatic analysis and optimization helper layer**
around the trade-off between network lifetime (FND) and fairness (Jain's
Index), driven primarily by **empirical results** from the simulator.

Important:
- This is **not** a complete or formal theory paper on its own.
- All "theorems" below should be read as **sketches / intended bounds**
  whose assumptions still need to be fully formalized and proved in LaTeX.
- The only fully validated artifacts today are the empirical Pareto
  frontiers and summaries computed from the 50-node and 100-node
  experiments in `top_tier_results/`.
"""

import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass


@dataclass
class ParetoPoint:
    """Represents a point on the Pareto frontier"""
    fnd: float
    fairness: float
    gamma: float
    alpha: float  # Weight in combined objective


class MultiObjectiveOptimizer:
    """
    Multi-objective helper for WSN lifetime–fairness trade-offs.

    This class is intentionally lightweight. It:
    1. Provides a concrete optimization problem *formulation*.
    2. Computes an empirical Pareto frontier from experimental data.
    3. Offers informal/theoretical *sketches* of bounds we would like to
       prove rigorously in a separate LaTeX appendix.
    4. Implements simple parameter-selection utilities (e.g., γ choice)
       based on already-computed frontiers.

    It does **not** by itself establish new theorems; instead, it keeps
    code and analysis aligned with the honest manuscript, which treats
    all theory as work-in-progress sketches.
    """
    
    def __init__(self):
        self.pareto_frontier: List[ParetoPoint] = []
        self.theoretical_bounds_cache = {}
    
    def formulate_optimization_problem(self, network_state: Dict) -> Dict:
        """
        Formulate the multi-objective optimization problem:
        
        Maximize: α·FND + (1-α)·Jain's_Index
        Subject to: 
          - Network connectivity constraints
          - Energy conservation constraints
          - Fairness lower bound: J ≥ J_min
        
        Returns:
            Dictionary with problem formulation
        """
        problem = {
            'objective': 'maximize',
            'variables': ['gamma', 'ch_probability', 'routing_weights'],
            'constraints': {
                'connectivity': 'all nodes must have path to BS',
                'energy_conservation': 'sum(energy_consumed) ≤ sum(initial_energy)',
                'fairness_lower_bound': 'Jain_index ≥ 0.7'  # Application-dependent
            },
            'parameters': {
                'alpha': 'weight between lifetime and fairness [0, 1]',
                'gamma': 'fairness parameter in routing [0, 1]',
                'ch_probability': 'cluster head selection probability [0, 1]'
            }
        }
        return problem
    
    def compute_pareto_frontier(self, experimental_data: List[Dict]) -> List[ParetoPoint]:
        """
        Compute Pareto frontier from experimental data.
        
        A point (FND_i, J_i) is Pareto-optimal if:
        - No other point has both FND > FND_i AND J > J_i
        - Or no other point has FND ≥ FND_i AND J > J_i (with at least one strict)
        
        Args:
            experimental_data: List of dicts with keys 'fnd', 'fairness', 'gamma'
        
        Returns:
            List of Pareto-optimal points
        """
        if not experimental_data:
            return []
        
        # Sort by FND (descending)
        sorted_data = sorted(experimental_data, key=lambda x: x['fnd'], reverse=True)
        
        pareto_points = []
        max_fairness_so_far = -1
        
        for point in sorted_data:
            fnd = point['fnd']
            fairness = point['fairness']
            gamma = point.get('gamma', 0.0)
            
            # Check if this point is Pareto-optimal
            # (dominates or is not dominated by any existing point)
            is_pareto = True
            for existing in pareto_points:
                # Existing point dominates this one
                if existing.fnd >= fnd and existing.fairness >= fairness:
                    if existing.fnd > fnd or existing.fairness > fairness:
                        is_pareto = False
                        break
                # This point dominates existing
                elif fnd >= existing.fnd and fairness >= existing.fairness:
                    if fnd > existing.fnd or fairness > existing.fairness:
                        # Remove dominated point (will be handled by rebuilding list)
                        pass
            
            if is_pareto:
                # Check if this point improves max fairness
                if fairness > max_fairness_so_far:
                    max_fairness_so_far = fairness
                    pareto_points.append(ParetoPoint(
                        fnd=fnd,
                        fairness=fairness,
                        gamma=gamma,
                        alpha=0.5  # Default, can be optimized
                    ))
        
        # Final cleanup: remove dominated points
        final_pareto = []
        for p in pareto_points:
            dominated = False
            for q in pareto_points:
                if p != q:
                    if q.fnd >= p.fnd and q.fairness >= p.fairness:
                        if q.fnd > p.fnd or q.fairness > p.fairness:
                            dominated = True
                            break
            if not dominated:
                final_pareto.append(p)
        
        # Sort by FND for visualization
        final_pareto.sort(key=lambda x: x.fnd, reverse=True)
        self.pareto_frontier = final_pareto
        return final_pareto
    
    def theoretical_bounds(self, network_size: int, initial_energy: float) -> Dict:
        """
        Calculates theoretical bounds for FND and fairness based on network parameters.
        
        Formula for FND Upper Bound:
          FND_max = (Total Energy) / (Avg Energy per Round)
          where Avg Energy per Round assumes optimal multi-hop routing (LP Bound).
        """
        # Improved approximation based on LP God-View
        e_tx_avg = 50e-9 + 10e-12 * (50**2) # Heuristic avg cost
        total_e = network_size * initial_energy
        data_rate = 2000 # bits/round/node
        
        fnd_upper_bound = total_e / (network_size * data_rate * e_tx_avg)
        
        bounds = {
            'fnd_upper_bound': {
                'value': fnd_upper_bound,
                'formula': 'FND ≤ (n · E_init) / (n · k · E_TX_avg)',
                'explanation': 'Hard energy limit based on network-wide dissipation'
            },
            'fairness_lower_bound': {
                'formula': 'J ≥ 1/n',
                'explanation': 'Worst-case fairness where 1 node does all work'
            },
            'approximation_ratio': {
                'value': 0.632,
                'formula': '1 - 1/e',
                'explanation': 'Proven ratio for submodular greedy maximization'
            }
        }
        
        self.theoretical_bounds_cache = bounds
        return bounds
    
    def optimal_gamma_selection(self, target_fairness: Optional[float] = None, 
                                 target_fnd: Optional[float] = None,
                                 alpha: float = 0.5) -> float:
        """
        Select optimal gamma parameter for given objectives.
        
        If target_fairness is specified, find gamma that achieves it while
        maximizing FND.
        
        If target_fnd is specified, find gamma that achieves it while
        maximizing fairness.
        
        If alpha is specified, optimize combined objective:
        maximize: α·FND + (1-α)·fairness
        
        Args:
            target_fairness: Desired fairness value (Jain's index)
            target_fnd: Desired FND value
            alpha: Weight in combined objective (0 = pure fairness, 1 = pure lifetime)
        
        Returns:
            Optimal gamma value
        """
        if not self.pareto_frontier:
            # Default if no data available
            return 0.5
        
        if target_fairness is not None:
            # Find point closest to target fairness with highest FND
            best_point = None
            best_fnd = -1
            for point in self.pareto_frontier:
                if abs(point.fairness - target_fairness) < 0.05:  # Within 5%
                    if point.fnd > best_fnd:
                        best_fnd = point.fnd
                        best_point = point
            if best_point:
                return best_point.gamma
        
        if target_fnd is not None:
            # Find point closest to target FND with highest fairness
            best_point = None
            best_fairness = -1
            for point in self.pareto_frontier:
                if abs(point.fnd - target_fnd) < 10:  # Within 10 rounds
                    if point.fairness > best_fairness:
                        best_fairness = point.fairness
                        best_point = point
            if best_point:
                return best_point.gamma
        
        # Optimize combined objective
        best_point = None
        best_score = -1.0
        for point in self.pareto_frontier:
            score = alpha * point.fnd + (1 - alpha) * point.fairness
            if score > best_score:
                best_score = score
                best_point = point
        
        if best_point is not None:
            return best_point.gamma
        
        # Absolute fallback if frontier is empty but somehow passed first check
        return 0.5
    
    def characterize_trade_off(self, experimental_data: List[Dict]) -> Dict:
        """
        Characterize the trade-off curve between lifetime and fairness.
        
        Returns:
            Dictionary with:
            - trade_off_curve: List of (FND, fairness) points
            - optimal_gamma_range: Range of gamma values for different objectives
            - synergy_metric: Quantification of how components work together
        """
        if not experimental_data:
            return {}
        
        # Group by gamma and compute statistics
        gamma_groups = {}
        for data in experimental_data:
            gamma = data.get('gamma', 0.0)
            if gamma not in gamma_groups:
                gamma_groups[gamma] = {'fnd': [], 'fairness': []}
            gamma_groups[gamma]['fnd'].append(data['fnd'])
            gamma_groups[gamma]['fairness'].append(data['fairness'])
        
        # Compute trade-off curve
        trade_off_curve = []
        for gamma in sorted(gamma_groups.keys()):
            fnd_mean = np.mean(gamma_groups[gamma]['fnd'])
            fairness_mean = np.mean(gamma_groups[gamma]['fairness'])
            trade_off_curve.append({
                'gamma': gamma,
                'fnd': fnd_mean,
                'fairness': fairness_mean
            })
        
        # Find optimal gamma range
        optimal_gamma_range = {
            'max_fnd': max(trade_off_curve, key=lambda x: x['fnd'])['gamma'],
            'max_fairness': max(trade_off_curve, key=lambda x: x['fairness'])['gamma'],
            'balanced': self.optimal_gamma_selection(alpha=0.5)
        }
        
        return {
            'trade_off_curve': trade_off_curve,
            'optimal_gamma_range': optimal_gamma_range,
            'pareto_frontier': [{'fnd': p.fnd, 'fairness': p.fairness, 'gamma': p.gamma} 
                               for p in self.pareto_frontier]
        }


def prove_approximation_ratio(network_size: int) -> Dict:
    """
    Return a **proof sketch** for a putative approximation ratio.

    Intended theorem (not yet fully proved for this exact model):

        "Under an appropriate static set-function formulation of the
        lifetime objective, greedy energy-aware CH selection could be
        shown to achieve

            FND_alg ≥ (1 - 1/e) · FND_optimal

        by appealing to standard submodular-maximization results."

    Caveats:
    - We have **not** fully defined the lifetime set function nor
      proved submodularity for the dynamic, per-round model implemented
      in the simulator.
    - Therefore, this function must be treated strictly as a structured
      proof **sketch**, not as a finished theorem.

    Returns:
        Dictionary with the informal statement and its high-level steps.
    """
    return {
        'theorem': 'Sketch: greedy energy-aware CH selection could be (1-1/e)-approximate under additional assumptions',
        'approximation_ratio': 1 - 1/np.e,  # ≈ 0.632
        'proof_sketch': [
            '1. Formulate CH selection as submodular maximization problem',
            '2. Lifetime function is submodular (diminishing returns property)',
            '3. Greedy algorithm for submodular maximization achieves (1-1/e) approximation',
            '4. Energy-aware selection is a greedy algorithm',
            '5. Therefore, approximation ratio holds'
        ],
        'implication': 'If all assumptions hold and submodularity is proved, the algorithm would be within 63% of optimal lifetime'
    }


def prove_scalability_bounds(network_size: int, density: float) -> Dict:
    """
    Sketch possible scalability behavior for large networks.

    Intended qualitative statement (not yet rigorously derived):

      For a network with n nodes and density δ we *expect*:
        - FND to scale on the order of n^α for some α depending on
          topology and traffic, with α ≈ 0.5 for grid-like deployments
          and α ≈ 0.6–0.7 for certain random deployments.

    This is based on standard intuitions about tree depth, hop counts,
    and radio-energy models; it is **not** a proved theorem for the
    exact EBPT-CRA implementation.

    Returns:
        Dictionary with the hypothesized scaling exponent and comments.
    """
    # Simplified bounds (can be made rigorous with graph theory)
    if density > 0.1:  # Dense network
        alpha = 0.5  # Grid-like scaling
    else:  # Sparse network
        alpha = 0.7  # Random topology scaling
    
    return {
        'theorem': 'Sketch: FND scales as O(n^α) for network size n under suitable topology/traffic assumptions',
        'scaling_exponent': alpha,
        'formula': f'FND(n) ≈ Θ(n^{alpha}) (heuristic fit)',
        'implication': f'For 2× network size, a naive fit would predict FND increasing by a factor ~{2**alpha:.2f}',
        'validation': 'Currently only modest empirical checks (e.g., 50- and 100-node runs); no 500-node validation yet'
    }

