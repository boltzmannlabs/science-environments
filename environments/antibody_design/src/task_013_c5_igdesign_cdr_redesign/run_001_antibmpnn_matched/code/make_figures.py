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

s=load(RUNS[0]/'metrics_summary.json');a=s['aar_endpoints']
keys=['run_002_hcdr3_1shot','run_002_hcdr3_100','run_002_hcdr123_1shot','run_002_hcdr123_100','run_001_hcdr3only','run_001_hcdr123']
labels=['Ig H3 / 1-shot','Ig H3 / n=100','Ig H123 / 1-shot','Ig H123 / n=100','Anti H3 / n=100','Anti H123 / n=100']
fig,axs=plt.subplots(1,2,figsize=(13,6.2),layout='constrained');y=np.arange(6)
axs[0].barh(y-.16,[a[k]['HCDR3']['mean_aar']for k in keys],height=.29,color=BLUE,label='Pool mean')
axs[0].barh(y+.16,[a[k]['HCDR3']['max_aar']for k in keys],height=.29,color=ORANGE,label='Pool maximum')
axs[0].set_yticks(y,labels);axs[0].invert_yaxis();axs[0].set_xlim(0,1);axs[0].set_xlabel('HCDR3 native AAR (higher)');axs[0].set_title('Native HCDR3 reconstruction');axs[0].legend();grid(axs[0])
names=sorted(s['candidates']);y=np.arange(len(names));short=[n.replace('hcdr3only','H3').replace('hcdr123','H123').replace('hcdr3','H3')for n in names]
for off,track,col in [(-.16,'boltz2',BLUE),(.16,'esmfold',ORANGE)]:axs[1].barh(y+off,[s['candidates'][n][track]['fv_scrmsd']for n in names],height=.29,color=col,label=track)
axs[1].set_yticks(y,short);axs[1].invert_yaxis();axs[1].set_xlabel('Fv Cα deviation vs native prediction (Å; lower)');axs[1].set_title('Matched-predictor candidate geometry');axs[1].legend();grid(axs[1])
fig.suptitle('C5: sequence recovery and predicted-reference consistency',fontsize=16,fontweight='bold');save(fig,'results_comparison.png')
flow('C5: two generation runs and shared two-predictor evaluation',[
(.28,.79,'R1 AntiBMPNN\n100 H3 + 100 H123\n200 sequences','#eaf1f5'),(.72,.79,'R2 IgDesign\n1 + 100 per scope\n202 sequences','#fcf0e5'),
(.28,.53,'2 AntiBMPNN\nselected designs\nNative AAR','#eaf1f5'),(.72,.53,'4 IgDesign\nselected designs\nNative AAR','#fcf0e5'),
(.50,.33,'Shared fixed panel\n6 designs + reference\n7 sequence pairs','#eaf4ef'),
(.28,.14,'Boltz2 Fv\n7 accepted models\nCα framework fit','#eaf1f5'),(.72,.14,'ESMFold scFv\n7 accepted models\nLinker excluded','#fcf0e5')],[(0,2),(1,3),(2,4),(3,4),(4,5),(4,6)],'Candidate geometry: against the same-predictor native model. Native controls: against crystal 5I5K.')
