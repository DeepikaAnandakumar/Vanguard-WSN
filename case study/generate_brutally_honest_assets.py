import matplotlib.pyplot as plt
import pandas as pd
import os

# Create ppt directory if it doesn't exist
os.makedirs('ppt', exist_ok=True)

def save_table_as_image(data, filename, title, figsize=(10, 4)):
    fig, ax = plt.subplots(figsize=figsize)
    ax.axis('off')
    ax.axis('tight')
    
    table = ax.table(cellText=data.values, colLabels=data.columns, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.2, 2.5)
    
    # Styling
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor('#002060') # Deep Navy
        else:
            if data.iloc[row-1, 0] == 'Vanguard' or data.iloc[row-1, 0] == 'Deepika':
                cell.set_facecolor('#EBF1DE') # Soft Green highlight
            else:
                cell.set_facecolor('#F2F2F2')
                
    plt.title(title, fontsize=16, fontweight='bold', pad=20, color='#002060')
    plt.savefig(f'ppt/{filename}', bbox_inches='tight', dpi=300)
    plt.close()

# 1. Literature Survey Data
lit_data = pd.DataFrame([
    ['LEACH', 'Randomized', 'Single-Hop', 'High d^4 energy drain'],
    ['HEED', 'Probability/Iterative', 'Cluster-Based', 'High control overhead'],
    ['PEGASIS', 'Static Chain', 'Chain-Based', 'High latency / Bottlenecks'],
    ['Vanguard', 'Utility-Driven', 'Tree (EBPT)', 'Optimized (Self-Healing)']
], columns=['Protocol', 'Selection Logic', 'Routing', 'Major Weakness'])

save_table_as_image(lit_data, 'table4_literature_survey.png', 'Vanguard-WSN vs. Legacy Protocols')

# 2. Team Role Matrix Data
team_data = pd.DataFrame([
    ['Deepika', 'Lead Modeler', 'Utility Index (Ui) Math & Physics'],
    ['Gayatri', 'Performance Lead', 'Simulation Engine & Multi-hop Validation'],
    ['Aishvarya', 'Logic Architect', 'EBPT Tree Construction & DAG Logic'],
    ['Anjana', 'Data Specialist', 'Benchmarking vs God-Line & Metrics']
], columns=['Name', 'Role', 'Primary Contribution'])

save_table_as_image(team_data, 'table5_team_roles.png', 'Team Contribution Matrix')

# 3. Expanded Comparison Table (Table 2 v2)
comp_data = pd.DataFrame([
    ['LEACH', '97.3', '12,400', '9.8%', 'Unstable'],
    ['HEED', '142.0', '18,900', '14.3%', 'Heavily Burdened'],
    ['PEGASIS', '412.5', '54,200', '41.5%', 'High Latency'],
    ['Vanguard', '993.1', '118,500', '92.1%', 'Production Ready']
], columns=['Method', 'FND Round', 'Data Harvest', 'Optimality %', 'Verdict'])

save_table_as_image(comp_data, 'table2_expanded_verdict.png', 'Performance Benchmarking with Verdict')

print("Brutal Audit Assets Generated successfully in ppt/ folder.")
