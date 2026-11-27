from pathlib import Path
from Bio import Align, SeqIO, __version__
from Bio.Align import substitution_matrices
import csv, json, hashlib, sys
base=Path(__file__).resolve().parent
parent_path=base.parents[6]/'inputs/parent.fasta'
if not parent_path.exists():
    parent_path=Path(sys.argv[1])
parent=str(SeqIO.read(parent_path,'fasta').seq)
assert len(parent)==269
ids=['A3FM73','P61872','A0A163J4P9','A0A167LKQ2']
aligner=Align.PairwiseAligner(mode='local')
aligner.substitution_matrix=substitution_matrices.load('BLOSUM62')
aligner.open_gap_score=-10
aligner.extend_gap_score=-0.5
mappings={}; metadata=[]
with (base/'pairwise_alignments.txt').open('w') as out:
    for ident in ids:
        seq=str(SeqIO.read(base/(ident+'.fasta'),'fasta').seq)
        alns=aligner.align(parent,seq); a=alns[0]
        blocks=a.aligned
        m={int(i):int(j) for (sa,ea),(sb,eb) in zip(*blocks) for i,j in zip(range(sa,ea),range(sb,eb))}
        matches=sum(parent[i]==seq[j] for i,j in m.items())
        motifs={str(i): {'parent': parent[i-1], 'homolog':seq[m[i-1]] if i-1 in m else '-', 'homolog_position':m[i-1]+1 if i-1 in m else None} for i in [82,144,145,203,257]}
        mappings[ident]=(seq,m)
        metadata.append({'id':ident,'length':len(seq),'score':a.score,'aligned_parent_positions':len(m),'parent_coverage':len(m)/len(parent),'identity_among_aligned':matches/len(m),'number_optimal_alignments':len(alns),'motif_checks':motifs})
        out.write(f'>{ident}\n{a}\n')
with (base/'parent_position_conservation.csv').open('w',newline='') as f:
    fields=['parent_position','parent_residue']+ids+['aligned_homolog_count','parent_identity_count','parent_identity_fraction_among_aligned']
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
    for i,aa in enumerate(parent):
        row={'parent_position':i+1,'parent_residue':aa}
        vals=[]
        for ident in ids:
            seq,m=mappings[ident]; v=seq[m[i]] if i in m else '-';row[ident]=v
            if v!='-':vals.append(v)
        row['aligned_homolog_count']=len(vals);row['parent_identity_count']=sum(v==aa for v in vals);row['parent_identity_fraction_among_aligned']=sum(v==aa for v in vals)/len(vals) if vals else ''
        w.writerow(row)
(base/'alignment_metadata.json').write_text(json.dumps({'method':'independent parent-anchored pairwise local alignments, not multiple-sequence alignment','provider':'local, explicitly user-approved','biopython':__version__,'matrix':'BLOSUM62','gap_open':-10,'gap_extend':-0.5,'selection':'published RML-family homologs, not comprehensive or phylogenetically independent','ambiguity':'first optimal alignment only; inspect alternative alignments and motif mapping; conservation is preliminary','alignments':metadata},indent=2)+'\n')
print(json.dumps(metadata,indent=2))
