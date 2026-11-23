import numpy as np
from Bio.PDB import PDBParser
from Bio.PDB.SASA import ShrakeRupley
B="/home/boltzmann4/.sci/profiles/monoclonal_antibodies1/cache/scratch/vhh_run/boltz2"
KD={'I':4.5,'V':4.2,'L':3.8,'F':2.8,'C':2.5,'M':1.9,'A':1.8,'G':-0.4,'T':-0.7,'S':-0.8,'W':-0.9,'Y':-1.3,'P':-1.6,'H':-3.2,'E':-3.5,'Q':-3.5,'D':-3.5,'N':-3.5,'K':-3.9,'R':-4.5}
CH3={"ALA":"A","ARG":"R","ASN":"N","ASP":"D","CYS":"C","GLN":"Q","GLU":"E","GLY":"G","HIS":"H","ILE":"I","LEU":"L","LYS":"K","MET":"M","PHE":"F","PRO":"P","SER":"S","THR":"T","TRP":"W","TYR":"Y","VAL":"V"}
# Chothia max SASA (A^2)
MAXS={"ALA":127,"ARG":257,"ASN":186,"ASP":163,"CYS":148,"GLN":209,"GLU":189,"GLY":80,"HIS":156,"ILE":187,"LEU":187,"LYS":210,"MET":164,"PHE":227,"PRO":140,"SER":140,"THR":163,"TRP":250,"TYR":215,"VAL":165}
p=PDBParser(QUIET=True)
for tag in ["run0s4","run2s1"]:
    m=p.get_structure(tag,f"{B}/{tag}/boltz_pdb/1_model_0.pdb")[0]
    vhh=[x for x in m if x.get_id()=="A"][0]
    res=[r for r in vhh if r.id[0]==' ']
    # compute over whole structure so interface burial is captured
    ShrakeRupley().compute(m, level="R")
    rows=[]
    for r in res:
        rn=r.get_resname(); a=CH3[rn]
        fasa=r.sasa/MAXS[rn]
        rows.append((r.id[1],a,fasa))
    surf=[(a,f) for _,a,f in rows if f>0.3]
    kd_surf=sum(KD[a] for a,f in surf)/len(surf)
    frac=len(surf)/len(rows)
    print(f"{tag}: n_res {len(rows)} | surface(FASA>0.3) {len(surf)} ({frac:.2f}) | surface-KD {kd_surf:.3f}")
