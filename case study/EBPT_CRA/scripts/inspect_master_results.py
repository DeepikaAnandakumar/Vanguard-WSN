import json
import glob
import os

folder = os.path.join(os.path.dirname(__file__), '..', 'master_results_final')
pattern = os.path.join(folder, 'metrics_seed_*.json')
files = sorted(glob.glob(pattern))

for p in files:
    try:
        with open(p, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f'ERROR reading {p}: {e}')
        continue
    seed = data.get('seed')
    print(f'--- {os.path.basename(p)} (seed={seed}) ---')
    # report common summary keys if present
    for k in ('first_node_death','half_node_death','last_node_death'):
        if k in data:
            print(f'{k}: {data[k]}')
    # list top-level arrays and simple stats
    for k,v in data.items():
        if isinstance(v, list):
            ln = len(v)
            sample_first = v[0] if ln>0 else None
            sample_last = v[-1] if ln>0 else None
            # if numeric list, compute basic stats for short lists
            print(f'array `{k}`: len={ln}, first={sample_first}, last={sample_last}')
    print()

print('Done.')
