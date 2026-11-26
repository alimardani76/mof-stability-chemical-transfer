#!/usr/bin/env python3
"""Reassemble and verify the complete source-evidence ZIP, then extract it."""
import argparse, hashlib, io, zipfile
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--out', type=Path, required=True)
a=p.parse_args()
root=Path(__file__).resolve().parent
parts=sorted((root/'archive_parts').glob('source_evidence.part*'))
assert [p.name for p in parts]==[f'source_evidence.part{i:02}' for i in range(12)], 'Missing archive part'
raw=b''.join(p.read_bytes() for p in parts)
assert hashlib.sha256(raw).hexdigest()=='477b52cfb0815b5683ef053bc2983f6692a79a22f5a72e5981b65f1f0a01327c', 'Archive checksum mismatch'
with zipfile.ZipFile(io.BytesIO(raw)) as z:
    assert z.testzip() is None, 'Corrupt archive'
    rootname='hydration_reproduction/'
    for line in z.read(rootname+'SHA256SUMS.txt').decode().splitlines():
        digest,name=line.split('  ',1)
        assert hashlib.sha256(z.read(rootname+name)).hexdigest()==digest,name
    assert all(n.startswith(rootname) and '..' not in Path(n).parts for n in z.namelist()), 'Unexpected archive path'
    a.out.mkdir(parents=True,exist_ok=False)
    z.extractall(a.out)
print('PASS: verified and extracted',a.out/'hydration_reproduction')
