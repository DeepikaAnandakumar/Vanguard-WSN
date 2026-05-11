#!/usr/bin/env python3
"""
Verify and calculate actual statistical tests for CH strategy comparison.
This script reads the actual experimental data and calculates t-tests and Cohen's d.
"""

import os
import sys
import json
import numpy as np
from scipy import stats
from statistics import mean, stdev

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def extract_fnd_from_json(json_path):
    """Extract FND from a seed JSON file."""
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Find first round where alive < initial count
    alive = data.get('alive_nodes', data.get('alive', []))
    if not alive:
        return None
    
    initial_count = alive[0] if alive else 50
    for i, count in enumerate(alive):
        if count < initial_count:
            return i
    return len(alive) - 1  # If never died, return last round

def extract_lnd_from_json(json_path):
    """Extract LND from a seed JSON file."""
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    alive = data.get('alive_nodes', data.get('alive', []))
    if not alive:
        return None
    
    for i, count in enumerate(alive):
        if count == 0:
            return i
    return len(alive) - 1  # If never fully died

def main():
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    
    # Read deterministic results
    det_fnds = []
    det_lnds = []
    det_dir = os.path.join(base_dir, 'master_results_safe', 'deterministic')
    for seed in range(10):
        json_path = os.path.join(det_dir, f'seed_{seed}.json')
        if os.path.exists(json_path):
            fnd = extract_fnd_from_json(json_path)
            lnd = extract_lnd_from_json(json_path)
            if fnd is not None:
                det_fnds.append(fnd)
            if lnd is not None:
                det_lnds.append(lnd)
    
    # Read energy_aware results
    ea_fnds = []
    ea_lnds = []
    ea_dir = os.path.join(base_dir, 'master_results_safe', 'energy_aware')
    for seed in range(10):
        json_path = os.path.join(ea_dir, f'seed_{seed}.json')
        if os.path.exists(json_path):
            fnd = extract_fnd_from_json(json_path)
            lnd = extract_lnd_from_json(json_path)
            if fnd is not None:
                ea_fnds.append(fnd)
            if lnd is not None:
                ea_lnds.append(lnd)
    
    print("="*80)
    print("STATISTICAL TEST VERIFICATION: Deterministic vs Energy-Aware")
    print("="*80)
    print(f"\nDeterministic FND: {det_fnds}")
    print(f"Energy-Aware FND: {ea_fnds}")
    print(f"\nDeterministic LND: {det_lnds}")
    print(f"Energy-Aware LND: {ea_lnds}")
    
    if len(det_fnds) >= 2 and len(ea_fnds) >= 2:
        # FND t-test
        t_stat_fnd, p_value_fnd = stats.ttest_ind(ea_fnds, det_fnds, equal_var=False)
        
        # FND Cohen's d
        pooled_std_fnd = np.sqrt((np.var(det_fnds, ddof=1) + np.var(ea_fnds, ddof=1)) / 2)
        cohens_d_fnd = (np.mean(ea_fnds) - np.mean(det_fnds)) / pooled_std_fnd if pooled_std_fnd > 0 else 0
        
        print(f"\n{'='*80}")
        print("FND (First Node Death) Statistical Tests:")
        print(f"{'='*80}")
        print(f"  Deterministic: {mean(det_fnds):.2f} ± {stdev(det_fnds):.2f}")
        print(f"  Energy-Aware:  {mean(ea_fnds):.2f} ± {stdev(ea_fnds):.2f}")
        print(f"  t-statistic:    {t_stat_fnd:.2f}")
        print(f"  p-value:        {p_value_fnd:.6f}")
        print(f"  Cohen's d:      {cohens_d_fnd:.2f}")
        print(f"  Significant:    {'YES' if p_value_fnd < 0.01 else 'NO'}")
    
    if len(det_lnds) >= 2 and len(ea_lnds) >= 2:
        # LND t-test
        t_stat_lnd, p_value_lnd = stats.ttest_ind(ea_lnds, det_lnds, equal_var=False)
        
        # LND Cohen's d
        pooled_std_lnd = np.sqrt((np.var(det_lnds, ddof=1) + np.var(ea_lnds, ddof=1)) / 2)
        cohens_d_lnd = (np.mean(ea_lnds) - np.mean(det_lnds)) / pooled_std_lnd if pooled_std_lnd > 0 else 0
        
        print(f"\n{'='*80}")
        print("LND (Last Node Death) Statistical Tests:")
        print(f"{'='*80}")
        print(f"  Deterministic: {mean(det_lnds):.2f} ± {stdev(det_lnds):.2f}")
        print(f"  Energy-Aware:  {mean(ea_lnds):.2f} ± {stdev(ea_lnds):.2f}")
        print(f"  t-statistic:    {t_stat_lnd:.2f}")
        print(f"  p-value:        {p_value_lnd:.6f}")
        print(f"  Cohen's d:      {cohens_d_lnd:.2f}")
        print(f"  Significant:    {'YES' if p_value_lnd < 0.01 else 'NO'}")
    
    print(f"\n{'='*80}")
    print("VERIFICATION COMPLETE")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()

