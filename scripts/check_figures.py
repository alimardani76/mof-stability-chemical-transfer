#!/usr/bin/env python3
"""Validate saved scientific results, plotted values, labels, and complete outputs."""
from __future__ import annotations
from collections import defaultdict
from pathlib import Path
import csv, math, re, json
R=Path(__file__).resolve().parents[1]
D=R/'figure_sources'/'source_data'

def rows(filename):
    with (D/filename).open(newline='',encoding='utf-8') as f:
        return list(csv.DictReader(f))

ladder=rows('family_water_ladder.csv')
assert len(ladder)==34, f'Expected 34 family ladders, found {len(ladder)}'
for r in ladder:
    assert -1<=min(float(r[k]) for k in ('B','C','L','I'))
    assert max(float(r[k]) for k in ('B','C','L','I'))<=1
for form,hold,n,targets in [
    ('ASR','element',13,(.082,.412,.471,.489)),
    ('FSR','element',11,(.183,.333,.401,.423)),
    ('ASR','allnodes',5,(.060,.593,.588,.621)),
    ('FSR','allnodes',5,(.111,.522,.556,.582))]:
    subset=[r for r in ladder if r['form']==form and r['holdout']==hold]
    assert len(subset)==n,(form,hold,len(subset))
    means=[sum(float(r[k]) for r in subset)/n for k in ('B','C','L','I')]
    assert all(abs(a-b)<.001 for a,b in zip(means,targets)),(form,hold,means)

conditional=rows('family_conditional_contributions.csv')
assert len(conditional)==34
for r in conditional:
    for k in ['properties_minus_identity','composition_given_properties','properties_given_composition',
              'context_given_attachment','attachment_given_context']:
        assert math.isfinite(float(r[k]))

paths=rows('family_N_paths.csv')
assert len(paths)==24
for r in paths:
    a,b,d=float(r['parent']),float(r['child']),float(r['delta'])
    assert math.isclose(b-a,d,abs_tol=6e-6),(r['form'],r['family'],a,b,d)
for form,total,positive in [('ASR',13,4),('FSR',11,4)]:
    vals=[r for r in paths if r['form']==form]
    assert len(vals)==total
    assert sum(float(r['delta'])>0 for r in vals)==positive
zr=[r for r in paths if r['form']=='FSR' and r['family']=='Zr']
assert len(zr)==1 and abs(float(zr[0]['parent'])+.211)<.001 and abs(float(zr[0]['child'])-.008)<.001

examples=rows('local_examples.csv')
assert len(examples)==6
for r in examples:
    target,parent,child=map(float,[r['inherited_score'],r['parent_prediction'],r['child_prediction']])
    delta=abs(parent-target)-abs(child-target)
    assert abs(delta-float(r['absolute_error_reduction']))<1e-7,(r['structure_record_id'],delta)

struct=rows('structural_summary.csv')
assert len(struct)>=20
for r in struct:
    assert 0<=int(r['positive_families'])<=int(r['family_count'])

# The immutable scientific inputs are the selected, verified slice of the original manifest.
from manifest import verify
verify(R/'data/aggregate/INPUT_SHA256.csv', exact=False)
from make_tables import build, CELLS
for name, expected in build().items():
    assert (R/'generated'/name).read_text(encoding='utf-8') == expected, name

macros = dict(re.findall(r'\\csname num([^\\]+)\\endcsname\{([^}]+)\}',
                         (R/'generated/numbers.tex').read_text(encoding='utf-8')))
for name in ['water_ladder.tex','subblocks.tex','structural.tex','endpoint_ladders.tex']:
    table = (R/'generated'/name).read_text(encoding='utf-8')
    assert set(re.findall(r'\\Num\{([^}]+)\}',table)).issubset(macros), name
    assert not re.search(r'\\(?:input|include|includegraphics|documentclass|bibliography)\b',table)

def aggregate(name):
    with (R/'data/aggregate'/name).open(encoding='utf-8',newline='') as f:
        return list(csv.DictReader(f))

def close(a,b,tol=5.1e-4):
    assert math.isclose(float(a),float(b),abs_tol=tol), (a,b,tol)

# Cross-check condensed family inputs against the independently retained rounded summaries.
water=aggregate('figure_02_ladder.csv')
increment=aggregate('figure_03_increment.csv')
for form,hold,n in CELLS:
    subset=[r for r in ladder if r['form']==form and r['holdout']==hold]
    assert len({r['family'] for r in subset})==n
    summary=[r for r in water if r['form']==form and r['holdout']==hold]
    assert len(summary)==4
    for k,r in zip(['B','C','L','I'],summary):
        close(sum(float(z[k]) for z in subset)/n,r['mean_equal_family_spearman'])
    sums=[r for r in increment if r['form']==form and r['holdout']==hold]
    for a,b,r in zip(['B','C','L'],['C','L','I'],sums):
        close(sum(float(z[b])-float(z[a]) for z in subset)/n,r['mean_paired_increment_rho'])
    sub=[r for r in conditional if r['form']==form and r['holdout']==hold]
    assert {(r['family'],r['n']) for r in sub}=={(r['family'],r['n']) for r in subset}
    for col,suffix in [('properties_minus_identity','propertiesminusidentity'),
                       ('composition_given_properties','compositiongivenproperties'),
                       ('properties_given_composition','propertiesgivencomposition'),
                       ('context_given_attachment','contextgivenattachmentcov'),
                       ('attachment_given_context','attachmentgivencontextcov')]:
        close(sum(float(r[col]) for r in sub)/n,macros['sub'+form+hold+suffix])

