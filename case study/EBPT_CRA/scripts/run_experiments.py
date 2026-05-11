"""Run multi-seed experiments and aggregate metrics.

Usage:
  python scripts/run_experiments.py --seeds 10 --rounds 200

Produces per-seed metrics in `results/` and aggregated files:
 - results/agg_metrics.json
 - results/agg_metrics.csv
 - results/avg_energy.png
 - results/avg_alive.png

This script imports the `Network` class and exercises the same API as `main.py` without changing core behavior.
"""
import argparse
import json
import os
import statistics
import random
import sys
from collections import defaultdict

# Ensure project root is on path so imports work when run from scripts/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import matplotlib.pyplot as plt

from core.network import Network


def run_seed(seed, rounds, num_nodes, field_x, field_y, bs_pos, out_dir, stop_on_fnd=False):
    random.seed(seed)

    network = Network(num_nodes, field_x, field_y, bs_pos)
    network.build()

    for r in range(rounds):
        network.run_round()
        if network.reconfiguration_needed():
            network.build()
        network.log_metrics(r)
        if stop_on_fnd and getattr(network.metrics, 'first_node_death', None) is not None:
            # stop early when FND occurs
            break

    out = {
        'seed': seed,
        'rounds': network.metrics.rounds,
        'alive_nodes': network.metrics.alive_nodes,
        'total_energy': network.metrics.total_energy,
        'dead_nodes': getattr(network.metrics, 'dead_nodes', []),
        'num_chs': getattr(network.metrics, 'num_chs', []),
        'jains_index': getattr(network.metrics, 'jains_index', []),
        'avg_hops': getattr(network.metrics, 'average_hop_count', []),
        'first_node_death': getattr(network.metrics, 'first_node_death', None),
        'half_node_death': getattr(network.metrics, 'half_node_death', None),
        'last_node_death': getattr(network.metrics, 'last_node_death', None),
    }

    fname = os.path.join(out_dir, f'metrics_seed_{seed}.json')
    with open(fname, 'w') as f:
        json.dump(out, f, indent=2)

    return out


def aggregate(all_metrics, rounds):
    # Create per-round lists
    alive_by_round = defaultdict(list)
    energy_by_round = defaultdict(list)
    num_chs_by_round = defaultdict(list)
    jain_by_round = defaultdict(list)
    hops_by_round = defaultdict(list)

    fnd_list = []
    hnd_list = []
    lnd_list = []

    for m in all_metrics:
        for i in range(rounds):
            alive = m['alive_nodes'][i] if i < len(m['alive_nodes']) else m['alive_nodes'][-1]
            energy = m['total_energy'][i] if i < len(m['total_energy']) else m['total_energy'][-1]
            alive_by_round[i].append(alive)
            energy_by_round[i].append(energy)
            
            # collect number of CHs if available
            if 'num_chs' in m and m['num_chs']:
                num_ch = m['num_chs'][i] if i < len(m['num_chs']) else m['num_chs'][-1]
            else:
                num_ch = None
            num_chs_by_round[i].append(num_ch)
            
            # collect jain's index if available
            if 'jains_index' in m and m['jains_index']:
                j = m['jains_index'][i] if i < len(m['jains_index']) else m['jains_index'][-1]
            else:
                j = None
            jain_by_round[i].append(j)

            # collect avg hops if available
            if 'avg_hops' in m and m['avg_hops']:
                h = m['avg_hops'][i] if i < len(m['avg_hops']) else m['avg_hops'][-1]
            else:
                h = None
            hops_by_round[i].append(h)

        if m.get('first_node_death') is not None:
            fnd_list.append(m['first_node_death'])
        if m.get('half_node_death') is not None:
            hnd_list.append(m['half_node_death'])
        if m.get('last_node_death') is not None:
            lnd_list.append(m['last_node_death'])

    agg = {
        'rounds': list(range(rounds)),
        'alive_mean': [], 'alive_std': [],
        'energy_mean': [], 'energy_std': [],
        'num_chs_mean': [], 'num_chs_std': [],
        'jain_mean': [], 'jain_std': [],
        'hops_mean': [], 'hops_std': []
    }

    for i in range(rounds):
        a_list = alive_by_round[i]
        e_list = energy_by_round[i]
        nc_list = [v for v in num_chs_by_round[i] if v is not None]
        j_list = [v for v in jain_by_round[i] if v is not None]
        h_list = [v for v in hops_by_round[i] if v is not None]

        agg['alive_mean'].append(statistics.mean(a_list))
        agg['alive_std'].append(statistics.pstdev(a_list))
        agg['energy_mean'].append(statistics.mean(e_list))
        agg['energy_std'].append(statistics.pstdev(e_list))
        
        if nc_list:
            agg['num_chs_mean'].append(statistics.mean(nc_list))
            agg['num_chs_std'].append(statistics.pstdev(nc_list))
        else:
            agg['num_chs_mean'].append(None)
            agg['num_chs_std'].append(None)
            
        if j_list:
            agg['jain_mean'].append(statistics.mean(j_list))
            agg['jain_std'].append(statistics.pstdev(j_list))
        else:
            agg['jain_mean'].append(None)
            agg['jain_std'].append(None)
            
        if h_list:
            agg['hops_mean'].append(statistics.mean(h_list))
            agg['hops_std'].append(statistics.pstdev(h_list))
        else:
            agg['hops_mean'].append(None)
            agg['hops_std'].append(None)

    # summary statistics for FND/HND/LND
    def summarize_list(lst):
        if not lst:
            return {'mean': None, 'std': None, 'count': 0}
        return {'mean': statistics.mean(lst), 'std': statistics.pstdev(lst), 'count': len(lst)}

    agg['FND'] = summarize_list(fnd_list)
    agg['HND'] = summarize_list(hnd_list)
    agg['LND'] = summarize_list(lnd_list)

    return agg


