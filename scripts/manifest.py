#!/usr/bin/env python3
"""Write or verify the exact distributable file set and its SHA256 hashes."""
from pathlib import Path
import argparse
import csv
import hashlib

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'SHA256_MANIFEST.csv'
OMIT_PARTS = {'.git', '__pycache__', '.venv', 'venv', '.pytest_cache'}


def files():
    return sorted(p for p in ROOT.rglob('*') if p.is_file()
                  and not OMIT_PARTS.intersection(p.relative_to(ROOT).parts)
                  and p != MANIFEST and p.suffix not in {'.pyc', '.pyo'})


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def verify(path=MANIFEST, exact=True):
    with path.open(encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f))
    seen = set()
    for r in rows:
        rel = r['path']
        p = (ROOT / rel).resolve()
        if not p.is_relative_to(ROOT) or rel in seen:
            raise ValueError(f'Invalid or repeated manifest path: {rel}')
        seen.add(rel)
        if digest(p) != r['sha256'] or p.stat().st_size != int(r['size_bytes']):
            raise ValueError(f'Hash/size mismatch: {rel}')
    if exact and seen != {p.relative_to(ROOT).as_posix() for p in files()}:
        raise ValueError('Manifest does not cover the exact distributable file set')
    print(f'PASS: {len(rows)} SHA256/size records in {path.relative_to(ROOT)}')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--write', action='store_true')
    args = p.parse_args()
    if args.write:
        with MANIFEST.open('w', encoding='utf-8', newline='') as f:
            w = csv.writer(f, lineterminator='\n')
            w.writerow(['path', 'sha256', 'size_bytes'])
            for item in files():
                w.writerow([item.relative_to(ROOT).as_posix(), digest(item), item.stat().st_size])
    verify()


if __name__ == '__main__':
    main()
