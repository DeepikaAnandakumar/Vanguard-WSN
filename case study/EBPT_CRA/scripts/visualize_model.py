
import matplotlib.pyplot as plt
import networkx as nx
import os

OUTPUT_DIR = 'submission_paper/paper_assets'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def draw_system_model():
    G = nx.DiGraph()
    
    # Nodes
    # BS at top
    pos = {
        'BS': (0.5, 0.9),
        'CH1': (0.2, 0.6),
        'CH2': (0.8, 0.6),
        'N1': (0.1, 0.3),
        'N2': (0.3, 0.3),
        'N3': (0.7, 0.3),
        'N4': (0.9, 0.3)
    }
    
    # Edges (Data Flow)
    edges = [
        ('N1', 'CH1'), ('N2', 'CH1'), 
        ('N3', 'CH2'), ('N4', 'CH2'),
        ('CH1', 'BS'), ('CH2', 'BS')
    ]
    
    G.add_edges_from(edges)
    
    plt.figure(figsize=(8, 6))
    
    # Draw Nodes
    nx.draw_networkx_nodes(G, pos, nodelist=['BS'], node_color='#ff4444', node_size=3000, label='Base Station')
    nx.draw_networkx_nodes(G, pos, nodelist=['CH1', 'CH2'], node_color='#44aa44', node_size=2000, label='Cluster Heads')
    nx.draw_networkx_nodes(G, pos, nodelist=['N1', 'N2', 'N3', 'N4'], node_color='#4444ff', node_size=1000, label='Sensor Nodes')
    
    # Draw Edges
    nx.draw_networkx_edges(G, pos, width=2, arrowsize=20, edge_color='#666666')
    
    # Labels
    nx.draw_networkx_labels(G, pos, font_size=12, font_color='white', font_weight='bold')
    
    plt.title("Vanguard-WSN System Model (Hierarchical Flow)", fontsize=14)
    plt.legend(scatterpoints=1)
    plt.axis('off')
    
    out_path = os.path.join(OUTPUT_DIR, 'system_model.png')
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    print(f"Saved {out_path}")
    plt.close()

if __name__ == "__main__":
    draw_system_model()
