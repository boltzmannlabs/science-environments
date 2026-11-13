"""Strict fixed-backbone sequence projections. No scientific imports or calculations."""
import hashlib, math
AA3=dict(zip('ARNDCQEGHILKMFPSTWYV',['ALA','ARG','ASN','ASP','CYS','GLN','GLU','GLY','HIS','ILE','LEU','LYS','MET','PHE','PRO','SER','THR','TRP','TYR','VAL']))
AA1={v:k for k,v in AA3.items()}
BB=('N','CA','C','O')

def validate_entropy_rows(rows, sequence):
    if len(rows)!=len(sequence) or sorted(r['position'] for r in rows)!=list(range(1,len(sequence)+1)):
        raise ValueError('incomplete or duplicated native residue coverage')
    for r in rows:
        if r['aa']!=sequence[r['position']-1] or not math.isfinite(r['entropy']) or not math.isfinite(r['packing_fraction']) or not 0<r['packing_fraction']<=1:
            raise ValueError('invalid native entropy/identity/packing fraction')
    return math.fsum(r['entropy'] for r in rows)


def backbone_view(text, expected_parent, target, sequence_sha):
    if hashlib.sha256(target.encode('ascii')).hexdigest()!=sequence_sha:
        raise ValueError('sequence SHA mismatch')
    if len(target)!=len(expected_parent) or any(a not in AA3 for a in target):
        raise ValueError('invalid target sequence')
    atoms={}; names={}; removed=0; output=[]
    for line in text.splitlines():
        if not line.startswith(('ATOM  ','HETATM')): continue
        if line[:6]!='ATOM  ' or line[21]!='A' or line[26]!=' ' or line[16] not in (' ','A'):
            raise ValueError('noncanonical source chain/record/insertion/alternate conformer')
        i=int(line[22:26]); name=line[12:16].strip()
        if not 1<=i<=len(target): raise ValueError('residue out of range')
        if AA1.get(line[17:20])!=expected_parent[i-1]: raise ValueError('source sequence mismatch')
        if name not in BB: removed+=1; continue
        key=(i,name)
        if key in atoms: raise ValueError('duplicate backbone atom')
        xyz=tuple(float(line[j:j+8]) for j in (30,38,46))
        if not all(math.isfinite(x) for x in xyz): raise ValueError('nonfinite source')
        atoms[key]=xyz; names.setdefault(i,set()).add(name)
        output.append(line[:17]+AA3[target[i-1]]+line[20:])
    if len(names)!=len(target) or any(names.get(i)!=set(BB) for i in range(1,len(target)+1)):
        raise ValueError('incomplete backbone')
    return '\n'.join(output)+'\nTER\nEND\n',{'residues':len(names),'backbone_atoms':len(atoms),'removed_atoms':removed,'backbone_xyz':{f'{i}:{n}':v for (i,n),v in atoms.items()}}
