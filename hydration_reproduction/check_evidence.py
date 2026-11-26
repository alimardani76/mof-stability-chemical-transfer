"""Read-only verification of archived energies, fixed masks and reported distances."""
import argparse,csv,re,json
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('evidence',type=Path);p.add_argument('--out',type=Path,default=Path(__file__).parent);a=p.parse_args();R=a.evidence;O=a.out;O.mkdir(parents=True,exist_ok=True)
read=lambda f:list(csv.DictReader(f.open(encoding='utf-8-sig')))
def xyz(p):
 s=p.read_text().splitlines();r=[l.split() for l in s[2:2+int(s[0])]];return [l[0].capitalize() for l in r],np.array([[float(x) for x in l[1:4]] for l in r])
def fix(p):
 if not p.exists():return []
 m=re.search(r'\$fix\s+atoms:\s*([^\n]+)',p.read_text());out=[]
 if m:
  for x in m[1].split(','):
   q=x.strip().split('-');out.extend(range(int(q[0])-1,int(q[-1])))
 return out
rows=read(R/'case_inventory.csv');out=[];energies={}
for r in rows:
 if r['calculation_status'] not in ('accepted','converged','accepted single point'):continue
 l=R/r['output_log_path'];s=l.read_text(errors='replace');v=re.findall(r'TOTAL ENERGY\s+(-?\d+\.\d+)\s+Eh',s);e=float(v[-1]) if v else None;expected=float(r['final_energy_Eh']) if r['final_energy_Eh'] else None
 entry={'case':r['case'],'configuration':r['configuration'],'status':r['calculation_status'],'log_energy_Eh':e,'inventory_energy_Eh':expected,'difference_Eh':abs(e-expected) if e is not None and expected is not None else None,'fixed_count':None,'fixed_max_component_A':None,'atom_order_matches':None,'optimization_convergence_marker':'GEOMETRY OPTIMIZATION CONVERGED' in s}
 i=R/r['input_structure_path'];j=R/r['optimized_structure_path']
 if i.is_file() and j.is_file() and j.suffix=='.xyz':
  ei,pi=xyz(i);ej,pj=xyz(j);inds=fix(i.parent/'xcontrol.inp');entry['atom_order_matches']=ei==ej;entry['fixed_count']=len(inds);entry['fixed_max_component_A']=float(np.max(np.abs(pj[inds]-pi[inds]))) if inds else 0.0
 energies[r['configuration']]=e;out.append(entry)
with (O/'archive_checks.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
print('status counts', {s:sum(r['calculation_status']==s for r in rows) for s in set(r['calculation_status'] for r in rows)})
print('checked',len(out),'max energy difference',max(x['difference_Eh'] or 0 for x in out),'max fixed component',max(x['fixed_max_component_A'] or 0 for x in out),'order failures',sum(x['atom_order_matches'] is False for x in out))
# Reconstruct association energies from total energies and shared water reference; check the final references.
water=energies['water'];conv=2625.4996394799;ar=[]
for case,folder,rel in [('A','01_metal_identity','numerical_results/results.csv'),('B','02_spatial_cooperation','numerical_results/results.csv'),('C','03_hydration_response','numerical_results/final/results.csv')]:
 for r in read(R/folder/rel):
  if not r.get('association_kJ_mol'):continue
  job=r['system'] if case=='C' else r['system']+'_'+r['configuration'];dry=r['dry_reference'] if case=='C' else r['used_dry_reference'];calc=(energies[job]-energies[dry]-water)*conv;reported=float(r['association_kJ_mol']);ar.append(dict(case=case,configuration=job,reference=dry,reported_kJ_mol=reported,recomputed_kJ_mol=calc,absolute_difference_kJ_mol=abs(calc-reported)))
with (O/'association_checks.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(ar[0]));w.writeheader();w.writerows(ar)
print('association rows',len(ar),'max diff',max(r['absolute_difference_kJ_mol'] for r in ar))
# Recover plotted interatomic distances directly from XYZ and atom-index maps.
checks=[]
for folder,kind,systems in [('01_metal_identity','metal',['Mg_open_metal','Zn_linker_O']),('02_spatial_cooperation','pocket',['MOF303_published_site','LA2_1_published_site'])]:
 d=R/folder;table=read(d/'numerical_results/results.csv')
 for job in systems:
  sys,conf=job.rsplit('_',2)[0],job.rsplit('_',2)[-2]+'_'+job.rsplit('_',2)[-1]
  r=next(z for z in table if z['system']+'_'+z['configuration']==job)
  e,x=xyz(d/'optimized_structures/accepted'/job/'xtbopt.xyz');m=json.loads((d/'cluster_inputs/prepared_models'/f'{job}.json').read_text(encoding='utf-8-sig'))
  pairs=[(0,'central_M_water_A')] if kind=='metal' else list(zip(m['pocket_indices'],['pyrazole_N1_Owater_A','pyrazole_N2_Owater_A','mu_OH_O_Owater_A']))
  for i,k in pairs:
   actual=float(np.linalg.norm(x[-3]-x[i]));reported=float(r[k]);checks.append(dict(job=job,observable=k,atom_index_zero_based=i,water_O_index_zero_based=len(e)-3,coordinate_distance_A=actual,reported_distance_A=reported,absolute_difference_A=abs(actual-reported)))
d=R/'03_hydration_response';table=read(d/'numerical_results/final/results.csv');m=json.loads((d/'cluster_inputs/original_prepared_models/jobs.json').read_text())
for r in table:
 job=r['system'];e,x=xyz(d/'optimized_structures/accepted/optimization'/job/'xtbopt.xyz');i=m[job]['zn_index'];actual=float(np.linalg.norm(x[-3]-x[i]));reported=float(r['water_Zn_A']);checks.append(dict(job=job,observable='water_Zn_A',atom_index_zero_based=i,water_O_index_zero_based=len(e)-3,coordinate_distance_A=actual,reported_distance_A=reported,absolute_difference_A=abs(actual-reported)))
with (O/'coordinate_checks.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(checks[0]));w.writeheader();w.writerows(checks)
print('distance checks',len(checks),'max difference',max(x['absolute_difference_A'] for x in checks))
assert len(out)==33 and all(x['difference_Eh'] is not None and x['difference_Eh']<1e-9 for x in out), 'Energy archive mismatch'
assert sum(x['atom_order_matches'] is not None for x in out)==29
assert all(x['atom_order_matches'] is not False and (x['fixed_max_component_A'] or 0)<=1e-4 for x in out)
assert len(ar)==12 and max(x['absolute_difference_kJ_mol'] for x in ar)<1e-6
assert len(checks)==14 and max(x['absolute_difference_A'] for x in checks)<1e-8
print('PASS: all archive-level assertions')
