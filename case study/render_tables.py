import matplotlib.pyplot as plt
import pandas as pd
import os

def save_table_as_image(df, title, filename, col_widths=None):
    plt.figure(figsize=(10, len(df) * 0.6 + 1))
    plt.axis('off')
    plt.title(title, fontsize=14, pad=20, fontweight='bold')
    
    table = plt.table(cellText=df.values,
                      colLabels=df.columns,
                      cellLoc='center',
                      loc='center',
                      colWidths=col_widths)
    
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.2, 1.8)
    
    # Styling
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor('#40466e')
        else:
            cell.set_facecolor('#f1f1f2' if row % 2 == 0 else 'white')
            
    plt.savefig(filename, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"Saved: {filename}")

# Ensure ppt directory exists
os.makedirs('ppt', exist_ok=True)

# 1. Simulation Parameters
params_data = {
    "Parameter": [
        "Field Dimensions", "Number of Nodes (N)", "Initial Energy (E0)",
        "Data Packet Size", "Exter (Transmitter/Receiver)", "EDA (Aggregation)",
        "eps_fs (Free-space)", "eps_mp (Multi-path)", "Max Rounds"
    ],
    "Value": [
        "100m x 100m", "50 or 100", "0.5 J",
        "2000 bits", "50 nJ/bit", "5 nJ/bit/report",
        "10 pJ/bit/m^2", "0.0013 pJ/bit/m^4", "2000"
    ]
}
save_table_as_image(pd.DataFrame(params_data), "Table 1: Simulation Parameters", "ppt/table1_parameters.png")

# 2. Performance Comparison
perf_data = {
    "Algorithm": ["LEACH (Deterministic)", "LEACH (Energy-Aware)", "Vanguard-WSN (Proposed)"],
    "FND (Mean)": ["97.3", "970.6", "993.1"],
    "LND (Mean)": ["1000.0", "1000.0", "1000.0"],
    "Improvement": ["1.00x", "9.98x", "10.21x"],
    "Fairness": ["0.965", "0.136", "0.156"]
}
save_table_as_image(pd.DataFrame(perf_data), "Table 2: Performance Comparison (50 Nodes)", "ppt/table2_performance.png")

# 3. Ablation Study
ablation_data = {
    "Configuration": [
        "Deterministic Base", "Energy-Aware Only", 
        "EBPT + Adaptive Tuner", "EBPT + Traffic Awareness", 
        "Vanguard (All Features)"
    ],
    "FND (Mean)": ["97.3", "970.6", "989.1", "972.9", "993.1"],
    "Improvement": ["1.00x", "9.98x", "10.17x", "10.00x", "10.21x"]
}
save_table_as_image(pd.DataFrame(ablation_data), "Table 3: Ablation Study", "ppt/table3_ablation.png")

print("All tables generated successfully in the 'ppt' folder.")
