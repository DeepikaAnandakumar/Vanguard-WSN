
import json
import os
import numpy as np

RESULTS_DIR = '../paper_results' # Relative to submission_paper/

def calculate_stats():
    stats = {}
    if not os.path.exists('paper_results'):
        # Just in case we run it from root
        if os.path.exists('EBPT_CRA/scripts/paper_results'):
             RESULTS_DIR = 'EBPT_CRA/scripts/paper_results'
        else:
             # Try to find it
             pass

    # Actually I know where they are: c:/Users/Lenovo/OneDrive/Desktop/6TH SEM/case study/case study/EBPT_CRA/paper_results
    # Let's use absolute path for safety in this script
    BASE_DIR = r"c:/Users/Lenovo/OneDrive/Desktop/6TH SEM/case study/case study/EBPT_CRA/paper_results"
    
    algorithms = ['Vanguard', 'LEACH-MultiHop', 'HEED-MultiHop', 'PEGASIS']
    
    print("| Algorithm | FND (Mean) | FND (Std) | LND (Mean) | LND (Std) |")
    print("|---|---|---|---|---|")
    
    for algo in algorithms:
        path = os.path.join(BASE_DIR, f"{algo}.json")
        if not os.path.exists(path):
            continue
            
        with open(path, 'r') as f:
            data = json.load(f)
            
        fnds = []
        lnds = []
        
        for seed_data in data:
            # First Node Death: First round with < N nodes
            # Alive nodes array
            alive = seed_data['alive']
            rounds = seed_data['rounds']
            total_nodes = alive[0]
            
            fnd = -1
            lnd = -1
            
            for r, a in zip(rounds, alive):
                if a < total_nodes and fnd == -1:
                    fnd = r
                if a == 0 and lnd == -1:
                    lnd = r
            
            if fnd == -1: fnd = rounds[-1] # Survived all
            if lnd == -1: lnd = rounds[-1]
            
            fnds.append(fnd)
            lnds.append(lnd)
            
        fnd_mean = np.mean(fnds)
        fnd_std = np.std(fnds)
        lnd_mean = np.mean(lnds)
        lnd_std = np.std(lnds)
        
        print(f"| {algo} | {fnd_mean:.1f} | {fnd_std:.1f} | {lnd_mean:.1f} | {lnd_std:.1f} |")

if __name__ == "__main__":
    calculate_stats()
