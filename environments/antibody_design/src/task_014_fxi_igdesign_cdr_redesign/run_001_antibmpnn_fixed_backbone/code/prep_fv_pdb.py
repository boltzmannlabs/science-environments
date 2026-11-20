#!/usr/bin/env python3
"""S1: Build the AntiBMPNN input Fv PDB from the verified 6HHC remap.

Extracts the Osocimab variable domains (VH 120 aa, VL 107/109 aa) from
inputs/6hhc_remap.pdb (A=VL, B=VH, C=FXIa), renumbers each chain per residue
1..N (chain A=VH, chain B=VL in the output), writes SEQRES + TER + END
(ATOM records only), and asserts:
  - per-chain unique-residue counts equal the expected variable-domain lengths
  - the native CDRs appear at the expected 1-based positions on chain A
    (HCDR1 26-33, HCDR2 51-58, HCDR3 97-109)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
IN_PDB = os.path.join(HERE, "..", "inputs", "6hhc_remap.pdb")
OUT_PDB = os.path.join(HERE, "..", "inputs", "fv_osocimab.pdb")

VH = ("EVQLLESGGGLVQPGGSLRLSCAASGFTFSQYGMDWVRQAPGKGLEWVSGIGPSGGSTVYADSVKGRFT"
      "ISRDNSKNTLYLQMNSLRAEDTAVYYCTRGGPYYYYGMDVWGQGTTVTVSS")
VL_FULL = ("DIQMTQSPSSLSASVGDRVTITCQASQDISNYLNWYQQKPGKAPKLLIYDASNLETGVPSRFSGS"
           "GSGTDFTFTISSLQPEDIATYYCQQANSFPVTFGGGTKVEIKRTVAAPSVFIFPP")
THREE2ONE = {
    'ALA': 'A', 'ARG': 'R', 'ASN': 'N', 'ASP': 'D', 'CYS': 'C', 'GLN': 'Q',
    'GLU': 'E', 'GLY': 'G', 'HIS': 'H', 'ILE': 'I', 'LEU': 'L', 'LYS': 'K',
    'MET': 'M', 'PHE': 'F', 'PRO': 'P', 'SER': 'S', 'THR': 'T', 'TRP': 'W',
    'TYR': 'Y', 'VAL': 'V'}

CDR_EXPECT = {  # 1-based inclusive on the output chain A (VH)
    "HCDR1": (26, 33, "GFTFSQYG"),
    "HCDR2": (51, 58, "IGPSGGST"),
    "HCDR3": (97, 109, "TRGGPYYYYGMDV"),
}


def read_chain(pdb_path, chain_id):
    """Ordered [(reskey, resname3, [atom lines])] for standard residues."""
    seen, residues = set(), []
    for line in open(pdb_path):
        if line.startswith("ATOM") and line[21] == chain_id:
            resname = line[17:20].strip()
            if resname not in THREE2ONE:
                continue
            key = (line[21], line[22:27])  # chain + resSeq+icode
            if key not in seen:
                seen.add(key)
                residues.append([key, resname, []])
            residues[-1][2].append(line)
    return residues


def var_domain_prefix(residues, full_seq, stop_marker):
    """Take the N-terminal variable-domain prefix ending at stop_marker."""
    seq = "".join(THREE2ONE[r[1]] for r in residues)
    end = full_seq.find(stop_marker) + len(stop_marker)
    prefix = full_seq[:end]
    assert seq.startswith(prefix), (
        f"chain mismatch: PDB starts {seq[:40]} vs expected {prefix[:40]}")
    n = len(prefix)
    assert n <= len(residues)
    return residues[:n], prefix


def write_chain_pdb(handle, residues, chain_id, serial_start):
    serial = serial_start
    resseq = 0
    last = atoms_line_of(residues[-1])
    for (_, _r3, atoms) in residues:
        resseq += 1
        for line in atoms:
            serial += 1
            new = (f"ATOM  {serial:5d} {line[12:16]}{line[16]}{line[17:20]} "
                   f"{chain_id}{resseq:4d}{line[26:80]}")
            handle.write(new.rstrip() + "\n")
    # TER
    serial += 1
    handle.write(f"TER   {serial:5d}      {last[17:20]} {chain_id}{resseq:4d}\n")
    return serial


def atoms_line_of(residue):
    return residue[2][0]


def write_seqres(handle, chain_id, seq, ser_start):
    ser = ser_start
    n = len(seq)
    for i in range(0, n, 10):
        chunk = seq[i:i + 10]
        resnames = " ".join(
            next(k for k, v in THREE2ONE.items() if v == a) for a in chunk)
        handle.write(f"SEQRES {ser:2d} {chain_id} {n:4d}  {resnames}\n")
        ser += 1
    return ser


def main():
    vh_res, vh_seq = var_domain_prefix(read_chain(IN_PDB, "B"), VH, "WGQGTTVTVSS")
    vl_res, vl_seq = var_domain_prefix(read_chain(IN_PDB, "A"), VL_FULL, "FGGGTKVEIK")
    print(f"VH variable domain: {len(vh_res)} residues")
    print(f"VL variable domain: {len(vl_res)} residues")

    # CDR placement assertions on the renumbered chain A (1-based)
    for name, (start, end, native) in CDR_EXPECT.items():
        got = vh_seq[start - 1:end]
        assert got == native, f"{name}: expected {native} at {start}-{end}, got {got}"
        print(f"{name} 1-based {start}-{end}: {got} OK")

    os.makedirs(os.path.dirname(OUT_PDB), exist_ok=True)
    with open(OUT_PDB, "w") as h:
        ser = 1
        ser = write_seqres(h, "A", vh_seq, 1)
        _ = ser
        write_seqres(h, "B", vl_seq, 1)
        s = write_chain_pdb(h, vh_res, "A", 0)
        s = write_chain_pdb(h, vl_res, "B", s)
        h.write("END\n")

    # re-open and assert unique-residue counts and CDR content
    got_vh, got_vl = read_chain(OUT_PDB, "A"), read_chain(OUT_PDB, "B")
    assert len(got_vh) == len(vh_seq) == 120, (len(got_vh), len(vh_seq))
    assert len(got_vl) == len(vl_seq), (len(got_vl), len(vl_seq))
    seq_a = "".join(THREE2ONE[r[1]] for r in got_vh)
    assert seq_a == vh_seq
    for name, (start, end, native) in CDR_EXPECT.items():
        assert seq_a[start - 1:end] == native, name
    print(f"WROTE {OUT_PDB}: chain A=VH {len(got_vh)} res, chain B=VL {len(got_vl)} res, "
          f"assertions passed (lengths, sequences, CDR positions)")


if __name__ == "__main__":
    main()
