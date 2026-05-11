import json
import os
import pandas as pd
import numpy as np
from scipy import stats
from theory.multi_objective import MultiObjectiveOptimizer

def analyze_top_tier(results_dir='top_tier_results'):
    """
    Perform deep analysis on top-tier experimental results.
    """
    comp_file = f'{results_dir}/comprehensive_results.json'
    if not os.path.exists(comp_file):
        print(f"Error: {comp_file} not found.")
        return

    with open(comp_file, 'r') as f:
        data = json.load(f)

    optimizer = MultiObjectiveOptimizer()
    
    print("\n" + "="*60)
    print("TOP-TIER RIGOROUS ANALYSIS")
    print("="*60)

    for size_key, size_data in data['experiments'].items():
        print(f"\n--- Network Size: {size_key} ---")
        
        # 1. Pareto Frontier
        size_list = []
        for name, stats_data in size_data.items():
            size_list.append({
                'name': name,
                'fnd': stats_data['fnd_mean'],
                'fairness': stats_data['fairness_mean']
            })
        
        frontier = optimizer.compute_pareto_frontier(size_list)
        print(f"Pareto Optimal Configurations: {[p.gamma for p in frontier]}")

        # 2. Hypothesis Testing: Hybrid vs Baseline_energy_aware
        hybrid = size_data.get('Hybrid_AllFeatures')
        baseline = size_data.get('Baseline_energy_aware')
        
        if hybrid and baseline:
            h_fnds = [r['fnd'] for r in hybrid['results']]
            b_fnds = [r['fnd'] for r in baseline['results']]
            
            t_stat, p_val = stats.ttest_ind(h_fnds, b_fnds, equal_var=False)
            
            # Cohen's d
            pooled_std = np.sqrt((np.std(h_fnds)**2 + np.std(b_fnds)**2) / 2)
            cohens_d = (np.mean(h_fnds) - np.mean(b_fnds)) / pooled_std if pooled_std > 0 else 0
            
            print(f"Hybrid vs Baseline (FND):")
            print(f"  Improvement: {np.mean(h_fnds) / np.mean(b_fnds):.2f}x")
            print(f"  Welch's t: {t_stat:.4f}, p-value: {p_val:.4e}")
            print(f"  Cohen's d: {cohens_d:.2f} ({'Large' if abs(cohens_d)>0.8 else 'Medium' if abs(cohens_d)>0.5 else 'Small'} effect)")

        # 3. Synergy Analysis
        adaptive = size_data.get('Adaptive_balanced')
        traffic = size_data.get('TrafficAware')
        
        if all([hybrid, adaptive, traffic, baseline]):
            imp_hybrid = hybrid['fnd_mean'] - baseline['fnd_mean']
            imp_adaptive = adaptive['fnd_mean'] - baseline['fnd_mean']
            imp_traffic = traffic['fnd_mean'] - baseline['fnd_mean']
            
            synergy = imp_hybrid - (imp_adaptive + imp_traffic)
            print(f"Synergy Metric: {synergy:.2f} rounds surplus (Hybrid vs Sum of Individual Improvements)")

if __name__ == '__main__':
    analyze_top_tier()
