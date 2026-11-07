#!/usr/bin/env python3
"""Offline reproduction, optionally denying access to sibling project folders."""
from pathlib import Path
import argparse
import os
import runpy
import sys

ROOT = Path(__file__).resolve().parents[1]


def isolate():
    """Enforce a read barrier around sibling projects, including any source checkout."""
    parent = ROOT.parent

    def audit(event, args):
        if event in {'socket.connect', 'socket.getaddrinfo'}:
            raise PermissionError('Network access disabled during saved-data reproduction')
        if event in {'open', 'os.listdir', 'os.scandir', 'os.chdir'} and args:
            raw = args[0]
            if isinstance(raw, (str, bytes, os.PathLike)):
                path = Path(os.fsdecode(raw)).absolute()
                # resolve() would recurse through audit events on some platforms.
                path = Path(os.path.normpath(path))
                if path.is_relative_to(parent) and not path.is_relative_to(ROOT):
                    raise PermissionError('Access outside the clean repository denied')

    sys.addaudithook(audit)
    try:
        (parent / 'isolation-negative-control').read_bytes()
    except PermissionError:
        print('PASS: sibling-file access is denied; network access is disabled')
    else:
        raise RuntimeError('Isolation barrier failed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--isolated', action='store_true')
    args = parser.parse_args()
    os.chdir(ROOT)
    sys.path.insert(0, str(ROOT / 'scripts'))
    if args.isolated:
        isolate()
    from manifest import verify
    verify(ROOT / 'data/aggregate/INPUT_SHA256.csv', exact=False)
    for script in ['figure_sources/make_figures.py', 'scripts/make_tables.py', 'scripts/check_figures.py']:
        sys.argv = [script]
        runpy.run_path(str(ROOT / script), run_name='__main__')
    print('PASS: offline saved-results reproduction completed')


if __name__ == '__main__':
    main()
