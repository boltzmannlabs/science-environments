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

a=load(RUNS[1]/'aar_metrics.json')['runs'];p=read(RUNS[0]/'candidates.csv')
values=[a['hcdr3_1shot']['one_shot']['overall_aar'],a['hcdr3_best100']['best_of_n']['overall_aar'],a['hcdr123_1shot']['one_shot']['overall_aar'],a['hcdr123_best100']['best_of_n']['overall_aar']]+[max(float(r['designed_scope_aar'])for r in p if scope+'_scope'in r['candidate_id'])for scope in ['hcdr3','hcdr123']]
labels=['Ig H3 / 1-shot','Ig H3 / best 100','Ig H123 / 1-shot','Ig H123 / best 100','Anti H3 / best 20','Anti H123 / best 20']
fig,axs=plt.subplots(1,2,figsize=(14,8.2),gridspec_kw={'width_ratios':[1,1.5]},layout='constrained')
axs[0].barh(labels,values,color=[BLUE]*4+[ORANGE]*2,height=.6);axs[0].invert_yaxis();axs[0].set_xlim(0,1);axs[0].set_xlabel('Designed-scope native AAR (higher)');axs[0].set_title('Recovery with stated sampling budgets');grid(axs[0])
for i,v in enumerate(values):axs[0].text(v+.013,i,f'{v:.4f}',va='center',fontsize=9)
gg=[]
for i,run in enumerate(RUNS,1):
    data=[r for r in read(run/'shortlist.csv')if r['entry_role']!='reference_control']
    for r in sorted(data,key=lambda q:float(q['boltz2_fv_scrmsd_A'])):
        name=r['candidate_id'].replace('t014r001_','R1 ').replace('t014r002_','R2 ').replace('hcdr123_scope_','H123 ').replace('hcdr3_scope_','H3 ').replace('hcdr123_best100_','H123 ').replace('hcdr3_best100_','H3 ')
        gg.append((name,float(r['boltz2_hcdr3_scrmsd_A']),float(r['boltz2_fv_scrmsd_A'])))
y=np.arange(len(gg));axs[1].scatter([r[1]for r in gg],y,marker='o',s=37,color=ORANGE,label='HCDR3');axs[1].scatter([r[2]for r in gg],y,marker='s',s=31,color=BLUE,label='Whole Fv')
axs[1].set_yticks(y,[r[0]for r in gg]);axs[1].invert_yaxis();axs[1].set_xlim(0,5.4);axs[1].set_xlabel('Cα deviation vs predicted native Fv (Å; lower)');axs[1].set_title('All 20 evaluated candidate geometries');axs[1].legend(loc='lower right');grid(axs[1])
fig.suptitle('FXI: native recovery and predicted-reference consistency',fontsize=16,fontweight='bold');save(fig,'results_comparison.png')
flow('FXI: two completed generation and evaluation routes',[
(.28,.79,'R1 AntiBMPNN\n20 H3 + 20 H123\n40 samples','#fcf0e5'),(.72,.79,'R2 IgDesign\n1 + 100 per scope\n202 samples','#eaf1f5'),
(.28,.54,'Mask verification\n40 passes\n26 unique sequences','#fcf0e5'),(.72,.54,'Mask verification\n202 samples\n158 unique sequences','#eaf1f5'),
(.28,.29,'Boltz2 evaluation\n10 designs + control\n11 accepted models','#fcf0e5'),(.72,.29,'Boltz2 evaluation\n10 designs + control\n11 accepted models','#eaf1f5')],[(0,2),(1,3),(2,4),(3,5)],'Native sequence recovery and candidate geometry are separate endpoints.\nGeometry uses a Cα framework fit against the Boltz2-predicted native Fv; self-comparison is zero.')
