
import pandas as pd
import numpy as np
from scipy import stats
import sys
import os

def cohen_d(x, y):
    nx = len(x)
    ny = len(y)
    dof = nx + ny - 2
    return (np.mean(x) - np.mean(y)) / np.sqrt(((nx-1)*np.std(x, ddof=1) ** 2 + (ny-1)*np.std(y, ddof=1) ** 2) / dof)

def analyze_results(csv_path):
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    df = pd.read_csv(csv_path)
    
    # Handle missing header case (robustness)
    if 'Algorithm' not in df.columns:
        # Check if first row looks like data
        # Try reloading with explicit names
        print("Warning: 'Algorithm' column not found. Reloading with manual header.")
        df = pd.read_csv(csv_path, names=['Seed', 'Algorithm', 'FND', 'LP_Bound', 'Optimality_Gap'])
    
    # metrics: FND
    algorithms = df['Algorithm'].unique()
    baseline_algo = 'HEED_Clustered' # Primary baseline
    
    results = []
    
    print(f"Analysis for {csv_path}")
    print("-" * 60)
    print(f"{'Comparison':<40} | {'t-stat':<10} | {'p-value':<10} | {'Cohen-d':<10}")
    print("-" * 60)
    
    if baseline_algo not in algorithms:
        print(f"Baseline {baseline_algo} not found in data.")
        return

    base_data = df[df['Algorithm'] == baseline_algo]['FND']
    
    for algo in algorithms:
        if algo == baseline_algo:
            continue
            
        compare_data = df[df['Algorithm'] == algo]['FND']
        
        # Welch's t-test (equal_var=False)
        t_stat, p_val = stats.ttest_ind(compare_data, base_data, equal_var=False)
        d = cohen_d(compare_data, base_data)
        
        print(f"{algo} vs {baseline_algo:<15} | {t_stat:10.4f} | {p_val:10.4e} | {d:10.4f}")
        
        results.append({
            'Algorithm_A': algo,
            'Algorithm_B': baseline_algo,
            't_stat': t_stat,
            'p_value': p_val,
            'cohen_d': d
        })

    # Save to CSV
    out_df = pd.DataFrame(results)
    out_path = csv_path.replace('raw_results', 'hypothesis_tests')
    out_df.to_csv(out_path, index=False)
    print(f"\nSaved hypothesis tests to {out_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        analyze_results(sys.argv[1])
    else:
        # Default to 50 nodes if exists
        analyze_results("num_results/raw_results_50.csv")
