"""
Theoretical Analysis Module for EBPT-CRA

Novel Contributions:
- Multi-objective optimization framework
- Theoretical bounds and approximation ratios
- Pareto frontier analysis
- Scalability proofs
"""

from theory.multi_objective import (
    MultiObjectiveOptimizer,
    ParetoPoint,
    prove_approximation_ratio,
    prove_scalability_bounds
)

__all__ = [
    'MultiObjectiveOptimizer',
    'ParetoPoint',
    'prove_approximation_ratio',
    'prove_scalability_bounds'
]

