#!/usr/bin/env python3
"""Reformat three saved-summary tables, without fitting or estimating new results.

Table layout and ordering adapted from the pinned upstream generator:
https://github.com/alimardani76/mof_stablity_transfer/blob/65725ae2b8b7f25d15ba08e68632198cc0ddc954/figure_sources/originals/phase_10_numbers.py
Only the three derivations fully supported by the supplied local CSVs are used.
subblocks.tex and numbers.tex remain immutable saved results.
"""
from pathlib import Path
import argparse
import csv

ROOT = Path(__file__).resolve().parents[1]
CELLS = [('ASR', 'element', 13), ('FSR', 'element', 11),
         ('ASR', 'allnodes', 5), ('FSR', 'allnodes', 5)]


def read(name):
    with (ROOT / 'data/aggregate' / name).open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def one(rows, **keys):
    selected = [r for r in rows if all(r[k] == str(v) for k, v in keys.items())]
    if len(selected) != 1:
        raise ValueError(f'Expected exactly one saved result: {keys}; found {len(selected)}')
    return selected[0]


def table(headers, rows, align):
    lines = [r'\begin{tabular}{' + align + '}', r'\toprule',
             ' & '.join(headers) + r' \\', r'\midrule']
    lines += [' & '.join(map(str, row)) + r' \\' for row in rows]
    return '\n'.join(lines + [r'\bottomrule', r'\end{tabular}']) + '\n'


def num(key):
    return r'\Num{' + key + '}'


def build():
    """Return standalone LaTeX tables; verify CSV values against the saved macros."""
    import re
    macros = dict(re.findall(r'\\csname num([^\\]+)\\endcsname\{([^}]+)\}',
                            (ROOT / 'generated/numbers.tex').read_text(encoding='utf-8')))

    def checked(key, value):
        if f'{float(value):.3f}' != macros[key]:
            raise ValueError(f'Saved macro and CSV disagree: {key}: {value} vs {macros[key]}')
        return num(key)

    water = read('figure_02_ladder.csv')
    rows = []
    for form, hold, n in CELLS:
        vals = []
        for short, model in zip(['B', 'BC', 'BCL', 'P'],
                               ['Pore and density B', 'B + chemistry C',
                                'B + C + coordination L', 'B + C + L + donor attachment I (P)']):
            r = one(water, form=form, holdout=hold, model=model)
            assert int(r['family_count']) == n
            vals.append(checked('water' + form + hold + short, r['mean_equal_family_spearman']))
        rows.append([form, 'element' if hold == 'element' else 'AllNodes', n, *vals])
    outputs = {'water_ladder.tex': table(
        ['Form', 'Holdout', '$n_f$', 'B', 'B+C', 'B+C+L', 'P'], rows, 'llrrrrr')}

    structural = read('figure_04_structural.csv')
    rows = []
    for branch in ['G9', 'N', 'V', 'H', 'J', 'SOAPkernel']:
        row = [{'J': 'J (conditional)', 'SOAPkernel': 'SOAP kernel'}.get(branch, branch)]
        for form, hold, n in CELLS:
            r = one(structural, branch=branch, form=form, holdout=hold)
            assert int(r['family_count']) == n
            key = branch.replace('_', '') + form + hold + 'mean_delta'
            row.append(checked(key, r['mean_delta_rho']) + f" ({int(r['positive_families'])}/{n})")
        rows.append(row)
    outputs['structural.tex'] = table(
        ['Branch', 'ASR element', 'FSR element', 'ASR AllNodes', 'FSR AllNodes'], rows, 'lrrrr')

    endpoints = read('figure_05_endpoints.csv')
    rows = []
    for endpoint in ['activation', 'thermal']:
        for form, hold, n in CELLS:
            row = [endpoint, form, 'element' if hold == 'element' else 'AllNodes', n]
            for i, model in enumerate(['B', 'B+C', 'B+C+L', 'P']):
                r = one(endpoints, endpoint=endpoint, form=form, holdout=hold, model=model)
                assert int(r['family_count']) == n
                row.append(checked(endpoint + form + hold + f'rho{i}', r['mean_spearman']))
            rows.append(row)
    outputs['endpoint_ladders.tex'] = table(
        ['Endpoint', 'Form', 'Holdout', '$n_f$', 'B', 'B+C', 'B+C+L', 'P'], rows, 'lllrrrrr')
    return outputs


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check', action='store_true', help='compare deterministic tables without writing')
    args = p.parse_args()
    for name, content in build().items():
        path = ROOT / 'generated' / name
        if args.check:
            if path.read_text(encoding='utf-8') != content:
                raise ValueError(f'Table differs from saved-data regeneration: {name}')
        else:
            path.write_text(content, encoding='utf-8', newline='\n')
        print(('Checked ' if args.check else 'Regenerated ') + name)


if __name__ == '__main__':
    main()
