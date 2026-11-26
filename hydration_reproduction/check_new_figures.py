"""Verify new scene manifests against archived coordinates, and decomposition against logs."""
import argparse, csv, json, re
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,default=Path(__file__).parent/'integration_evidence');p.add_argument('--figures',type=Path,default=Path(__file__).parent/'figures');a=p.parse_args();R=a.evidence;F=a.figures
read=lambda p:list(csv.DictReader(p.open(encoding='utf-8-sig')))
rows=read(R/'case_inventory.csv'); inv={r['configuration']:r for r in rows};n=0
for f in sorted((F/'scene_manifests').glob('*.json')):
 d=json.loads(f.read_text());job=d['job'];r=inv[job];x=(R/r['optimized_structure_path']).read_text().splitlines();atoms=[s.split() for s in x[2:2+int(x[0])]];e=[s[0].capitalize() for s in atoms];xyz=np.array([[float(v) for v in s[1:4]] for s in atoms]);assert d['atom_symbols']==e and np.array_equal(xyz,np.array(d['original_xyz_A']));shown=set(d['displayed_atom_indices']);w=d['water_atom_indices'];assert [e[i] for i in w]==['O','H','H'] and set(w)<=shown
 for k in ['displayed_bonds','water_contact_pairs','auxiliary_Zn_O_pairs','metal_water_proximity_pairs']:
  assert all(set(pair)<=shown for pair in d.get(k,[])),(job,k)
 b=np.array(d['camera_basis_columns']);assert np.allclose(b.T@b,np.eye(3),atol=1e-9);q=np.array(d['display_xyz_A']);assert np.allclose(q-q[0],(xyz-xyz[0])@b,atol=1e-8)
 if job.startswith('A_'):assert len(d['auxiliary_Zn_O_pairs'])==1
 if job=='MOF303_published_site':assert (5 in {i for pair in d['water_contact_pairs'] for i in pair}) and len(d['water_contact_pairs'])==4
 if job in ('B_Zn_approach','B_bound_O'):assert len(d['metal_water_proximity_pairs'])==1
 n+=1
assert n==9;print('PASS:',n,'scene manifests match archived atom identities, coordinates, displayed contact endpoints and rigid camera transforms')
conv=2625.49963948
def energy(job):
 r=inv[job];s=(R/r['output_log_path']).read_text(errors='replace');return float(re.findall(r'TOTAL ENERGY\s+(-?\d+\.\d+)\s+Eh',s)[-1])
rr={r['system']:r for r in read(R/'03_hydration_response/numerical_results/final/results.csv')}
for s in ('A','B'):
 r=rr[s+'_carboxyl'];ew=energy(s+'_carboxyl');ef=energy(s+'_framework_at_hydrated_geometry');eg=energy(s+'_water_at_hydrated_geometry');ed=energy(r['dry_reference']);e0=energy('water');vals=[(ew-ef-eg)*conv,(ef-ed)*conv,(eg-e0)*conv];expected=[float(r[k]) for k in ['interaction_kJ_mol','framework_deformation_kJ_mol','water_deformation_kJ_mol']];assert np.allclose(vals,expected,atol=1e-6,rtol=0);print(s,'decomposition kJ/mol:',vals)
print('PASS: decomposition values agree with fragment single-point logs')
