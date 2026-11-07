#!/usr/bin/env python3
"""Six MOF inherited-stability transfer figures from saved scientific results.

Only pinned, supplied scientific tables and the archived conceptual artwork are used.
No simulation, new model fit, experimental endpoint, or inferred crystal geometry is introduced.
Run from any directory: python make_figures.py
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, FancyArrowPatch
from matplotlib.lines import Line2D
from matplotlib.gridspec import GridSpec
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from PIL import Image

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'source_data'
ASSETS=ROOT/'assets'
OUT=ROOT/'figures'
for _ext in ('pdf', 'svg', 'png'):
    (OUT/_ext).mkdir(parents=True, exist_ok=True)
P= {'navy':'#18394D','ink':'#203545','teal':'#0B7C77','mint':'#DEF1ED',
    'gold':'#BD8B35','sand':'#F6EBDD','purple':'#745FA2','lav':'#EEEAF7',
    'coral':'#C65C52','rose':'#FAE8E5','slate':'#738999','muted':'#627787',
    'grid':'#DEE8EC','paper':'#FFFFFF','panel':'#F5F8F9','line':'#CEDDE3',
    'blue':'#366B88'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10.4,'axes.labelcolor':P['ink'],
 'axes.edgecolor':P['line'],'text.color':P['ink'],'xtick.color':P['muted'],'ytick.color':P['muted'],
 'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none','lines.solid_capstyle':'round',
 'svg.hashsalt':'mof-saved-results', 'savefig.facecolor':'white','figure.facecolor':'white'})

def figtitle(fig,kicker,title,subtitle):
    fig.text(.048,.968,kicker.upper(),ha='left',va='top',fontsize=10,weight='bold',color=P['teal'])
    fig.text(.048,.917,title,ha='left',va='top',fontsize=18.3,weight='bold',color=P['navy'])
    fig.text(.048,.851,subtitle,ha='left',va='top',fontsize=9.9,color=P['muted'])

def foot(fig,txt,y=.028):
    fig.text(.048,y,txt,fontsize=8.1,color=P['muted'],ha='left',va='bottom')

def panel(ax,title,subtitle=None):
    ax.set_title(title,loc='left',pad=11,color=P['navy'],fontweight='bold',fontsize=11.2)
    if subtitle: ax.text(0,1.008,subtitle,transform=ax.transAxes,fontsize=8.4,color=P['muted'],va='bottom')
    ax.spines[['top','right']].set_visible(False)
    ax.grid(axis='y',color=P['grid'],lw=.7,zorder=0)
    ax.set_axisbelow(True)

def save(fig,number):
    name=f'Figure_{number:02d}'
    for suf,kw in [('pdf',{}),('svg',{}),('png',{'dpi':450})]:
        metadata = {'CreationDate': None, 'ModDate': None} if suf == 'pdf' else {'Date': None} if suf == 'svg' else {}
        fig.savefig(OUT/suf/f'{name}.{suf}',bbox_inches=None,facecolor='white',metadata=metadata,**kw)
    plt.close(fig)

def roundbox(ax,x,y,w,h,face=P['panel'],edge=P['line'],radius=.025,lw=1.0):
    obj=FancyBboxPatch((x,y),w,h,boxstyle=f'round,pad=0.007,rounding_size={radius}',
                      facecolor=face,edgecolor=edge,linewidth=lw,transform=ax.transAxes,zorder=1)
    ax.add_patch(obj)
    return obj

def arrow(ax,p1,p2,color=P['navy'],lw=1.75):
    ax.add_patch(FancyArrowPatch(p1,p2,transform=ax.transAxes,arrowstyle='-|>',mutation_scale=15,
                                color=color,lw=lw,zorder=4))

def scatter_jitter(ax,x,y,color,seed=19,marker='o',size=43,alpha=.78,**kwargs):
    rng=np.random.default_rng(seed)
    return ax.scatter(np.asarray(x)+rng.uniform(-.095,.095,len(y)),y,s=size,c=color,marker=marker,
                      alpha=alpha,edgecolor='white',linewidth=.6,zorder=4,**kwargs)

# ---------- Figure 01: conceptual visual + rigorous workflow (no results) ----------
def make1():
 fig=plt.figure(figsize=(12.4,8.00));figtitle(fig,'01   /   chemical representation',
   'From framework chemistry to a family-exclusion test',
   'Which chemical distinctions are supplied to a student model, and what does its score agreement actually mean?')
 ax=fig.add_axes([.042,.085,.916,.714]);ax.set_axis_off();ax.set_xlim(0,1);ax.set_ylim(0,1)
 # Source art includes metal node, linker, coordination close-up, and network diagram.
 # It is an explicitly illustrative render, not a CIF-verified image.
 strip=Image.open(ASSETS/'concept_top.png')
 ax.imshow(strip,extent=[.145,.855,.708,.995],aspect='auto',interpolation='lanczos',zorder=2)
 ax.text(.05,.600,'A   Four controlled information blocks',fontsize=12,weight='bold',color=P['navy'],transform=ax.transAxes)
 blocks=[('B','GLOBAL GEOMETRY','6 variables','Pores · area · density',P['blue']),
         ('C','CONSTITUTION','23 variables','Composition · metal properties',P['teal']),
         ('L','CONTACT SHELL','13 variables','Metal–donor neighbours',P['gold']),
         ('I','DONOR ATTACHMENT','22 variables','Donor context · group incidences',P['purple'])]
 for j,(key,label,count,desc,c) in enumerate(blocks):
  x=.044+j*.242
  roundbox(ax,x,.362,.217,.207,face='white',edge=P['line'])
  ax.add_patch(Rectangle((x,.542),.217,.024,transform=ax.transAxes,facecolor=c,edgecolor='none',zorder=3))
  ax.text(x+.016,.497,key,fontsize=21,weight='bold',color=c,transform=ax.transAxes)
  ax.text(x+.057,.509,label,fontsize=9.2,weight='bold',color=P['navy'],transform=ax.transAxes)
  ax.text(x+.057,.472,count,fontsize=9,color=c,transform=ax.transAxes)
  ax.text(x+.016,.407,desc,fontsize=8.65,color=P['muted'],transform=ax.transAxes)
  if j<3: arrow(ax,(x+.218,.456),(x+.241,.456),c,1.5)
 ax.text(.05,.319,'B   What the validation establishes',fontsize=12,weight='bold',color=P['navy'],transform=ax.transAxes)
 xys=[(.048,.095,.240,.154,'TRAIN','Known element / topology families','Student model',P['blue']),
      (.381,.095,.242,.154,'TEST','Excluded element or exact label','Held-out student predictions',P['teal']),
      (.715,.095,.238,.154,'COMPARE','Predicted ordering vs inherited','Upstream model score',P['purple'])]
 for x,y,w,h,heading,sub,body,c in xys:
  roundbox(ax,x,y,w,h,face=P['panel'])
  ax.text(x+.015,y+.111,heading,fontsize=11.1,weight='bold',color=c,transform=ax.transAxes)
  ax.text(x+.015,y+.068,sub,fontsize=8.6,color=P['ink'],transform=ax.transAxes)
  ax.text(x+.015,y+.027,body,fontsize=8.0,color=P['muted'],transform=ax.transAxes)
 arrow(ax,(.292,.175),(.369,.175),P['navy']);arrow(ax,(.627,.175),(.705,.175),P['navy'])
 ax.text(.050,.029,'IMPORTANT BOUNDARY',fontsize=9.4,weight='bold',color=P['coral'],transform=ax.transAxes)
 ax.text(.220,.029,'Inherited stability estimates are not direct tests of water-induced framework survival.',
         fontsize=9.3,color=P['ink'],transform=ax.transAxes)
 foot(fig,'Illustrative MOF artwork from supplied Version A; descriptor counts and evaluation design from pinned CoRE analysis.')
 save(fig,1)

# ---------- Figure 02: four groups, every held-out family and mean +/- step sign --------
def make2():
 df=pd.read_csv(DATA/'family_water_ladder.csv');x=np.arange(4);mods=['B','B+C','+L','+I (= P)']
 fig=plt.figure(figsize=(12.5,7.45));figtitle(fig,'02   /   family-resolved ranking',
 'Constitution gives the largest average gain—but families differ',
 'Absolute Spearman agreement with inherited water scores; all eligible excluded families remain visible.')
 gs=fig.add_gridspec(2,4,left=.112,right=.984,top=.775,bottom=.123,height_ratios=[2.05,.87],
   wspace=.21,hspace=.18)
 cells=[('ASR','element','ASR  ·  elements'),('FSR','element','FSR  ·  elements'),
        ('ASR','allnodes','ASR  ·  topology labels'),('FSR','allnodes','FSR  ·  topology labels')]
 for j,(form,hold,title) in enumerate(cells):
  t=df[(df.form==form)&(df.holdout==hold)].reset_index(drop=True)
  vals=t[['B','C','L','I']].to_numpy(float); means=vals.mean(axis=0)
  ax=fig.add_subplot(gs[0,j]);ax.axhline(0,color=P['slate'],lw=1)
  for k,z in enumerate(vals):
   # Every family shown: highlight adverse final ranking in muted coral.
   col=P['coral'] if z[-1]<0 else '#9DAEB8'
   ax.plot(x,z,color=col,alpha=.55 if col==P['coral'] else .43,lw=1.25,zorder=2)
   ax.scatter(x,z,s=13,c=col,alpha=.7,zorder=3)
  ax.plot(x,means,color=P['navy'],lw=3.0,marker='D',ms=7.4,mfc=P['navy'],mec='white',mew=.9,zorder=7)
  for k,z in enumerate(means):
   ax.annotate(f'{z:.3f}',xy=(k,z),xytext=(0,11 if k!=0 else -17),textcoords='offset points',
              color=P['navy'],weight='bold',fontsize=8.9,ha='center',zorder=8)
  ax.set_ylim(-.75,1.03);ax.set_xlim(-.27,3.27);ax.set_yticks([-.5,0,.5,1.0])
  ax.set_xticks(x,mods,fontsize=9.2)
  panel(ax,f'{chr(65+j)}    {title}')
  ax.text(.02,.05,f'{len(t)} families',transform=ax.transAxes,fontsize=9,color=P['muted'])
  if j==0:ax.set_ylabel('Within-family Spearman ρ',fontsize=9.6)
  else:ax.set_yticklabels([])
  ax2=fig.add_subplot(gs[1,j]);changes=np.diff(vals,axis=1);mn=changes.mean(axis=0)
  ax2.axvline(0,color=P['slate'],lw=.95)
  cs=[P['teal'],P['gold'],P['purple']]
  for a,v in enumerate(mn):
   ax2.barh(a,v,height=.52,color=cs[a],zorder=2)
   cnt=(changes[:,a]>1e-10).sum();total=len(t)
   ax2.text(.02 if v>=0 else -.025,a,f'{v:+.3f}   {cnt}/{total}',va='center',ha='left' if v>=0 else 'right',
            fontsize=8.7,weight='bold',color=P['navy'],zorder=5)
  ax2.set_yticks([0,1,2],['+ constitution','+ coordination','+ attachment'] if j==0 else ['','',''])
  ax2.invert_yaxis();ax2.set_xlim(-.13,.72);ax2.set_xticks([0,.3,.6])
  ax2.spines[['top','right','left']].set_visible(False);ax2.grid(axis='x',alpha=.15)
  if j==0:ax2.set_xlabel('Mean paired Δρ  |  families helped',fontsize=9.2)
  else:ax2.set_xlabel('Δρ  |  helped / total',fontsize=8.8)

 foot(fig,'Family means are unweighted; ASR and FSR are distinct preparation forms, not independent experimental replications.')
 save(fig,2)

# ---------- Figure 03: chemistry subblock controls, no duplicated local examples ------
def make3():
 df=pd.read_csv(DATA/'family_conditional_contributions.csv')
 fig=plt.figure(figsize=(12.5,7.12));figtitle(fig,'03   /   conditional chemical information',
 'Not all chemically meaningful features add new information',
 'Paired representation changes, each against the declared parent, on the same test records.')
 gs=fig.add_gridspec(2,2,left=.076,right=.98,top=.786,bottom=.123,height_ratios=[1.07,1.00],
                     wspace=.24,hspace=.46)
 specs=[('ASR','element','ASR · element'),('FSR','element','FSR · element'),
        ('ASR','allnodes','ASR · topology'),('FSR','allnodes','FSR · topology')]
 # A: conditional constitution complementary contributions across 4 cases
 ax=fig.add_subplot(gs[0,0]);groups=[]
 for j,(form,hold,label) in enumerate(specs):
  t=df[(df.form==form)&(df.holdout==hold)]
  for i,(col,c) in enumerate([('composition_given_properties',P['teal']),('properties_given_composition',P['gold'])]):
   vals=t[col].values;idx=j*2+i;mean=vals.mean();groups.append((label,'comp.' if i==0 else 'props.',mean))
   ax.scatter(np.full(len(vals),idx)+np.random.default_rng(411+idx).uniform(-.10,.10,len(vals)),vals,
              s=24,color=c,alpha=.45,edgecolors='white',linewidth=.3,zorder=3)
   ax.scatter(idx,mean,s=102,color=c,edgecolors='white',lw=1.2,marker='D',zorder=6)
 for ix in [1.5,3.5,5.5]:ax.axvline(ix,color=P['grid'],lw=1)
 ax.axhline(0,color=P['slate'],lw=1);ax.set_xlim(-.45,7.45);ax.set_ylim(-.43,.9)
 ax.set_xticks(np.arange(8),['C','P']*4,fontsize=9)
 ax.set_xlabel('C: composition beyond properties  ·  P: properties beyond composition')
 ax.set_ylabel('Paired ΔSpearman ρ')
 panel(ax,'A    Constitution remains complementary')
 ax.text(.12,.94,'ASR el.        FSR el.       ASR topo.       FSR topo.',transform=ax.transAxes,fontsize=8.5,color=P['muted'])
 # B: all family-level properties minus identity values, including outlier Sc
 ax=fig.add_subplot(gs[0,1]);ax.axhline(0,color=P['slate'],lw=1)
 for j,(form,hold,label) in enumerate(specs):
  t=df[(df.form==form)&(df.holdout==hold)];v=t.properties_minus_identity.to_numpy();
  rng=np.random.default_rng(424+j);xx=np.full(len(v),j)+rng.uniform(-.20,.20,len(v))
  ax.scatter(xx,v,s=38,marker='o' if hold=='element' else 's',color=P['blue'] if form=='ASR' else P['gold'],
             edgecolors='white',lw=.5,alpha=.72,zorder=3)
  ax.scatter(j,np.mean(v),s=125,marker='D',color=P['navy'],edgecolors='white',lw=1.4,zorder=5)
 ax.set_xticks(range(4),['ASR\nelement','FSR\nelement','ASR\ntopology','FSR\ntopology'],fontsize=9)
 ax.set_ylim(-.39,1.22);ax.set_ylabel('Properties − identity  |  Δρ')
 panel(ax,'B    Continuous properties versus metal identity')
 ax.annotate('Sc (+1.119)',xy=(0,1.119488),xytext=(.55,1.03),arrowprops={'arrowstyle':'-','color':P['slate'], 'lw':.8},color=P['navy'],fontsize=9)
 # C: conditional donor context and attachment: per-group paired effects
 ax=fig.add_subplot(gs[1,:]);ax.axhline(0,color=P['slate'],lw=1)
 for j,(form,hold,label) in enumerate(specs):
  t=df[(df.form==form)&(df.holdout==hold)]
  for k,(col,c,marker) in enumerate([('context_given_attachment',P['purple'],'o'),('attachment_given_context',P['teal'],'s')]):
   vals=t[col].to_numpy();xx=j*2+k;
   ax.scatter(xx+np.random.default_rng(552+xx).uniform(-.13,.13,len(vals)),vals,c=c,s=34,
              marker=marker,alpha=.49,edgecolors='white',lw=.35,zorder=3)
   mn=vals.mean();lo=np.mean(vals)-(np.max(vals)-mn)/(len(vals)-1) if False else min(np.mean(np.delete(vals,i)) for i in range(len(vals)))
   hi=max(np.mean(np.delete(vals,i)) for i in range(len(vals)))
   ax.errorbar(xx,mn,yerr=[[mn-lo],[hi-mn]],fmt='D',color=P['navy'],mfc=c,mec='white',mew=1,
             elinewidth=2.1,capsize=4,markersize=9,zorder=8)
   ax.text(xx,mn+(.024 if mn>=0 else -.024),f'{mn:+.3f}',fontsize=9,ha='center',
           va='bottom' if mn>=0 else 'top',weight='bold',color=P['navy'])
 for k in [1.5,3.5,5.5]:ax.axvline(k,color=P['grid'],lw=1)
 ax.set_xlim(-.45,7.45);ax.set_ylim(-.192,.207)
 ax.set_xticks(range(8),['context','attach.']*4)
 ax.set_ylabel('Mean and family-specific Δρ')
 ax.set_xlabel('Within each protocol: context given attachment  /  attachment given context',fontsize=9.4)
 ax.grid(axis='y',alpha=.45)
 panel(ax,'C    Donor context and attachment depend on what is already encoded')

 foot(fig,'All comparisons reuse the same held-out test records and inherited score; the sign of Δρ is not a bond-strength or mechanism estimate.')
 save(fig,3)

# ---------- Figure 04: saved contact graphs, conceptual paintings, exact score changes -
def graph_draw(ax,record,graph):
 ax.set_xlim(-2.2,3.45);ax.set_ylim(-2.6,2.75);ax.set_aspect('equal');ax.axis('off')
 nodes=graph['nodes']
 loc={i:(float(n[4]),float(n[5])) for i,n in enumerate(nodes)}
 for pair in graph['context']:
  i,j=pair
  ax.plot([loc[i][0],loc[j][0]],[loc[i][1],loc[j][1]],lw=2.3,color='#A9BAC4',zorder=1)
 for tup in graph['contacts']:
  i,j=tup[:2]
  ax.plot([loc[i][0],loc[j][0]],[loc[i][1],loc[j][1]],lw=3.5,color=P['purple'],zorder=2)
 for k,n in enumerate(nodes):
  name,el,ix,img,px,py=n;x,y=loc[k]
  col=P['coral'] if el=='O' else P['navy'] if el=='C' else P['gold']
  ax.scatter(x,y,s=172 if el=='O' else 160,c=col,zorder=4,edgecolors='white',lw=1.5)
  label=name if img==[0,0,0] else f"{name}[{','.join(map(str,img))}]"
  if el=='O':xy=(x+(-.21 if x>0 else .16),y+(.33 if y>0 else -.34));ha='right' if x>0 else 'left'
  elif el=='C':xy=(x-.15,y+.30);ha='right'
  else:xy=(x+.27,y+.17 if y>0 else y-.19);ha='left'
  ax.text(*xy,label,fontsize=11.0,ha=ha,va='center',color=P['ink'],zorder=5,
          fontweight='bold' if name==graph['donor'] else 'normal')

def make4():
 ex=pd.read_csv(DATA/'local_examples.csv').set_index('structure_record_id');graph=json.loads((DATA/'local_graphs.json').read_text(encoding='utf-8'))
 fig=plt.figure(figsize=(12.4,9.5));figtitle(fig,'04   /   local chemical environments',
 'The same donor class can help one record and harm another',
 'Matched saved predictions and atom-labelled contact projections—not hydrolysis pathways or verified bond geometry.')
 starts=[.047,.527]
 for ix,(record,title,col,img) in enumerate([
  ('ASR-1180-1180','HELPED',P['teal'],'helped_illustration.png'),
  ('ASR-1065-1065','HARMED',P['coral'],'harmed_illustration.png')]):
  x0=starts[ix];w=.426;y0=.116;h=.671
  ax=fig.add_axes([x0,y0,w,h]);ax.axis('off')
  roundbox(ax,0.0,0.0,1.0,1.0,'white',P['line'],radius=.023,lw=1.15)
  ax.add_patch(Rectangle((.023,.94),.954,.029,facecolor=col,transform=ax.transAxes,zorder=2))
  ax.text(.040,.885,f'{chr(65+ix)}    {record}',fontsize=13,weight='bold',color=P['navy'],transform=ax.transAxes)
  ax.text(.966,.889,title,fontsize=11.1,ha='right',weight='bold',color=col,transform=ax.transAxes)
  ax.text(.045,.834,'O donor  ·  operational carboxyl-like context',fontsize=9.4,color=P['muted'],transform=ax.transAxes)
  ill=Image.open(ASSETS/img)
  # original cropped art contains an illustrative CIF-style label; use only as a conceptual motif.
  ax.imshow(ill,extent=[.045,.958,.56,.812],aspect='auto',interpolation='lanczos',transform=ax.transAxes,zorder=3)
  ax.text(.047,.548,'ILLUSTRATIVE ART — NOT A VERIFIED CIF',fontsize=9.3,weight='bold',color=col,transform=ax.transAxes)
  ax.text(.045,.515,'Saved periodic-image contact graph (2D display)',fontsize=9.4,weight='bold',color=P['navy'],transform=ax.transAxes)
  gax=fig.add_axes([x0+.042,.245,w-.084,.198]);graph_draw(gax,record,graph[record])
  vals=ex.loc[record];
  for k,(lab,val) in enumerate([('INHERITED',vals.inherited_score),('PARENT',vals.parent_prediction),('CHILD',vals.child_prediction),('Δ ERROR',vals.absolute_error_reduction)]):
   xx=.065+k*.235
   ax.text(xx,.170,lab,fontsize=8.7,color=P['muted'],ha='left',transform=ax.transAxes)
   ax.text(xx,.118,f'{float(val):+.3f}' if k==3 else f'{float(val):.3f}',
           fontsize=14.4,weight='bold',color=col if k==3 else P['navy'],ha='left',transform=ax.transAxes)
  ax.text(.045,.055,'Error reduction = |parent − target| − |child − target|',fontsize=8.6,color=P['muted'],transform=ax.transAxes)
 fig.text(.075,.089,'Graph key:  — context adjacency',color=P['muted'],fontsize=9)
 fig.text(.390,.089,'— shared cov15/CrystalNN15 contact',color=P['purple'],fontsize=9)
 foot(fig,'Examples selected after inspecting errors. Element-family label refers to the entire record; the visible graph may contain different metals.',.025)
 save(fig,4)

# ---------- Figure 05: heatmap with separate SOAP learner ----------------------------
def make5():
 df=pd.read_csv(DATA/'structural_summary.csv')
 fig=plt.figure(figsize=(12.4,7.05));figtitle(fig,'05   /   structural complexity',
 'A positive mean can conceal deterioration in most families',
 'Independent additions to a declared chemical parent; medians and favourable-family counts remain visible.')
 axes=fig.add_axes([.267,.201,.685,.550]);
 order=['G9','N','V','H','J'];contexts=[('ASR','element'),('FSR','element'),('ASR','allnodes'),('FSR','allnodes')]
 mat=np.array([[df[(df.branch==br)&(df.form==form)&(df.holdout==hold)].mean_delta_rho.iloc[0] for form,hold in contexts] for br in order])
 from matplotlib.colors import LinearSegmentedColormap
 cmap=LinearSegmentedColormap.from_list('paper_div',[P['coral'],'#F6D8D1','#F6F9F8','#B6DDD6',P['teal']],N=300)
 im=axes.imshow(mat,cmap=cmap,norm=colors.TwoSlopeNorm(vcenter=0,vmin=-.075,vmax=.075),aspect='auto')
 axes.set_xticks(range(4),['ASR  ·  element','FSR  ·  element','ASR  ·  topology','FSR  ·  topology'])
 axes.xaxis.tick_top();axes.tick_params(axis='x',length=0,pad=11,labelsize=10)
 axes.set_yticks(range(5),['G   Distances / angles','N   Periodic paths','V   Local clearance','H   Coordination spread','J   Contact covariances'])
 axes.tick_params(axis='y',length=0,pad=12,labelsize=10.2)
 for a,br in enumerate(order):
  for b,(form,hold) in enumerate(contexts):
   r=df[(df.branch==br)&(df.form==form)&(df.holdout==hold)].iloc[0]
   v=float(r.mean_delta_rho); med=float(r.median_delta_rho)
   ink='white' if abs(v)>.052 else P['navy']
   axes.text(b,a-.19,f'{v:+.3f}',ha='center',va='center',fontsize=12,weight='bold',color=ink)
   axes.text(b,a+.13,f'median {med:+.3f}',ha='center',va='center',fontsize=9.4,color=ink)
   axes.text(b,a+.33,f'{int(r.positive_families)}/{int(r.family_count)} helped',ha='center',va='center',fontsize=9.3,color=ink)
 for a in np.arange(-.5,5.5):axes.axhline(a,color='white',lw=4)
 for b in np.arange(-.5,4.5):axes.axvline(b,color='white',lw=4)
 for spine in axes.spines.values():spine.set_visible(False)
 axes.add_patch(Rectangle((-.485,.52),3.97,.97,fill=False,edgecolor=P['navy'],lw=1.45,ls='--',zorder=7))
 # Separate lower SOAP row to prevent cross-learner comparisons being mistaken for apples-to-apples
 bx=fig.add_axes([.267,.105,.685,.073]);bx.axis('off')
 bx.add_patch(Rectangle((0,0),1,1,facecolor=P['panel'],edgecolor=P['line'],lw=1,transform=bx.transAxes))
 for j,(form,hold) in enumerate(contexts):
  r=df[(df.branch=='SOAPkernel')&(df.form==form)&(df.holdout==hold)].iloc[0]
  bx.text((j+.5)/4,.61,f'{r.mean_delta_rho:+.3f}',ha='center',va='center',fontsize=11.1,weight='bold',color=P['navy'],transform=bx.transAxes)
  bx.text((j+.5)/4,.22,f'{int(r.positive_families)}/{int(r.family_count)} helped',ha='center',va='center',fontsize=8.5,color=P['muted'],transform=bx.transAxes)
 fig.text(.055,.134,'SOAP',fontsize=12,weight='bold',color=P['purple'])
 fig.text(.055,.104,'Kernel ridge\nseparate comparison',fontsize=9,color=P['muted'],va='top')

 foot(fig,'Dashed N row: mean gains (+0.019, +0.029) coexist with negative medians and only 4/13 and 4/11 improved element families.')
 save(fig,5)

# ---------- Figure 06: absolute reliability & full saved conditional intervals --------
def make6():
 df=pd.read_csv(DATA/'family_N_paths.csv')
 fig=plt.figure(figsize=(12.5,7.48));figtitle(fig,'06   /   absolute reliability',
 'Does adding periodic paths make an unfamiliar-family ranking useful?',
 'Absolute parent–child agreement and every held-element family change; positive Δρ alone is not sufficient.')
 gs=fig.add_gridspec(2,2,left=.075,right=.985,top=.788,bottom=.107,width_ratios=[1.15,1.00],height_ratios=[1,1],
                     hspace=.20,wspace=.22)
 ax=fig.add_subplot(gs[:,0]);ax.plot([-.33,1],[-.33,1],ls='--',lw=1.4,color=P['slate'],zorder=1)
 ax.axhline(0,color=P['grid'],lw=1);ax.axvline(0,color=P['grid'],lw=1)
 for form,c,mrk in [('ASR',P['navy'],'o'),('FSR',P['teal'],'s')]:
  t=df[df.form==form];
  ax.scatter(t.parent,t.child,s=90,c=[P['coral'] if v<0 else c for v in t.delta],
             edgecolors='white',linewidth=1,alpha=.92,zorder=4,marker=mrk)
 ax.set_xlim(-.32,.96);ax.set_ylim(-.30,.96);ax.set_aspect('equal',adjustable='box')
 ax.set_xlabel('Chemical parent P  |  Spearman ρ',fontsize=10.2)
 ax.set_ylabel('Parent + N  |  Spearman ρ',fontsize=10.2)
 panel(ax,'A    Absolute ranking: before versus after')
 ax.annotate('FSR Zr  (n = 21)\n−0.211  →  +0.008',xy=(-.211382,.0078049),xytext=(.05,-.16),
             fontsize=10,weight='bold',color=P['coral'],
             arrowprops={'arrowstyle':'->','lw':1.4,'color':P['coral']},
             bbox={'boxstyle':'round,pad=.4','fc':'white','ec':P['line']})
 ax.legend(handles=[Line2D([0],[0],marker='o',linestyle='None',markersize=8,mfc=P['navy'],mec='white',label='ASR'),
                    Line2D([0],[0],marker='s',linestyle='None',markersize=8,mfc=P['teal'],mec='white',label='FSR'),
                    Line2D([0],[0],linestyle='--',color=P['slate'],label='Unchanged performance')],
            loc='upper left',frameon=False,ncol=1,fontsize=9.2)
 # right two forest plots of all 24 element families, conditional intervals
 for gi,(form,title) in enumerate([('ASR','B    ASR  ·  4 / 13 helped'),('FSR','C    FSR  ·  4 / 11 helped')]):
  t=df[df.form==form].copy().sort_values('delta',ascending=False).reset_index(drop=True)
  ax2=fig.add_subplot(gs[gi,1]);y=np.arange(len(t))[::-1]
  ax2.axvline(0,color=P['slate'],lw=1.1)
  for ix,r in t.iterrows():
   co=P['teal'] if r.delta>0 else P['coral'];yy=y[ix]
   ax2.plot([r.lower,r.upper],[yy,yy],color='#AFC1C9',lw=1.75,zorder=2)
   ax2.plot([r.lower,r.lower],[yy-.13,yy+.13],color='#AFC1C9',lw=1.3)
   ax2.plot([r.upper,r.upper],[yy-.13,yy+.13],color='#AFC1C9',lw=1.3)
   ax2.scatter([r.delta],[yy],s=53,marker='D' if form=='ASR' else 's',c=co,
               edgecolors='white',lw=.8,zorder=4)
  ax2.set_yticks(y,[f'{z}  ({n})' for z,n in zip(t.family,t.n)],fontsize=8.4)
  ax2.set_xlim(-.58,.68);ax2.set_ylim(-.8,len(t)-.2);ax2.set_xticks([-.5,-.25,0,.25,.5])
  ax2.spines[['top','right','left']].set_visible(False);ax2.tick_params(axis='y',length=0)
  ax2.grid(axis='x',alpha=.24);ax2.set_axisbelow(True)
  panel(ax2,title)
  if gi==1:ax2.set_xlabel('Family Δρ with conditional 95% interval',fontsize=9.8)
  else:ax2.set_xticklabels([])

 foot(fig,'Only 4/13 ASR and 4/11 FSR held-out element families gain from N; most become worse despite positive equal-family means.')
 save(fig,6)

# ---------- saved-data verification ---------------------------------------------------
def qa():
 df=pd.read_csv(DATA/'family_water_ladder.csv')
 assert len(df)==34 and not df[['B','C','L','I']].isna().any().any()
 ex=pd.read_csv(DATA/'family_conditional_contributions.csv')
 assert len(ex)==34
 n=pd.read_csv(DATA/'family_N_paths.csv')
 assert len(n)==24
 assert np.allclose(n.child-n.parent,n.delta,atol=2e-7)
 for f in ('ASR','FSR'):
  d=n[n.form==f]
  expected=13 if f=='ASR' else 11
  assert len(d)==expected and sum(d.delta>0)==4
  means=df[(df.form==f)&(df.holdout=='element')][['B','C','L','I']].mean().round(3)
  assert np.isclose(means['I'],.489 if f=='ASR' else .423,atol=.001)
  print(f,'water mean',means.to_dict(),'periodic N mean',d.delta.mean(),'families helped',sum(d.delta>0))
 a=pd.read_csv(DATA/'local_examples.csv')
 assert np.allclose((a.parent_prediction-a.inherited_score).abs()-(a.child_prediction-a.inherited_score).abs(),a.absolute_error_reduction,atol=2e-7)
 print('QA PASS: 34 ladder families; 34 subblock families; 24 periodic families; six saved error examples.')

if __name__=='__main__':
 qa()
 for f in (make1,make2,make3,make4,make5,make6):
  f();print(f.__name__,'written')
