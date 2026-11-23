import csv, json
# load human repertoire 9-mers
def load9mers(path):
    seqs=[]
    cur=""
    for line in open(path):
        line=line.strip()
        if line.startswith(">"):
            if cur: seqs.append(cur)
            cur=""
        elif line: cur+=line
    if cur: seqs.append(cur)
    mers=set()
    for s in seqs:
        for i in range(len(s)-8): mers.add(s[i:i+9])
    return mers
mers=set()
for p in ["human_ig.fasta","human_ig_p1.fasta","human_ig_p2.fasta"]:
    try: mers|=load9mers(p)
    except: pass
print("human 9-mer repertoire size:",len(mers))
# Kyte-Doolittle
KD={'I':4.5,'V':4.2,'L':3.8,'F':2.8,'C':2.5,'M':1.9,'A':1.8,'G':-0.4,'T':-0.7,'S':-0.8,'W':-0.9,'Y':-1.3,'P':-1.6,'H':-3.2,'E':-3.5,'Q':-3.5,'D':-3.5,'N':-3.5,'K':-3.9,'R':-4.5}
res=list(csv.DictReader(open("antibmpnn_out/antibmpnn_results.csv")))
out=[]
for idx,row in enumerate(res):
    seq=row['heavy_chain']; pdb=row['pdb_name']
    # humanness: fraction of VHH 9-mers in repertoire
    vmers={seq[i:i+9] for i in range(len(seq)-8)}
    hum=len(vmers & mers)/len(vmers) if vmers else 0
    kd=sum(KD[c] for c in seq)/len(seq)
    out.append({"id":f"ppiflow_HA_{pdb.replace('.pdb','')}_s{idx%5+1}","pdb":pdb,"seq":seq,"humanness":round(hum,4),"kd_mean":round(kd,3),"n_vhh_mers":len(vmers)})
# sort by humanness desc
out.sort(key=lambda x:-x["humanness"])
for o in out[:15]:
    print(o["id"],"hum",o["humanness"],"kd",o["kd_mean"])
json.dump(out,open("ppiflow50_props.json","w"),indent=1)
print("total",len(out),"| hum>=0.50:",sum(1 for o in out if o["humanness"]>=0.50))
