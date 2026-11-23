#!/usr/bin/env python3
"""Check that all seven manuscript rasters match the archived release."""
import csv
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'publication' / 'figure_index.csv'
EXPECTED = {f'figure_{number:02}.png' for number in range(1, 7)} | {'toc_graphic.png'}


def check():
    with INDEX.open(encoding='utf-8', newline='') as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != len(EXPECTED) or {row['file'] for row in rows} != EXPECTED:
        raise ValueError('Figure index must list the six article figures and the graphical abstract once each.')
    for row in rows:
        path = INDEX.parent / 'figures' / row['file']
        if sha256(path.read_bytes()).hexdigest() != row['sha256']:
            raise ValueError(f'Published artwork checksum differs: {path.relative_to(ROOT)}')
        for source in row['numerical_sources'].split('|'):
            if source and not (ROOT / source).is_file():
                raise FileNotFoundError(source)
    print(f'PASS: {len(rows)} exact manuscript raster assets and their source references')


if __name__ == '__main__':
    check()
