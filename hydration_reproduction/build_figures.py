"""Rebuild coordinate-derived P1 hydration figure from integration_evidence. No xTB runs."""
import argparse,csv,json, re, math, os
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib import font_manager
import vtk
from vtk.util.numpy_support import vtk_to_numpy
import networkx as nx
P=argparse.ArgumentParser();P.add_argument('evidence',type=Path);P.add_argument('--out',type=Path,default=Path(__file__).parent);args=P.parse_args();R=args.evidence;O=args.out;O.mkdir(parents=True,exist_ok=True)
A=R/'01_metal_identity';B=R/'02_spatial_cooperation';C=R/'03_hydration_response'
def readcsv(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def xyz(p):
 s=p.read_text().splitlines();a=[l.split() for l in s[2:2+int(s[0])]];return [l[0].capitalize() for l in a],np.array([[float(x) for x in l[1:4]] for l in a])
def unit(x):return x/np.linalg.norm(x)
def molbonds(p):
 s=p.read_text().splitlines();n=int(s[3][:3]);m=int(s[3][3:6]);return [(int(l[:3])-1,int(l[3:6])-1) for l in s[4+n:4+n+m]]
def files(case,job):
 if case==C:
  d=case/'optimized_structures/accepted/optimization'/job; m=json.loads((case/'cluster_inputs/original_prepared_models/jobs.json').read_text())[job];m['contacts']=[[m['zn_index'],j] for j in m['donors']]
 else:
  d=case/'optimized_structures/accepted'/job;m=json.loads((case/'cluster_inputs/prepared_models'/f'{job}.json').read_text(encoding='utf-8-sig'))
 e,p=xyz(d/'xtbopt.xyz');return e,p,m,molbonds(d/'xtbtopo.mol')
ra=readcsv(A/'numerical_results/results.csv');rb=readcsv(B/'numerical_results/results.csv');rc=readcsv(C/'numerical_results/final/results.csv');rcc={r['system']:r for r in rc}
colors={'C':'#68737c','O':'#d7473e','N':'#2d65b4','H':'#f0f2f4','Mg':'#208e69','Zn':'#7960b0','Al':'#7292a3'}
rad={'C':.235,'O':.30,'N':.30,'H':.17,'Mg':.46,'Zn':.46,'Al':.38}
metals={'Mg','Zn','Al'}; teal='#176e73'; ochre='#a4612e'; ink='#20313b'; muted='#65757d'; grid='#dfe5e7'; purple=colors['Zn']
def rgb(h):return np.array([int(h[i:i+2],16)/255 for i in (1,3,5)])
def shade(h,f):return rgb(h)*f+np.array([.92,.93,.94])*(1-f)
def add_sphere(renderer,pt,r,col):
 s=vtk.vtkSphereSource();s.SetCenter(*pt);s.SetRadius(r);s.SetThetaResolution(28);s.SetPhiResolution(24);m=vtk.vtkPolyDataMapper();m.SetInputConnection(s.GetOutputPort());a=vtk.vtkActor();a.SetMapper(m);pr=a.GetProperty();pr.SetColor(*col);pr.SetAmbient(.29);pr.SetDiffuse(.74);pr.SetSpecular(.24);pr.SetSpecularPower(28);renderer.AddActor(a)
def tube(renderer,a,b,r,col):
 l=vtk.vtkLineSource();l.SetPoint1(*a);l.SetPoint2(*b);t=vtk.vtkTubeFilter();t.SetInputConnection(l.GetOutputPort());t.SetRadius(r);t.SetNumberOfSides(14);t.CappingOn();m=vtk.vtkPolyDataMapper();m.SetInputConnection(t.GetOutputPort());act=vtk.vtkActor();act.SetMapper(m);pr=act.GetProperty();pr.SetColor(*col);pr.SetAmbient(.33);pr.SetDiffuse(.70);pr.SetSpecular(.12);renderer.AddActor(act)
def dashed(renderer,a,b,color="#238b8b",step=.24):
 d=b-a;length=np.linalg.norm(d); u=d/length;start=.28;end=length-.26
 for s in np.arange(start,end,step):tube(renderer,a+s*u,a+min(s+step*.55,end)*u,.044,rgb(color))
def render(case,job,kind,ax=None,full=False):
 e,p,m,mb=files(case,job);aux=[];prox=[];w=len(e)-3; water={w,w+1,w+2};contacts={tuple(sorted(t)) for t in m['contacts']}; cov={tuple(sorted((i,j))) for i,j in mb if e[i] not in metals and e[j] not in metals};bonds=cov|contacts
 assert e[w:]==['O','H','H'], (job,e[w:])
 bonds|={(w,w+1),(w,w+2)}
 g=nx.Graph();g.add_nodes_from(range(len(e)));g.add_edges_from(cov)
 if kind=='metal':
  center=p[0]; y=unit(p[w]-center); xx=p[1]-p[2];x=unit(xx-y*(xx@y));core={0,w,w+1,w+2}|{j for i,j in m['contacts'] if i==0}; context={i for i,a in enumerate(e) if a!='H' and np.linalg.norm(p[i]-center)<5.1};context|={0,1,2}|{j for i,j in m['contacts']};hbs=[(0,w)]; labels=[];scale=0
  if job=='Mg_open_metal':
   for h in [w+1,w+2]:
    for j,a in enumerate(e[:w]):
     if a!='O':continue
     da=np.linalg.norm(p[j]-p[w]);ha=np.linalg.norm(p[j]-p[h]);angle=np.degrees(np.arccos(np.clip(unit(p[w]-p[h])@unit(p[j]-p[h]),-1,1)))
     if da<3.1 and ha<2.4 and angle>150: hbs.append((h,j));core.add(j)
 elif kind=='pocket':
  n1,n2,oh=m['pocket_indices'];center=(p[w]+p[oh]+p[n1]+p[n2])/4; x=unit(p[n2]-p[n1]); yy=(p[n1]+p[n2])/2-p[oh];y=unit(yy-x*(yy@x));core={n1,n2,oh,*water}|{i for i,j in m['contacts'] if j==oh};context={i for i,a in enumerate(e) if a!='H' and np.linalg.norm(p[i]-p[w])<4.65}|core;hbs=[(n1,w),(n2,w),(oh,w),(5,w)];core.add(5);labels=[(n1,'N1'),(n2,'N2'),(oh,'OH1'),(5,'OH2')];scale=0
 else:
  z=m['zn_index'];center=(p[z]+p[w])*.5;x=unit(p[w]-p[z]);ds=m['donors'];yy=p[ds[0]]-p[ds[1]];y=unit(yy-x*(yy@x));core={z,*ds,*water};context={i for i,a in enumerate(e) if a!='H' and np.linalg.norm(p[i]-p[z])<4.5}|core; rr=rcc[job];hbs=[]
  for hb in json.loads(rr['hydrogen_bonds']):
   a,b=hb['H_idx'],hb['acceptor_idx'];hbs.append((a,b));core|={a,b,hb['donor_idx']}
  if float(rr['water_Zn_A'])<3: prox=[(z,w)]
  labels=[];scale=0
  if job.startswith('A_'):
   j=m['cluster_labels'].index('O2@(0, 0, 0)');aux=[(z,j)];core.add(j)
 # Include complete small rings touching selected active environment, not partial ring fragments.
 heavy=g.subgraph([i for i,a in enumerate(e) if a!='H'])
 for ring in nx.cycle_basis(heavy):
  if len(ring)<=7 and (len(set(ring)&context)>=3 or set(ring)&core):context.update(ring)
 # Show all polar hydrogens on active/pocket atoms, omit distal C–H for clarity.
 for i,j in cov:
  if e[i]=='H' and e[j] in ('N','O') and j in core:core.add(i)
  if e[j]=='H' and e[i] in ('N','O') and i in core:core.add(j)
 shown=context|core|water
 # Do not draw distant cap-only atoms. Explicitly retain water and contact endpoints.
 zaxis=unit(np.cross(x,y));q=(p-center)@np.stack([x,y,zaxis],axis=1)
 # Set camera extent to cover the displayed atoms, preserving a common lower bound by case.
 # Recenter display, not the underlying coordinates, and reserve edge space for labels.
 lo=q[list(shown)].min(axis=0);hi=q[list(shown)].max(axis=0);q=q-(lo+hi)/2
 sx=np.max(np.abs(q[list(shown),0]))+.70;sy=np.max(np.abs(q[list(shown),1]))+.70
 aspect=1.14;scale=max(5.45 if kind=='response' else 4.95,sx/aspect,sy)
 # Exact scene manifest for independent checking of the cropped visualizations.
 scene_dir=O/'scene_manifests';scene_dir.mkdir(exist_ok=True)
 scene={'job':job,'kind':kind,'atom_index_convention':'zero-based XYZ order','water_atom_indices':sorted(water),'displayed_atom_indices':sorted(shown),'highlighted_atom_indices':sorted(core),'displayed_bonds':[list(t) for t in sorted(bonds) if set(t)<=shown and (t in contacts or np.linalg.norm(p[t[0]]-p[t[1]])<=1.95)],'water_contact_pairs':[list(t) for t in hbs], 'auxiliary_Zn_O_pairs':aux, 'metal_water_proximity_pairs':prox,'contact_style':'solid coordination' if kind=='metal' else 'teal dashed selected H-bond/contact; orange dotted Zn proximity; purple dashed auxiliary Zn-O','labels':[[int(i),t] for i,t in labels]+[[w,'H2O']],'original_xyz_A':p.tolist(),'display_xyz_A':q.tolist(),'camera_parallel_scale_A':float(scale),'camera_basis_columns':np.stack([x,y,zaxis],axis=1).tolist(),'atom_symbols':e}
 (scene_dir/f'{job}.json').write_text(json.dumps(scene,indent=2))
 ren=vtk.vtkRenderer();ren.SetBackground(1,1,1);ren.SetUseDepthPeeling(False);ren.SetUseSSAO(True);ren.SetSSAORadius(.65);ren.SetSSAOBias(.03);ren.SetSSAOKernelSize(64)
 win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetMultiSamples(4);win.SetSize(950,830);win.AddRenderer(ren)
 strength={i:(1.0 if i in core else .76 if np.linalg.norm(p[i]-center)<3.5 else .55) for i in shown}
 for i,j in bonds:
  if i not in shown or j not in shown:continue
  # Suppress an erroneous MOL-inferred non-metal edge if implausibly long.
  if (i,j) not in contacts and np.linalg.norm(p[i]-p[j])>1.95:continue
  mid=(q[i]+q[j])/2;th=.105 if (i,j) in contacts else .078;th=.11 if i in water and j in water else th
  tube(ren,q[i],mid,th,shade(colors[e[i]],strength[i]));tube(ren,mid,q[j],th,shade(colors[e[j]],strength[j]))
 for i,j in hbs:
  if kind=='metal' and i==0 and j==w:
   mid=(q[i]+q[j])/2;tube(ren,q[i],mid,.10,rgb(colors[e[i]]));tube(ren,mid,q[j],.10,rgb(colors[e[j]]))
  else:dashed(ren,q[i],q[j])
 for i,j in prox:dashed(ren,q[i],q[j],'#c37522',.16)
 for i,j in aux:dashed(ren,q[i],q[j],'#8053a4',.34)
 for i in sorted(shown):add_sphere(ren,q[i],rad[e[i]]*(1.40 if i in water else 1),shade(colors[e[i]],strength[i]))
 cam=ren.GetActiveCamera();cam.SetPosition(0,0,50);cam.SetFocalPoint(0,0,0);cam.SetViewUp(0,1,0);cam.ParallelProjectionOn();cam.SetParallelScale(scale);cam.SetClippingRange(1,100)
 win.Render();f=vtk.vtkWindowToImageFilter();f.SetInput(win);f.Update();im=f.GetOutput();a=vtk_to_numpy(im.GetPointData().GetScalars()).reshape(830,950,3)[::-1].copy();win.Finalize()
 if ax is not None:
  ax.imshow(a,extent=(-scale*950/830,scale*950/830,-scale,scale));ax.set_axis_off();ax.set_xlim(-scale*950/830,scale*950/830);ax.set_ylim(-scale,scale)
  # Water label anchored to the actual oxygen coordinate.
  # Choose an offset from the active site; explicit display of one water per model.
  off=(12,16) if kind=='metal' else (16,12) if kind=='response' else (26,9)
  ax.annotate('H₂O',q[w,:2],xytext=off,textcoords='offset points',fontsize=9,weight='bold',color='#087e80',ha='center' if kind=='pocket' else 'left',va='center',bbox=dict(fc='white',ec='none',alpha=.9,pad=.6),arrowprops=dict(arrowstyle='-',color='#087e80',lw=.75))
  # labels placed adjacent to the chemical atom, not invented structural features.
  for idx,t in labels:
   off=(-10,10) if t=='N1' else (10,10) if t=='N2' else (-14,-12) if t=='OH2' else (13,-12)
   ax.annotate(t,q[idx,:2],xytext=off,textcoords='offset points',fontsize=8,weight='bold',color=ink,ha='right' if off[0]<0 else 'left',va='center',bbox=dict(fc='white',ec='none',alpha=.86,pad=1),arrowprops=dict(arrowstyle='-',color=muted,lw=.55))
 return a
# Use Arial when installed. Arimo is a metrically compatible fallback; do not bundle fonts.
fonts={f.name for f in font_manager.fontManager.ttflist}
font='Arial' if 'Arial' in fonts else 'Arimo' if 'Arimo' in fonts else 'Liberation Sans'
print('Font:',font)
plt.rcParams.update({'font.family':font,'font.size':9,'axes.labelsize':9,'xtick.labelsize':8,'ytick.labelsize':8,'pdf.fonttype':42,'svg.fonttype':'none','text.color':ink,'axes.labelcolor':ink,'xtick.color':ink,'ytick.color':ink,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#a8b4b9','axes.linewidth':.7,'savefig.facecolor':'white','mathtext.fontset':'custom','mathtext.rm':font,'mathtext.it':font+':italic','mathtext.bf':font+':bold'})

from matplotlib.ticker import MaxNLocator
from matplotlib.patches import Patch

def save(fig,name):
 for ext in ['pdf','png','svg']:fig.savefig(O/f'{name}.{ext}',dpi=400)
 plt.close(fig)
def axes(fig,xy):return fig.add_axes(xy)
def title(fig,x,y,s):fig.text(x,y,s,fontsize=11,weight='bold',color=ink,va='center')
def element_key(fig,y,allowed=None):
 handles=[Line2D([],[],marker='o',ls='',markerfacecolor=c,markeredgecolor='#a1a9ae' if e=='H' else c,label=e,ms=6) for e,c in colors.items() if allowed is None or e in allowed]
 fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.5,y),ncol=len(handles),frameon=False,fontsize=8,columnspacing=1.35,handletextpad=.3)
starts=['carboxyl','Zn_approach','bound_O'];names=['Free carboxylate O','Zn approach','Zn-bound O'];
fig=plt.figure(figsize=(7.5,8.2));title(fig,.045,.97,'a   Six optimized hydration configurations');fig.text(.96,.97,'1 H₂O per cluster',ha='right',va='center',color=muted,fontsize=8.5);
for j,n in enumerate(names):fig.text(.205+j*.295,.925,n,ha='center',weight='bold',fontsize=9.2)
for i,s in enumerate(['A','B']):
 y=.655-i*.245;fig.text(.045,y+.13,s,color=teal if i==0 else ochre,fontsize=18,weight='bold',va='center')
 for j,k in enumerate(starts):
  job=s+'_'+k;r=rcc[job];ax=axes(fig,[.07+j*.295,y,.275,.25]);render(C,job,'response',ax)
  fig.text(.207+j*.295,y-.003,f"{float(r['association_kJ_mol']):.2f} kJ/mol",ha='center',fontsize=10,weight='bold',color=teal if i==0 else ochre)
  fig.text(.207+j*.295,y-.024,f"Zn···O(w) {float(r['water_Zn_A']):.2f} Å",ha='center',fontsize=8,color=muted)
fig.legend(handles=[Line2D([],[],ls='--',color='#238b8b',label='H bond'),Line2D([],[],ls=':',color='#c37522',label='Zn···O(w) proximity'),Line2D([],[],ls='--',color='#8053a4',label='Auxiliary Zn···O')],loc='center',bbox_to_anchor=(.5,.36),ncol=3,frameon=False,fontsize=8)
fig.text(.045,.332,'b   Association energy',weight='bold',fontsize=11);fig.text(.52,.332,'c   Lowest sampled endpoint',weight='bold',fontsize=11)
ax=axes(fig,[.11,.105,.35,.19]);ax2=axes(fig,[.60,.105,.35,.19]);
for i,s in enumerate(['A','B']):
 vals=[float(rcc[s+'_'+k]['association_kJ_mol']) for k in starts];col=teal if i==0 else ochre;ax.scatter(np.arange(3)+(i-.5)*.12,vals,s=46,marker='o' if i==0 else 's',c=col,label=s,zorder=4);ax.text(.03,.94-i*.11,f'{s} span: {max(vals)-min(vals):.2f}',transform=ax.transAxes,color=col,fontsize=8,weight='bold',va='top')
ax.set_xticks(range(3),['Free O','Zn','Bound O']);ax.set_xlim(-.35,2.35);ax.set_ylim(-57,-25);ax.set_ylabel('Energy (kJ/mol)');ax.set_xlabel('Initial water placement');ax.grid(axis='y',color=grid);ax.legend(loc='lower right',frameon=False,ncol=2,fontsize=8)
# find saved decomposition columns by names, verified against final results table
for i,s in enumerate(['A','B']):
 r=rcc[s+'_carboxyl'];keys=[k for k in r if 'interaction' in k.lower() or 'deformation' in k.lower()];print('decomposition',keys)
 for j,(key,col,lab) in enumerate(zip(['interaction_kJ_mol','framework_deformation_kJ_mol','water_deformation_kJ_mol'],['#517aa1','#b87936','#a5adb2'],['Interaction','Framework def.','Water def.'])):
  v=float(r[key]);ax2.bar(i+(j-1)*.22,v,.19,color=col,label=lab if i==0 else None)
ax2.axhline(0,c=muted,lw=.7);ax2.set_xticks([0,1],['A','B']);ax2.set_ylabel('Energy (kJ/mol)');ax2.set_ylim(-62,14);ax2.legend(loc='upper center',bbox_to_anchor=(.5,-.17),ncol=3,frameon=False,fontsize=6.9,handlelength=1.1,columnspacing=.7);ax2.grid(axis='y',color=grid,zorder=0)
element_key(fig,.005,{'C','O','N','H','Zn'});save(fig,'hydration_Zn_endpoints')
fig=plt.figure(figsize=(7.5,6.9));title(fig,.045,.966,'a   Matched Mg/Zn hydration models');
for j,(job,label) in enumerate([('Mg_open_metal','Mg-MOF-74'),('Zn_linker_O','Zn-MOF-74')]):
 ax=axes(fig,[.02+j*.295,.56,.29,.35]);render(A,job,'metal',ax);fig.text(.165+j*.295,.915,label,ha='center',weight='bold',fontsize=10)
ax=axes(fig,[.68,.625,.29,.26]);
for j,sys in enumerate(['Mg','Zn']):
 vals=[float(r['association_kJ_mol']) for r in ra if r['system']==sys and r['association_kJ_mol']];
 for k,v in enumerate(vals):ax.scatter(v,j+(k-.5)*.22,c=colors[sys],marker='o' if k==0 else 's',s=42,zorder=4)
ax.scatter(-80.1,2,marker='D',c=muted,s=32);ax.scatter(-79.8,3,marker='D',facecolors='white',edgecolors=muted,s=32);ax.set_yticks(range(4),['Mg','Zn','PBE+D3','Corrected']);ax.set_ylim(3.45,-.45);ax.set_xlim(-88,-54);ax.grid(axis='x',color=grid);ax.set_xlabel('Energy (kJ/mol)');ax.legend(handles=[Line2D([],[],ls='',marker='o',color=ink,label='Metal start'),Line2D([],[],ls='',marker='s',color=ink,label='Linker O start')],loc='lower right',frameon=False,fontsize=7)
fig.text(.67,.55,'23.02 kJ/mol',fontsize=13,weight='bold',color=teal);fig.text(.67,.525,'Lowest sampled endpoints',fontsize=8,color=muted)
fig.add_artist(Line2D([.045,.97],[.50,.50],transform=fig.transFigure,color=grid,lw=1))
title(fig,.045,.47,'b   Retention of a published MOF-303 binding geometry');
ax=axes(fig,[.065,.085,.48,.34]);render(B,'MOF303_published_site','pocket',ax)
e,p,m,_=files(B,'MOF303_published_site');_,p0=xyz(B/'cluster_inputs/prepared_models/MOF303_published_site.xyz');inds=m['pocket_indices']+[5];d0=np.array([np.linalg.norm(p0[i]-p0[-3]) for i in inds]);d1=np.array([np.linalg.norm(p[i]-p[-3]) for i in inds]);obs=np.array([2.797,2.887,2.798]);ax=axes(fig,[.67,.164,.28,.21]);ax.scatter(d0,np.arange(4)-.12,marker='s',facecolors='white',edgecolors=muted,s=40,label='Periodic start');ax.scatter(d1,np.arange(4)+.12,c=teal,s=40,label='Relaxed xTB');ax.errorbar(obs,np.arange(3),xerr=[.007,.009,.006],fmt='D',mfc='white',mec=ink,ecolor=ink,ms=5,capsize=2,label='Diffraction');ax.set_yticks(range(4),['N1','N2','OH1','OH2']);ax.set_ylim(3.5,-.5);ax.set_xlim(2.65,3.2);ax.set_xlabel('O(w)···donor distance (Å)');ax.grid(axis='x',color=grid);ax.legend(loc='upper center',bbox_to_anchor=(.5,1.33),frameon=False,fontsize=7,ncol=2);fig.text(.67,.060,f'{max(abs(d1[:3]-obs)):.3f} Å max deviation',fontsize=10.5,weight='bold',color=teal);element_key(fig,.003);save(fig,'hydration_benchmarks')
# Emit additional contacts and all plot values in machine-readable form.
rows=[]
for s in ['A','B']:
 for k in starts:
  job=s+'_'+k;e,p,m,_=files(C,job);r=rcc[job];rows.append(dict(job=job,association_kJ_mol=r['association_kJ_mol'],water_Zn_A=np.linalg.norm(p[-3]-p[m['zn_index']]),auxiliary_Zn_O_A=np.linalg.norm(p[m['zn_index']]-p[m['cluster_labels'].index('O2@(0, 0, 0)')]) if s=='A' else ''))
with (O/'Zn_plot_values.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
with (O/'MOF303_contacts.csv').open('w') as f:w=csv.writer(f);w.writerow(['contact','start_A','relaxed_A','diffraction_A']);w.writerows(zip(['N1','N2','OH1','OH2'],d0,d1,[*obs,'']))
