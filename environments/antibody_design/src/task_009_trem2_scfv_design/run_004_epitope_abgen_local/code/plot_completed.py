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

fig,axs=plt.subplots(1,2,figsize=(13,7.5),gridspec_kw={'width_ratios':[1.7,1]},layout='constrained')
labels=[];scores=[];colors=[];best=[]
for i,run in enumerate(RUNS,1):
    data=read(run/'metrics.csv');cc=[BLUE,ORANGE,GREEN,PURPLE][i-1]
    for row in data:
        name=row.get('candidate_id')or row.get('candidate')
        name=name.replace('_T009-C',' / C')
        labels.append(f'R{i} {name}');scores.append(float(row['iptm']));colors.append(cc)
    best.append(max(float(row['iptm'])for row in data))
axs[0].barh(labels,scores,color=colors,height=.65);axs[0].invert_yaxis();axs[0].set_xlim(0,1.06)
axs[0].axvline(.8987,color='#243b48',ls='--',lw=1.4,label='Matched reference 0.8987');axs[0].legend(loc='lower right',fontsize=9)
for i,v in enumerate(scores):axs[0].text(v+.012,i,f'{v:.4f}',va='center',fontsize=9)
axs[0].set_title('All 15 evaluated candidates');axs[0].set_xlabel('Boltz2 ipTM (higher)');grid(axs[0])
axs[1].barh(['R1 AntiBMPNN','R2 IgDesign','R3 AgCDR + IF','R4 Epitope + IF'],best,color=[BLUE,ORANGE,GREEN,PURPLE],height=.5)
axs[1].invert_yaxis();axs[1].set_xlim(0,1.06);axs[1].axvline(.8987,color='#243b48',ls='--',lw=1.4)
for i,v in enumerate(best):axs[1].text(v+.012,i,f'{v:.4f}',va='center')
axs[1].set_title('Best observed candidate by route');axs[1].set_xlabel('Boltz2 ipTM (higher)');grid(axs[1])
fig.suptitle('TREM2: four completed routes and one matched control',fontsize=16,fontweight='bold')
save(fig,'results_comparison.png')
flow('TREM2: completed design routes',[
(.14,.79,'R1 AntiBMPNN\n40 sequences\n39 unique','#eaf1f5'),(.38,.79,'R2 IgDesign\n100 sequences\n95 pass / unique','#fcf0e5'),
(.62,.79,'R3 AgCDR + IF\n8 backbones → 1\n40 sequences','#eaf4ef'),(.86,.79,'R4 Epitope + IF\n4 backbones\n160 sequences','#f1edf7'),
(.14,.49,'4 evaluated\n1 low-confidence\nfollow-up exclusion','#eaf1f5'),(.38,.49,'4 evaluated\nExact model\nsequence checks','#fcf0e5'),
(.62,.49,'4 evaluated\nSample-7\nsequence panel','#eaf4ef'),(.86,.49,'94 gate passes\n3 evaluated\n1 shortlisted','#f1edf7'),
(.50,.20,'Matched Boltz2\n15 candidate models\nNative control 0.8987','#eaf1f5')],[(0,4),(1,5),(2,6),(3,7),(4,8),(5,8),(6,8),(7,8)],'Every route’s best candidate ipTM is below the matched reference. IF = inverse folding.\nGeneration budgets differ; counts distinguish backbones, sequences and evaluated complexes.')