def save_csv(agg, out_csv):
    import csv
    with open(out_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['round', 
                         'alive_mean', 'alive_std', 
                         'energy_mean', 'energy_std', 
                         'num_chs_mean', 'num_chs_std',
                         'jain_mean', 'jain_std',
                         'hops_mean', 'hops_std'])
        for i, r in enumerate(agg['rounds']):
            writer.writerow([
                r,
                agg['alive_mean'][i], agg['alive_std'][i],
                agg['energy_mean'][i], agg['energy_std'][i],
                agg.get('num_chs_mean', [None])[i], agg.get('num_chs_std', [None])[i],
                agg.get('jain_mean', [None])[i], agg.get('jain_std', [None])[i],
                agg.get('hops_mean', [None])[i], agg.get('hops_std', [None])[i]
            ])


def plot_agg(agg, out_dir):
    rounds = agg['rounds']

    # Energy
    plt.figure()
    mean = agg['energy_mean']
    std = agg['energy_std']
    plt.plot(rounds, mean, label='mean')
    plt.fill_between(rounds, [m - s for m, s in zip(mean, std)], [m + s for m, s in zip(mean, std)], alpha=0.2)
    plt.xlabel('Round')
    plt.ylabel('Total Residual Energy (J)')
    plt.title('Average Total Energy vs Rounds')
    plt.grid(True)
    plt.tight_layout()
    outp = os.path.join(out_dir, 'avg_energy.png')
    plt.savefig(outp)
    plt.close() # Close to free memory

    # Alive
    plt.figure()
    mean = agg['alive_mean']
    std = agg['alive_std']
    plt.plot(rounds, mean, label='mean')
    plt.fill_between(rounds, [m - s for m, s in zip(mean, std)], [m + s for m, s in zip(mean, std)], alpha=0.2)
    plt.xlabel('Round')
    plt.ylabel('Alive Nodes')
    plt.title('Average Alive Nodes vs Rounds')
    plt.grid(True)
    plt.tight_layout()
    outp2 = os.path.join(out_dir, 'avg_alive.png')
    plt.savefig(outp2)
    plt.close()

    # Fairness
    if any(x is not None for x in agg.get('jain_mean', [])):
        plt.figure()
        mean = [m if m is not None else 0 for m in agg['jain_mean']]
        std = [s if s is not None else 0 for s in agg['jain_std']]
        plt.plot(rounds, mean, label='mean')
        plt.fill_between(rounds, [m - s for m, s in zip(mean, std)], [m + s for m, s in zip(mean, std)], alpha=0.2)
        plt.xlabel('Round')
        plt.ylabel("Jain's Fairness Index")
        plt.title('Fairness Index vs Rounds')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, 'avg_fairness.png'))
        plt.close()

    return outp, outp2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seeds', type=int, default=10)
    parser.add_argument('--rounds', type=int, default=200)
    parser.add_argument('--nodes', type=int, default=50)
    parser.add_argument('--field', type=int, default=100)
    parser.add_argument('--bs_x', type=int, default=50)
    parser.add_argument('--bs_y', type=int, default=50)
    parser.add_argument('--data-bits', type=int, default=None, help='Override DATA_BITS for experiments')
    parser.add_argument('--initial-energy', type=float, default=None, help='Override INITIAL_ENERGY for experiments')
    parser.add_argument('--out', type=str, default='results')
    parser.add_argument('--start-seed', type=int, default=0)
    parser.add_argument('--stop-on-fnd', action='store_true', help='Stop early when first node death occurs')
    # Heterogeneity args
    parser.add_argument('--hetero', action='store_true', help='Enable heterogeneity')
    parser.add_argument('--fraction', type=float, default=0.1, help='Fraction of advanced nodes (m)')
    parser.add_argument('--alpha', type=float, default=1.0, help='Energy multiplier for advanced nodes (alpha)')

    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)

    # Optionally override core params for experimentation without changing source
    import core.params as params
    if args.data_bits is not None:
        params.DATA_BITS = args.data_bits
        print('Overriding DATA_BITS ->', params.DATA_BITS)
    if args.initial_energy is not None:
        params.INITIAL_ENERGY = args.initial_energy
        print('Overriding INITIAL_ENERGY ->', params.INITIAL_ENERGY)
        
    # Heterogeneity overrides
    if args.hetero:
        params.HETEROGENEITY_ENABLED = True
        params.HETEROGENEITY_M = args.fraction
        params.HETEROGENEITY_ALPHA = args.alpha
        print(f'Heterogeneity ENABLED: m={args.fraction}, alpha={args.alpha} (Adv Node Energy = {params.INITIAL_ENERGY * (1+args.alpha)}J)')
    else:
        params.HETEROGENEITY_ENABLED = False

    all_metrics = []
    for i in range(args.seeds):
        seed = args.start_seed + i
        print('Running seed', seed)
        m = run_seed(seed, args.rounds, args.nodes, args.field, args.field, (args.bs_x, args.bs_y), args.out, stop_on_fnd=args.stop_on_fnd)
        all_metrics.append(m)

    agg = aggregate(all_metrics, args.rounds)

    # Create timestamped run directory and subfolders
    import datetime
    import shutil
    import csv

    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    run_dir = os.path.join(args.out, f'run_{ts}')
    plots_dir = os.path.join(run_dir, 'plots')
    tables_dir = os.path.join(run_dir, 'tables')
    raw_dir = os.path.join(run_dir, 'raw')
    os.makedirs(plots_dir, exist_ok=True)
    os.makedirs(tables_dir, exist_ok=True)
    os.makedirs(raw_dir, exist_ok=True)

    # Save aggregated metrics (JSON + CSV)
    with open(os.path.join(run_dir, 'agg_metrics.json'), 'w') as f:
        json.dump(agg, f, indent=2)
    save_csv(agg, os.path.join(run_dir, 'agg_metrics.csv'))

    # Generate plots into plots_dir and rename to requested filenames
    png1, png2 = plot_agg(agg, plots_dir)
    # Ensure requested filenames
    energy_png = os.path.join(plots_dir, 'energy_vs_rounds.png')
    alive_png = os.path.join(plots_dir, 'alive_nodes_vs_rounds.png')
    shutil.copy(png1, energy_png)
    shutil.copy(png2, alive_png)

    # Lifetime metrics (table) -> JSON + CSV
    lifetime = {'FND': agg['FND'], 'HND': agg['HND'], 'LND': agg['LND']}
    with open(os.path.join(tables_dir, 'lifetime_metrics.json'), 'w') as f:
        json.dump(lifetime, f, indent=2)
    with open(os.path.join(tables_dir, 'lifetime_metrics.csv'), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['metric', 'mean', 'std', 'count'])
        for k in ('FND', 'HND', 'LND'):
            v = lifetime[k]
            writer.writerow([k, v['mean'], v['std'], v['count']])

    # Simulation parameters snapshot
    import core.params as params
    sim_params = {
        'num_nodes': args.nodes,
        'field': f'{args.field}x{args.field}',
        'bs': [args.bs_x, args.bs_y],
        'INITIAL_ENERGY': params.INITIAL_ENERGY,
        'DATA_BITS': params.DATA_BITS,
        'AGGR_RATIO': params.AGGR_RATIO,
        'E_ELEC': params.E_ELEC,
        'EPS_FS': params.EPS_FS,
        'EPS_MP': params.EPS_MP,
        'CH_PROB': params.CH_PROB,
    }
    with open(os.path.join(tables_dir, 'simulation_parameters.json'), 'w') as f:
        json.dump(sim_params, f, indent=2)

    # Raw per-round metrics (aggregated mean/std)
    round_csv = os.path.join(raw_dir, 'round_metrics.csv')
    with open(round_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['round', 'alive_mean', 'alive_std', 'dead_mean', 'dead_std', 'total_energy_mean', 'total_energy_std', 'num_chs_mean', 'num_chs_std', 'jain_mean', 'jain_std', 'hops_mean', 'hops_std'])
        for i, r in enumerate(agg['rounds']):
            alive_mean = agg['alive_mean'][i]
            alive_std = agg['alive_std'][i]
            energy_mean = agg['energy_mean'][i]
            energy_std = agg['energy_std'][i]
            num_chs_mean = agg.get('num_chs_mean', [None])[i]
            num_chs_std = agg.get('num_chs_std', [None])[i]
            jain_mean = agg.get('jain_mean', [None])[i]
            jain_std = agg.get('jain_std', [None])[i]
            hops_mean = agg.get('hops_mean', [None])[i]
            hops_std = agg.get('hops_std', [None])[i]
            
            # Dead = nodes - alive (num_nodes args.nodes)
            dead_mean = (args.nodes - alive_mean) if alive_mean is not None else None
            # std for dead can be same as alive_std
            dead_std = alive_std
            writer.writerow([r, alive_mean, alive_std, dead_mean, dead_std, energy_mean, energy_std, num_chs_mean, num_chs_std, jain_mean, jain_std, hops_mean, hops_std])

    # Write a simple README for the run directory
    with open(os.path.join(run_dir, 'README.txt'), 'w') as f:
        f.write('This run was produced by scripts/run_experiments.py\n')
        f.write(f"Rounds: {args.rounds}, Seeds: {args.seeds}, Nodes: {args.nodes}\n")
        f.write('Contents:\n')
        f.write('  plots/energy_vs_rounds.png\n')
        f.write('  plots/alive_nodes_vs_rounds.png\n')
        f.write('  plots/avg_fairness.png (new)\n')
        f.write('  tables/lifetime_metrics.json/csv\n')
        f.write('  tables/simulation_parameters.json\n')
        f.write('  raw/round_metrics.csv\n')

    print('Wrote', run_dir)
    print('Wrote', energy_png)
    print('Wrote', alive_png)

    print('\nSummary FND/HND/LND (mean, std, count):')
    print('FND:', agg['FND'])
    print('HND:', agg['HND'])
    print('LND:', agg['LND'])


if __name__ == '__main__':
    main()
