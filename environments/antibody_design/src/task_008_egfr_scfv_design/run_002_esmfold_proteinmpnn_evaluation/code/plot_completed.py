#!/usr/bin/env python3
"""Render this task's two benchmark figures from saved result files; no inference."""
import csv
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

ROOT=Path(__file__).resolve().parents[4]
TASK=Path(__file__).resolve().parents[2].name
RESULTS=ROOT/'results'/TASK
OUT=ROOT/'benchmark/monoclonal_antibody_design'/TASK/'figures'
OUT.mkdir(parents=True,exist_ok=True)
RUNS=sorted(RESULTS.glob('run_*'))
BLUE='#246b91'; ORANGE='#ca763b'; GREEN='#35816a'; PURPLE='#7762a1'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'white','axes.titleweight':'bold','savefig.facecolor':'white'})
def read(p):
    with p.open()as f:return list(csv.DictReader(f))
def load(p):return json.loads(p.read_text())
def save(fig,name):
    fig.savefig(OUT/name,dpi=180,bbox_inches='tight');plt.close(fig)
def grid(ax,axis='x'):
    ax.set_axisbelow(True);ax.grid(axis=axis,color='#dfe5ea',lw=.7)
def flow(title,nodes,edges,footer):
    fig,ax=plt.subplots(figsize=(12,7));ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off')
    ax.text(.5,.97,title,ha='center',va='top',fontsize=17,fontweight='bold',color='#20384a')
    for start,end in edges:
        x,y,_,_=nodes[start];xx,yy,_,_=nodes[end]
        dx,dy=xx-x,yy-y
        if abs(dy)>.10: y+=.075*np.sign(dy);yy-=.075*np.sign(dy)
        else:x+=.105*np.sign(dx);xx-=.105*np.sign(dx)
        ax.add_patch(FancyArrowPatch((x,y),(xx,yy),arrowstyle='-|>',mutation_scale=13,lw=1.4,color='#7c91a0',zorder=1))
    for x,y,text,color in nodes:
        ax.add_patch(FancyBboxPatch((x-.106,y-.075),.212,.15,boxstyle='round,pad=0.009,rounding_size=0.015',facecolor=color,edgecolor='#afc3ce',lw=1,zorder=2))
        ax.text(x,y,text,ha='center',va='center',fontsize=10,color='#1d3342',linespacing=1.5,zorder=3)
    ax.text(.5,.035,footer,ha='center',va='bottom',fontsize=10,color='#4e6371',linespacing=1.5)
    save(fig,'workflow_results.png')

a={r['entity']:r for r in read(RUNS[0]/'metrics.csv')}
b={r['entity']:r for r in read(RUNS[1]/'metrics.csv')}
names=['reference']+sorted(n for n in a if n!='reference')
labels=['Reference']+[n.replace('cet_008_r1_','')for n in names[1:]]
fig,axs=plt.subplots(1,3,figsize=(13,5.8),layout='constrained')
for ax,values,title,unit in zip(axs,[[float(a[n]['iptm'])for n in names],[float(b[n]['esmfold_mean_plddt'])for n in names],[float(b[n]['mpnn_score_own_backbone'])for n in names]],['Complex interface confidence','Whole-scFv confidence','Own-backbone sequence score'],['Boltz2 ipTM (higher)','ESMFold pLDDT, 0–100 (higher)','ProteinMPNN NLL (lower)']):
    colors=[GREEN]+[BLUE]*6;ax.barh(labels,values,color=colors,height=.6)
    ax.invert_yaxis();ax.set_title(title,pad=12);ax.set_xlabel(unit);grid(ax)
    if unit.startswith('Boltz2'):ax.set_xlim(0,1.08)
    elif unit.startswith('ESMFold'):ax.set_xlim(0,99)
    else:ax.set_xlim(0,1.80)
    for i,v in enumerate(values):ax.text(v+.013*ax.get_xlim()[1],i,f'{v:.4f}'if not unit.startswith('ESMFold')else f'{v:.2f}',va='center',fontsize=9)
fig.suptitle('EGFR: six CDR redesigns and the matched native reference',fontsize=16,fontweight='bold')
save(fig,'results_comparison.png')
flow('EGFR: completed generation and matched evaluation',[
(.15,.75,'1YY9 preparation\nNative Fv + EGFR\nCDR-only mask','#eaf1f5'),
(.42,.75,'AntiBMPNN\n20 sequences\nFixed framework','#eaf1f5'),
(.69,.75,'Sequence gates\n6 selected designs\n+ native reference','#eaf1f5'),
(.69,.46,'Matched Boltz2\nscFv–EGFR complexes\n7 accepted models','#eaf4ef'),
(.42,.22,'ESMFold\nSame 7 sequences\n7 scFv models','#eaf1f5'),
(.69,.22,'ProteinMPNN\nOwn-backbone scoring\n7 NLL values','#eaf4ef')],[(0,1),(1,2),(2,3),(2,4),(4,5)],'Run 001: generation + complex evaluation. Run 002: single-chain confidence + sequence scoring.\nThe second run evaluates the fixed panel; it adds no new designs.')
