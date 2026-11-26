"""Optional replay of saved xTB inputs. Dry-run by default, never changes the archive.
Requires a separately installed xTB executable and parameter directory. Not tested here.
"""
from pathlib import Path
import argparse, csv, json, os, re, shutil, subprocess
p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,default=Path(__file__).parent/'integration_evidence');p.add_argument('--job',action='append',default=[]);p.add_argument('--all-accepted',action='store_true');p.add_argument('--xtb',default='xtb');p.add_argument('--xtbpath');p.add_argument('--out',type=Path,default=Path('xtb_replay'));p.add_argument('--execute',action='store_true');a=p.parse_args()
R=a.evidence.resolve();O=a.out.resolve();rows=list(csv.DictReader((R/'case_inventory.csv').open(encoding='utf-8-sig')));rows=[r for r in rows if r['calculation_status'] in ('accepted','converged')];jobs=[r for r in rows if a.all_accepted or r['configuration'] in a.job]
if not jobs:raise SystemExit('Select --job CONFIGURATION or --all-accepted; omit --execute to list commands.')
if O==R or R in O.parents:raise SystemExit('Output must be outside the evidence directory.')
env=os.environ.copy();env.update(OMP_NUM_THREADS='2',MKL_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2');
if a.xtbpath:env['XTBPATH']=str(Path(a.xtbpath).resolve())
exe=shutil.which(a.xtb) if a.execute else a.xtb
if a.execute and not exe:raise SystemExit('xTB executable not found')
for r in jobs:
 src=(R/r['input_structure_path']).parent;cmd=json.loads((src/'command.json').read_text(encoding='utf-8-sig'));cmd=cmd['command'] if isinstance(cmd,dict) else cmd;cmd=[exe]+cmd[1:];dest=O/r['case']/r['configuration'];print(r['configuration'],cmd)
 if not a.execute:continue
 dest.mkdir(parents=True,exist_ok=False)
 for file in ('input.xyz','xcontrol.inp'):
  if (src/file).exists():shutil.copy2(src/file,dest/file)
 try:
  with (dest/'replay.log').open('w') as f:res=subprocess.run(cmd,cwd=dest,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=900)
  t=(dest/'replay.log').read_text(errors='replace');v=re.findall(r'TOTAL ENERGY\s+(-?\d+\.\d+)\s+Eh',t);actual=float(v[-1]) if v else None
  (dest/'replay_summary.json').write_text(json.dumps({'returncode':res.returncode,'energy_Eh':actual,'archived_energy_Eh':r['final_energy_Eh'],'difference_Eh':actual-float(r['final_energy_Eh']) if actual is not None else None,'optimization_convergence_marker':'GEOMETRY OPTIMIZATION CONVERGED' in t},indent=2))
 except subprocess.TimeoutExpired:(dest/'replay_summary.json').write_text(json.dumps({'status':'timeout'}))
