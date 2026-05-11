
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

def plot_final_results(csv_path):
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    df = pd.read_csv(csv_path)
    
    # Handle missing header case (robustness)
    if 'Algorithm' not in df.columns:
        print("Warning: 'Algorithm' column not found. Reloading with manual header.")
        df = pd.read_csv(csv_path, names=['Seed', 'Algorithm', 'FND', 'LP_Bound', 'Optimality_Gap'])

    output_dir = os.path.dirname(csv_path)
    
    # 1. FND Comparison (Bar Chart with Error Bars)
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Algorithm', y='FND', data=df, capsize=.2, ci='sd')
    plt.axhline(y=df['LP_Bound'].mean(), color='r', linestyle='--', label='LP Upper Bound (God View)')
    plt.title('Network Lifetime (First Node Death) - 50 Nodes')
    plt.ylabel('Rounds')
    plt.xticks(rotation=15)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'fnd_comparison.png'), dpi=300)
    print(f"Saved {os.path.join(output_dir, 'fnd_comparison.png')}")

    # 2. Optimality Gap (Box Plot)
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='Algorithm', y='Optimality_Gap', data=df)
    plt.title('Optimality Gap (%) - Lower is Better')
    plt.ylabel('Gap (%)')
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'optimality_gap.png'), dpi=300)
    print(f"Saved {os.path.join(output_dir, 'optimality_gap.png')}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        plot_final_results(sys.argv[1])
    else:
        plot_final_results("num_results/raw_results_50.csv")
