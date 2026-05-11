"""Manage and prune old result files safely.

Usage examples:
  # Dry-run, show what would be removed (keep 3 most-recent graphs)
  python scripts/manage_results.py --path master_results_final --what graphs --keep 3 --dry-run

  # Actually remove (move to .trash) without prompting
  python scripts/manage_results.py --path master_results_final --what graphs --keep 3 --yes

  # Interactive prompt before deleting
  python scripts/manage_results.py --path master_results_final --what runs --keep 5

This script moves deleted items to a timestamped .trash_<ts> folder under the target path.
"""
from __future__ import annotations
import argparse
import os
import shutil
import time
from pathlib import Path
from typing import List

GRAPH_EXTS = {'.png', '.jpg', '.jpeg', '.pdf', '.svg'}


def list_graphs(path: Path) -> List[Path]:
    return [p for p in path.rglob('*') if p.suffix.lower() in GRAPH_EXTS and p.is_file()]


def list_runs(path: Path) -> List[Path]:
    # consider directories that look like runs: folders starting with 'run_' or timestamp-like names or algorithm folders
    dirs = [p for p in path.iterdir() if p.is_dir()]
    candidates = []
    for d in dirs:
        name = d.name.lower()
        if name.startswith('run_') or name.startswith('run') or name.startswith('master_results') or name in ('comparison', 'ebpt', 'load_balanced', 'traffic_aware', 'qos'):
            candidates.append(d)
        else:
            # include any directory that contains images or seed_*.json as a run folder
            if any(d.rglob('seed_*.json')) or any(d.rglob('*.png')):
                candidates.append(d)
    return candidates


def keep_latest(items: List[Path], keep: int) -> (List[Path], List[Path]):
    # Sort by modification time descending
    items_sorted = sorted(items, key=lambda p: p.stat().st_mtime, reverse=True)
    keep_items = items_sorted[:keep]
    remove_items = items_sorted[keep:]
    return keep_items, remove_items


def move_to_trash(items: List[Path], target_path: Path, dry_run: bool = True) -> None:
    if not items:
        print('Nothing to remove.')
        return
    ts = time.strftime('%Y%m%d_%H%M%S')
    trash_dir = target_path / f'.trash_{ts}'
    if dry_run:
        print(f'[DRY-RUN] Would move {len(items)} items to {trash_dir}')
        for p in items:
            print('  DRY:', p)
        return

    trash_dir.mkdir(parents=True, exist_ok=True)
    for p in items:
        dest = trash_dir / p.name
        try:
            shutil.move(str(p), str(dest))
            print('Moved:', p, '->', dest)
        except Exception as e:
            print('Failed to move', p, ':', e)


def confirm(prompt: str) -> bool:
    try:
        ans = input(prompt + ' [y/N]: ').strip().lower()
        return ans in ('y', 'yes')
    except KeyboardInterrupt:
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', '-p', type=str, default='master_results', help='Target results path')
    parser.add_argument('--what', choices=['graphs', 'runs', 'all'], default='graphs', help='What to prune')
    parser.add_argument('--keep', type=int, default=3, help='Number of recent items to keep')
    parser.add_argument('--dry-run', action='store_true', help='Do not perform deletion; show what would be done')
    parser.add_argument('--yes', action='store_true', help='Skip confirmation (be careful)')
    args = parser.parse_args()

    target = Path(args.path)
    if not target.exists():
        print('Target path does not exist:', target)
        return

    if args.what in ('graphs', 'all'):
        graphs = list_graphs(target)
        keep_g, remove_g = keep_latest(graphs, args.keep)
        print(f'Found {len(graphs)} graph files under {target}. Keeping {len(keep_g)} newest, removing {len(remove_g)}.')
    else:
        remove_g = []

    if args.what in ('runs', 'all'):
        runs = list_runs(target)
        keep_r, remove_r = keep_latest(runs, args.keep)
        print(f'Found {len(runs)} run directories under {target}. Keeping {len(keep_r)} newest, removing {len(remove_r)}.')
    else:
        remove_r = []

    to_remove = remove_g + remove_r

    if not to_remove:
        print('Nothing to remove.')
        return

    if args.dry_run:
        move_to_trash(to_remove, target, dry_run=True)
        return

    if not args.yes:
        print('\nItems to remove:')
        for p in to_remove:
            print(' ', p)
        if not confirm('Proceed and move these items to a local .trash folder?'):
            print('Aborted by user.')
            return

    move_to_trash(to_remove, target, dry_run=False)


if __name__ == '__main__':
    main()
