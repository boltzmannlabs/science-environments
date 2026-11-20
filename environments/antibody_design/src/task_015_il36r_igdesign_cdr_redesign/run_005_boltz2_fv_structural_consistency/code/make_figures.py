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

keys=[(0,'hcdr3','hcdr3','H3-only / H3'),(1,'hcdr123','hcdr1','H123 / H1'),(1,'hcdr123','hcdr2','H123 / H2'),(1,'hcdr123','hcdr3','H123 / H3')]
single=[];maximum=[];labels=[]
for idx,scope,cdr,label in keys:
    single.append(load(RUNS[idx]/'raw'/f'{scope}_1shot_aar.json')['per_cdr_aar'][cdr]);maximum.append(load(RUNS[idx]/'raw'/f'{scope}_100_aar.json')['per_cdr_aar'][cdr]);labels.append(label)
fig,axs=plt.subplots(1,2,figsize=(14,7.5),gridspec_kw={'width_ratios':[1,1.7]},layout='constrained');y=np.arange(4)
axs[0].barh(y-.16,single,height=.29,color=BLUE,label='Separate 1-shot');axs[0].barh(y+.16,maximum,height=.29,color=ORANGE,label='Per-CDR max / 100')
axs[0].set_yticks(y,labels);axs[0].set_ylim(4.3,-.6);axs[0].set_xlim(0,1.06);axs[0].set_xlabel('IgDesign native AAR (higher)');axs[0].set_title('Per-CDR sequence recovery');axs[0].legend(loc='lower right');grid(axs[0])
panel=read(RUNS[4]/'metrics.csv');ref=load(RUNS[4]/'boltz2_metrics.json')['members']['reference']['scrmsd_A_frame_aligned_vs_6u6u']['fv_all']
names=['Reference']+[r['candidate_id'].replace('antibmpnn','Anti').replace('igdesign','Ig').replace('hcdr123','H123').replace('hcdr3','H3')for r in panel];values=[ref]+[float(r['scrmsd_fv_A'])for r in panel]
axs[1].barh(names,values,color=[GREEN]+[ORANGE if 'Anti'in n else BLUE for n in names[1:]],height=.64);axs[1].invert_yaxis();axs[1].set_xlim(0,.74)
for i,v in enumerate(values):axs[1].text(v+.008,i,f'{v:.4f}',va='center',fontsize=9)
axs[1].set_xlabel('Whole-Fv backbone deviation vs crystal 6U6U (Å; lower)');axs[1].set_title('Fixed 12-design panel and matched native control');grid(axs[1])
fig.suptitle('IL-36R: native reconstruction and experimental-reference geometry',fontsize=16,fontweight='bold');save(fig,'results_comparison.png')
flow('IL-36R: four generation runs and one shared evaluation',[
(.14,.79,'R1 IgDesign H3\n1 + 100 samples\n3 panel members','#eaf1f5'),(.38,.79,'R2 IgDesign H123\n1 + 100 samples\n3 panel members','#eaf1f5'),
(.62,.79,'R3 AntiBMPNN H3\n40 sequences\n3 panel members','#fcf0e5'),(.86,.79,'R4 AntiBMPNN H123\n40 sequences\n3 panel members','#fcf0e5'),
(.50,.49,'R5 fixed panel\n12 designs + native\nExact VH/VL pairs','#eaf4ef'),
(.50,.24,'Matched Boltz2\n13 accepted Fv models\n6U6U backbone fit','#eaf1f5')],[(0,4),(1,4),(2,4),(3,4),(4,5)],'IgDesign selection: ascending cross-entropy. AntiBMPNN: recorded descending-NLL panel.\nNLL is lower-is-preferred; AntiBMPNN panel labels do not claim optimal likelihood selection.')
