"""Parameter sweep over DATA_BITS and INITIAL_ENERGY.

Produces:
 - results_sweep/run_YYYYMMDD_HHMMSS/
   - per-config subfolders with aggregated metrics and plots
   - summary CSV/JSON with FND/HND/LND means and stds per config
"""
import argparse
import datetime
import json
import os
import statistics
import shutil

# ensure project root in path when invoked from scripts/
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.run_experiments import run_seed, aggregate
import core.params as params

import matplotlib.pyplot as plt


def run_grid(data_bits_list, energy_list, seeds, rounds, out_root):
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    run_root = os.path.join(out_root, f'run_{ts}')
    os.makedirs(run_root, exist_ok=True)

    summary = []

    for db in data_bits_list:
        for ie in energy_list:
            label = f'db{db}_ie{ie}'
            print('Running config:', label)
            cfg_dir = os.path.join(run_root, label)
            os.makedirs(cfg_dir, exist_ok=True)
            all_metrics = []

            # override params for this config
            params.DATA_BITS = db
            params.INITIAL_ENERGY = ie

            for s in range(seeds):
                seed = s
                m = run_seed(seed, rounds, num_nodes=50, field_x=100, field_y=100, bs_pos=(50,50), out_dir=cfg_dir, stop_on_fnd=False)
                all_metrics.append(m)

            agg = aggregate(all_metrics, rounds)

            # Save per-config aggregated JSON/CSV
            agg_json = os.path.join(cfg_dir, 'agg_metrics.json')
            with open(agg_json, 'w') as f:
                json.dump(agg, f, indent=2)

            # extract lifetime summary (FND/HND/LND)
            fnd = agg.get('FND', {})
            hnd = agg.get('HND', {})
            lnd = agg.get('LND', {})

            summary.append({'DATA_BITS': db, 'INITIAL_ENERGY': ie,
                            'FND_mean': fnd.get('mean'), 'FND_std': fnd.get('std'), 'FND_count': fnd.get('count'),
                            'HND_mean': hnd.get('mean'), 'HND_std': hnd.get('std'), 'HND_count': hnd.get('count'),
                            'LND_mean': lnd.get('mean'), 'LND_std': lnd.get('std'), 'LND_count': lnd.get('count')})

            # basic plot: alive mean
            plt.figure()
            plt.plot(agg['rounds'], agg['alive_mean'])
            plt.xlabel('Round')
            plt.ylabel('Alive Nodes')
            plt.title(f'Alive nodes - {label}')
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(os.path.join(cfg_dir, 'alive_nodes_vs_rounds.png'))
            plt.close()

            plt.figure()
            plt.plot(agg['rounds'], agg['energy_mean'])
            plt.xlabel('Round')
            plt.ylabel('Total Residual Energy (J)')
            plt.title(f'Energy - {label}')
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(os.path.join(cfg_dir, 'energy_vs_rounds.png'))
            plt.close()

    # write summary CSV and JSON
    import csv
    csv_path = os.path.join(run_root, 'sweep_summary.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['DATA_BITS', 'INITIAL_ENERGY', 'FND_mean', 'FND_std', 'FND_count', 'HND_mean', 'HND_std', 'HND_count', 'LND_mean', 'LND_std', 'LND_count'])
        for row in summary:
            writer.writerow([row['DATA_BITS'], row['INITIAL_ENERGY'], row['FND_mean'], row['FND_std'], row['FND_count'], row['HND_mean'], row['HND_std'], row['HND_count'], row['LND_mean'], row['LND_std'], row['LND_count']])

    with open(os.path.join(run_root, 'sweep_summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)

    print('Sweep complete. Results in', run_root)
    return run_root


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=str, default='results_sweep')
    parser.add_argument('--seeds', type=int, default=10)
    parser.add_argument('--rounds', type=int, default=2000)
    args = parser.parse_args()

    data_bits_list = [2500, 10000, 50000, 200000]
    energy_list = [1.0, 0.5, 0.25]

    run_grid(data_bits_list, energy_list, seeds=args.seeds, rounds=args.rounds, out_root=args.out)