assert struct==aggregate('figure_04_structural.csv')
assert examples==aggregate('figure_03_examples.csv')
derived=aggregate('fig3_full_precision_derived_metrics.csv')
for a,b in zip(examples,derived):
    assert a['structure_record_id']==b['structure_record_id']
    for key in ['parent_absolute_error','child_absolute_error']:
        prediction='parent_prediction' if key.startswith('parent') else 'child_prediction'
        close(abs(float(a[prediction])-float(a['inherited_score'])),b[key],1e-9)
    close(a['absolute_error_reduction'],b['error_change_check'],1e-9)

for form,hold,n in CELLS[:2]:
    sub=[r for r in paths if r['form']==form]
    saved=next(r for r in struct if r['branch']=='N' and r['form']==form and r['holdout']==hold)
    close(sum(float(r['delta']) for r in sub)/n,saved['mean_delta_rho'])
    import statistics
    close(statistics.median(float(r['delta']) for r in sub),saved['median_delta_rho'])
    assert int(saved['positive_families'])==sum(float(r['delta'])>0 for r in sub)
for r in paths:
    assert all(math.isfinite(float(r[k])) for k in ['parent','child','delta','lower','upper'])
    assert -1<=float(r['parent'])<=1 and -1<=float(r['child'])<=1
    assert float(r['lower'])<=float(r['upper'])
for r in aggregate('figure_05_zr_case.csv'):
    source=next(z for z in paths if z['form']=='FSR' and z['family']=='Zr')
    assert int(r['n'])==int(source['n'])==21
    close(r['rho'],source['parent' if r['model']=='P' else 'child'])

graphs=json.loads((D/'local_graphs.json').read_text(encoding='utf-8'))
assert graphs==json.loads((R/'data/aggregate/fig3_graph_projection_snapshot.json').read_text(encoding='utf-8'))
lineage=aggregate('fig3_github_source_manifest.csv')
assert set(graphs)=={r['structure_record_id'] for r in examples}
for r in lineage:
    g=graphs[r['record_id']]
    assert g['sha']==r['github_blob_sha']
    assert g['repo_tree_sha']=='65725ae2b8b7f25d15ba08e68632198cc0ddc954'
    assert g['donor'] in {node[0] for node in g['nodes']}
    for node in g['nodes']:
        assert len(node)==6 and len(node[3])==3
        assert all(math.isfinite(float(v)) for v in node[4:])
    for edge in g['context']+g['contacts']:
        assert all(0<=int(index)<len(g['nodes']) for index in edge[:2])

# Build the actual plot definitions in memory, then inspect the arrays given to Matplotlib.
import importlib.util
import numpy as np
import fitz
from PIL import Image
import xml.etree.ElementTree as ET
spec=importlib.util.spec_from_file_location('saved_figures',R/'figure_sources/make_figures.py')
plot=importlib.util.module_from_spec(spec)
spec.loader.exec_module(plot)
definitions=json.loads((R/'figure_sources/figure_definitions.json').read_text(encoding='utf-8'))
captured={}
plot.save=lambda fig,number: captured.update({number:fig})
for definition in definitions['figures']:
    for source in definition['inputs']:
        assert (R/'figure_sources'/source).is_file(),source
    getattr(plot,definition['function'])()

f=captured[2]
for j,(form,hold,n) in enumerate(CELLS):
    values=np.array([[float(r[k]) for k in ['B','C','L','I']]
                     for r in ladder if r['form']==form and r['holdout']==hold])
    ax=f.axes[2*j]
    lines=[line for line in ax.lines if len(line.get_ydata())==4]
    assert len(lines)==n+1
    np.testing.assert_allclose([line.get_ydata() for line in lines[:-1]],values,atol=1e-12)
    np.testing.assert_allclose(lines[-1].get_ydata(),values.mean(axis=0),atol=1e-12)
    np.testing.assert_allclose([p.get_width() for p in f.axes[2*j+1].patches],np.diff(values,axis=1).mean(axis=0),atol=1e-12)

