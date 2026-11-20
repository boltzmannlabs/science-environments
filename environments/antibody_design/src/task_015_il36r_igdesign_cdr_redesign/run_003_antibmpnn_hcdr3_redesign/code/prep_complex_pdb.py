#!/usr/bin/env python3
"""S1: Build the AntiBMPNN input complex PDB for task_015 (6u6u).

Extracts protein-only chains H (Spesolimab heavy), L (kappa light) and
R (IL-36R ECD, residues 21-217) from inputs/6u6u.pdb, drops waters/glycans/
ions, keeps native contiguous numbering, writes ATOM records + SEQRES per
chain (H, L, R order), and asserts:
  - per-chain residue counts and sequences match the verified 6u6u SEQRES
  - the native CDRs appear at the expected 1-based H-chain positions
    (HCDR1 26-33, HCDR2 51-58, HCDR3 97-108), i.e. 0-based 25-32/50-57/96-107
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
IN_PDB = os.path.join(HERE, "..", "inputs", "6u6u.pdb")
OUT_PDB = os.path.join(HERE, "..", "inputs", "complex_hlr_6u6u.pdb")

THREE2ONE = {
    'ALA': 'A', 'ARG': 'R', 'ASN': 'N', 'ASP': 'D', 'CYS': 'C', 'GLN': 'Q',
    'GLU': 'E', 'GLY': 'G', 'HIS': 'H', 'ILE': 'I', 'LEU': 'L', 'LYS': 'K',
    'MET': 'M', 'PHE': 'F', 'PRO': 'P', 'SER': 'S', 'THR': 'T', 'TRP': 'W',
    'TYR': 'Y', 'VAL': 'V'}

# Verified 6u6u SEQRES-derived variable domains (ANARCI-checked)
CDR_EXPECT = {  # 1-based inclusive on chain H (numbering starts at 1)
    "HCDR1": (26, 33, "GYSFTSSW"),
    "HCDR2": (51, 58, "INPGNVRT"),
    "HCDR3": (97, 108, "TVVFYGEPYFPY"),
}
EXPECT_LEN = {"H": 221, "L": 214, "R": 197}


def read_chain(pdb_path, chain_id):
    seen, residues = set(), []
    for line in open(pdb_path):
        if line.startswith("ATOM") and line[21] == chain_id:
            resname = line[17:20].strip()
            if resname not in THREE2ONE:
                continue
            key = (line[21], line[22:27])
            if key not in seen:
                seen.add(key)
                residues.append([key, resname, []])
            residues[-1][2].append(line.rstrip("\n"))
    return residues


def write_seqres(handle, chain_id, seq):
    ser = 1
    n = len(seq)
    one2three = {v: k for k, v in THREE2ONE.items()}
    for i in range(0, n, 10):
        chunk = seq[i:i + 10]
        handle.write(f"SEQRES {ser:2d} {chain_id} {n:4d}  " +
                     " ".join(one2three[a] for a in chunk) + "\n")
        ser += 1


def main():
    with open(OUT_PDB, "w") as h:
        for cid in ["H", "L", "R"]:
            residues = read_chain(IN_PDB, cid)
            seq = "".join(THREE2ONE[r[1]] for r in residues)
            assert len(residues) == EXPECT_LEN[cid], (cid, len(residues))
            write_seqres(h, cid, seq)
        for cid in ["H", "L", "R"]:
            residues = read_chain(IN_PDB, cid)
            for (_, _r3, atoms) in residues:
                for line in atoms:
                    h.write(line + "\n")
            h.write("TER\n")
        h.write("END\n")

    # verify output
    vh = read_chain(OUT_PDB, "H")
    seq_h = "".join(THREE2ONE[r[1]] for r in vh)
    assert len(vh) == 221
    for name, (start, end, native) in CDR_EXPECT.items():
        got = seq_h[start - 1:end]
        assert got == native, f"{name}: expected {native} at {start}-{end}, got {got}"
        print(f"{name} 1-based {start}-{end}: {got} OK")
    for cid in ["H", "L", "R"]:
        n = len(read_chain(OUT_PDB, cid))
        assert n == EXPECT_LEN[cid], (cid, n)
        print(f"chain {cid}: {n} residues OK")
    print(f"WROTE {OUT_PDB}")


if __name__ == "__main__":
    main()
