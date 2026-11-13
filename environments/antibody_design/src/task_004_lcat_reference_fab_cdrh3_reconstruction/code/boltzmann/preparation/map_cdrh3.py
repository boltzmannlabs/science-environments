#!/usr/bin/env python3
"""Map IMGT CDR-H3 positions to PDB residue numbers for heavy chain C."""
from collections import OrderedDict

AA3to1 = {'ALA':'A','ARG':'R','ASN':'N','ASP':'D','CYS':'C','GLN':'Q','GLU':'E',
          'GLY':'G','HIS':'H','ILE':'I','LEU':'L','LYS':'K','MET':'M','PHE':'F',
          'PRO':'P','SER':'S','THR':'T','TRP':'W','TYR':'Y','VAL':'V'}

# Parse chain C with positions - get sequence in order
chain_c = OrderedDict()  # (resseq, icode) -> aa1
with open('5BV7.pdb') as f:
    for line in f:
        if line.startswith('ATOM'):
            resn = line[17:20].strip()
            if resn in ('HOH','WAT','EDO','GLC','NAG','BME','CLR','SUL','PO4','NA','CL'):
                continue
            cid = line[21]
            if cid != 'C':
                continue
            if resn not in AA3to1:
                continue
            resseq = int(line[22:26].strip())
            icode = line[26]
            key = (resseq, icode)
            if key not in chain_c:
                chain_c[key] = AA3to1[resn]

# Dataset VH sequence
vseq = "VQLVESGGGVVQPGRSLRLSCAASGFTFSSYGMHWVRQAPGKGLEWVAVIWYDGSNKFYEDSVKGRFTISRDNSKNTLYLQMDSLRAEDTAVYYCAREGAAVRSFYYSYYGMDVWGQGTTVTVSSA"
print("Dataset VH length:", len(vseq))
print("Chain C modeled:", len(chain_c))
pdb_keys = list(chain_c.keys())
pdb_aa = [chain_c[k] for k in pdb_keys]
print("Chain C seq (first 130):", ''.join(pdb_aa[:130]))

# Align VH to first 130 residues of chain C
def nw_align(a, b):
    n, m = len(a), len(b)
    score = [[0]*(m+1) for _ in range(n+1)]
    for i in range(n+1): score[i][0] = -1*i
    for j in range(m+1): score[0][j] = -1*j
    for i in range(1, n+1):
        for j in range(1, m+1):
            match = 2 if a[i-1]==b[j-1] else -1
            score[i][j] = max(score[i-1][j-1]+match, score[i-1][j]-1, score[i][j-1]-1)
    i, j = n, m
    pairs = []
    while i>0 and j>0:
        if a[i-1]==b[j-1] and score[i][j]==score[i-1][j-1]+2:
            pairs.append((i-1, j-1)); i-=1; j-=1
        elif score[i][j]==score[i-1][j]-1:
            pairs.append((i-1, None)); i-=1
        elif score[i][j]==score[i][j-1]-1:
            pairs.append((None, j-1)); j-=1
        else:
            pairs.append((i-1, j-1)); i-=1; j-=1
    return list(reversed(pairs))

pdb_aa_vh = pdb_aa[:130]
pairs = nw_align(vseq, pdb_aa_vh)
# mapping: dataset index (0-based) -> pdb key
mapping = {}
for vi, pi in pairs:
    if vi is not None and pi is not None:
        mapping[vi] = pdb_keys[pi]

# Verify alignment quality
n_match = sum(1 for vi, pi in pairs if vi is not None and pi is not None and vseq[vi]==pdb_aa_vh[pi])
n_aligned = sum(1 for vi, pi in pairs if vi is not None and pi is not None)
print(f"Alignment: {n_match}/{n_aligned} matched")

# CDR-H3: IMGT positions 95-113 (1-indexed)
print("\n=== CDR-H3 (IMGT 95-113) PDB mapping ===")
cdr_keys = []
for imgt_pos in range(95, 114):
    vi = imgt_pos - 1
    if vi in mapping:
        key = mapping[vi]
        cdr_keys.append(key)
        print(f"IMGT {imgt_pos}: {vseq[vi]} -> PDB C{key[0]}{key[1]}")
    else:
        print(f"IMGT {imgt_pos}: {vseq[vi]} -> NOT MODELED")

if cdr_keys:
    print("\nCDR-H3 PDB residue numbers:", [k[0] for k in cdr_keys])
    print("CDR-H3 PDB residue range:", min(k[0] for k in cdr_keys), "-", max(k[0] for k in cdr_keys))

# Verify with known landmarks: CDR-H1 (IMGT 24-31), CDR-H2 (IMGT 49-56)
print("\n=== Landmark verification ===")
for name, start, end in [('CDR-H1', 24, 31), ('CDR-H2', 49, 56), ('CDR-H3', 95, 113)]:
    seq = ''
    for imgt_pos in range(start, end+1):
        vi = imgt_pos - 1
        if vi in mapping:
            key = mapping[vi]
            seq += str(key[0]) + ':'
    print(f"{name} (IMGT {start}-{end}): PDB residues {seq}")