f=captured[3]
for j,(form,hold,n) in enumerate(CELLS):
    sub=[r for r in conditional if r['form']==form and r['holdout']==hold]
    for k,col in enumerate(['composition_given_properties','properties_given_composition']):
        vals=np.array([float(r[col]) for r in sub])
        np.testing.assert_allclose(f.axes[0].collections[4*j+2*k].get_offsets()[:,1],vals)
        close(f.axes[0].collections[4*j+2*k+1].get_offsets()[0,1],vals.mean(),1e-12)
    vals=np.array([float(r['properties_minus_identity']) for r in sub])
    np.testing.assert_allclose(f.axes[1].collections[2*j].get_offsets()[:,1],vals)
    for k,col in enumerate(['context_given_attachment','attachment_given_context']):
        vals=np.array([float(r[col]) for r in sub])
        np.testing.assert_allclose(f.axes[2].collections[4*j+2*k].get_offsets()[:,1],vals)
        low,high=min(np.mean(np.delete(vals,i)) for i in range(n)),max(np.mean(np.delete(vals,i)) for i in range(n))
        np.testing.assert_allclose(f.axes[2].collections[4*j+2*k+1].get_segments()[0][:,1],[low,high])

f=captured[4]
for j,rid in enumerate(['ASR-1180-1180','ASR-1065-1065']):
    ax=f.axes[2*j+1]
    g=graphs[rid]
    np.testing.assert_allclose([c.get_offsets()[0] for c in ax.collections],[node[4:] for node in g['nodes']])
    assert len(ax.lines)==len(g['context'])+len(g['contacts'])
    r=next(z for z in examples if z['structure_record_id']==rid)
    labels=[text.get_text() for text in f.axes[2*j].texts]
    for key in ['inherited_score','parent_prediction','child_prediction']:
        assert f'{float(r[key]):.3f}' in labels
    assert f"{float(r['absolute_error_reduction']):+.3f}" in labels

f=captured[5]
expected=np.array([[float(next(r['mean_delta_rho'] for r in struct if r['branch']==br and r['form']==form and r['holdout']==hold))
                    for form,hold,n in CELLS] for br in ['G9','N','V','H','J']])
np.testing.assert_allclose(f.axes[0].images[0].get_array(),expected)
for a,br in enumerate(['G9','N','V','H','J']):
    for b,(form,hold,n) in enumerate(CELLS):
        r=next(z for z in struct if z['branch']==br and z['form']==form and z['holdout']==hold)
        texts=[t.get_text() for t in f.axes[0].texts if abs(t.get_position()[0]-b)<1e-9 and abs(t.get_position()[1]-a)<.4]
        assert f"median {float(r['median_delta_rho']):+.3f}" in texts
        assert f"{r['positive_families']}/{r['family_count']} helped" in texts

f=captured[6]
for j,form in enumerate(['ASR','FSR']):
    sub=[r for r in paths if r['form']==form]
    np.testing.assert_allclose(f.axes[0].collections[j].get_offsets(),[[float(r['parent']),float(r['child'])] for r in sub])
    ordered=sorted(sub,key=lambda r:float(r['delta']),reverse=True)
    ax=f.axes[j+1]
    for k,r in enumerate(ordered):
        np.testing.assert_allclose(ax.lines[1+3*k].get_xdata(),[float(r['lower']),float(r['upper'])])
        close(ax.collections[k].get_offsets()[0,0],r['delta'],1e-12)
        assert ax.get_yticklabels()[k].get_text()==f"{r['family']}  ({r['n']})"

def normalized(text):
    return ' '.join(text.replace('\u2212','-').split())

for definition in definitions['figures']:
    number=definition['number']
    name=f'Figure_{number:02d}'
    f=captured[number]
    for ext in ['pdf','svg','png']:
        p=R/'figure_sources/figures'/ext/f'{name}.{ext}'
        assert p.is_file() and p.stat().st_size>1000,p
    pdf=fitz.open(R/'figure_sources/figures/pdf'/f'{name}.pdf')
    assert len(pdf)==1
    np.testing.assert_allclose([pdf[0].rect.width,pdf[0].rect.height],f.get_size_inches()*72,atol=.01)
    svg=ET.parse(R/'figure_sources/figures/svg'/f'{name}.svg').getroot()
    assert svg.tag.endswith('svg')
    texts=[normalized(pdf[0].get_text()),normalized(' '.join(svg.itertext()))]
    for text in texts:
        for label in definition['panels']+definition['labels']:
            assert normalized(label) in text,(number,label)
    with Image.open(R/'figure_sources/figures/png'/f'{name}.png') as im:
        np.testing.assert_allclose(im.size,np.floor(f.get_size_inches()*450),atol=1)
        im.verify()
    pdf.close()
    plot.plt.close(f)
    print(f'PASS: {name} PDF/SVG/PNG dimensions, labels, panels and plotted scientific values')
assert len(list((R/'figure_sources/figures').rglob('*.*')))==18
for path in definitions['reference_support']['paths']:
    with fitz.open(R/path) as pdf:
        assert len(pdf)==1
        assert 'Original result-selected illustrations' in pdf[0].get_text()
print('PASS: 34 family ladders, 34 conditional contrasts, 24 N effects, six saved examples; three regenerated tables; saved subblock/macro integrity; three reference PDFs.')
