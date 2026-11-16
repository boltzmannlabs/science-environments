#!/usr/bin/env python3
"""Place the study starting scFv framework at the PD-L1 epitope via a paired-Fab
pose donor (5X8M durvalumab Fab:PD-L1), fully independent of H5 (35TL).

Steps
-----
1. Superpose 5X8M PD-L1 chain A onto the study target construct
   (Germinal repo pdbs/pdl1.pdb chain A; study numbering 1-115, hotspots 37/39/41/96/98).
   Mapping: study i  <->  5X8M i+17 (both mature PD-L1 numbering).
2. Apply the transform to 5X8M VH (chain B) and VL (chain C) -> donor pose in the
   study antigen frame.
3. Superpose the study scFv (split: VH chain H 1-120, VL chain L 136-242) onto the
   donor VH/VL framework CA atoms (framework positions only), single rigid transform,
   iterative outlier rejection.
4. Verify: framework RMSD, min heavy-atom distance and clash count vs study antigen
   (all atoms and framework-only), VH/VL internal geometry preserved.
5. Write antibody_framework_placed.pdb (H, L), antigen_pdl1_Vdomain.pdb (A),
   placed_complex_framework.pdb (A + H + L).
"""
import hashlib
import json
import os
import shutil
import subprocess
from collections import OrderedDict

import numpy as np
from scipy.spatial import cKDTree

THREE2ONE = {
    'ALA': 'A', 'ARG': 'R', 'ASN': 'N', 'ASP': 'D', 'CYS': 'C', 'GLN': 'Q',
    'GLU': 'E', 'GLY': 'G', 'HIS': 'H', 'ILE': 'I', 'LEU': 'L', 'LYS': 'K',
    'MET': 'M', 'PHE': 'F', 'PRO': 'P', 'SER': 'S', 'THR': 'T', 'TRP': 'W',
    'TYR': 'Y', 'VAL': 'V', 'MSE': 'M',
}

SCRATCH = '/home/boltzmann10/.sci/cache/scratch/task002'
REPO = f'{SCRATCH}/germinal_repo'
RUN = ('/home/boltzmann10/new_agent_scienece_env/science-environments/environments/'
       'antibody_design/src/task_002_pdl1_epitope_targeted_scfv_design/run1_epitope_abgen')
INPUTS = f'{RUN}/inputs'


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()


def parse_protein(path, chain=None):
    residues = OrderedDict()
    with open(path) as f:
        for line in f:
            if not line.startswith('ATOM  '):
                continue
            resn = line[17:20].strip()
            if resn not in THREE2ONE:
                continue
            ch = line[21]
            if chain is not None and ch != chain:
                continue
            try:
                resseq = int(line[22:26])
            except ValueError:
                continue
            icode = line[26].strip()
            altloc = line[16]
            if altloc not in (' ', 'A'):
                continue
            atom = line[12:16].strip()
            key = (ch, resseq, icode)
            r = residues.setdefault(key, dict(chain=ch, resseq=resseq, icode=icode,
                                              resn=resn, atoms=OrderedDict()))
            r['atoms'][atom] = (float(line[30:38]), float(line[38:46]), float(line[46:54]))
    return residues


def kabsch(P, Q):
    Pc, Qc = P.mean(0), Q.mean(0)
    p, q = P - Pc, Q - Qc
    H = p.T @ q
    U, S, Vt = np.linalg.svd(H)
    d = np.sign(np.linalg.det(Vt.T @ U.T))
    R = Vt.T @ np.diag([1.0, 1.0, d]) @ U.T
    rmsd = float(np.sqrt((((p @ R.T) - q) ** 2).sum(1).mean()))
    return R, Qc - Pc @ R.T, rmsd


def robust_kabsch(P, Q, cutoff=2.0, min_keep=30):
    used = list(range(len(P)))
    R = t = None
    rmsd = float('nan')
    for _ in range(6):
        R, t, rmsd = kabsch(P[used], Q[used])
        dev = np.sqrt((((P[used] @ R.T + t) - Q[used]) ** 2).sum(1))
        keep = [i for j, i in enumerate(used) if dev[j] <= cutoff]
        if len(keep) < min_keep or len(keep) == len(used):
            used = keep if len(keep) >= min_keep else used
            break
        used = keep
    R, t, rmsd = kabsch(P[used], Q[used])
    return R, t, rmsd, used


def main():
    os.makedirs(INPUTS, exist_ok=True)
    records = {}

    # ---- 0. copy + hash inputs ----
    copies = {
        'study_framework_scfv.pdb': f'{REPO}/pdbs/scfv.pdb',
        'study_target_pdl1_seedcomplex.pdb': f'{REPO}/pdbs/pdl1.pdb',
        'pose_donor_5X8M_durvalumab.pdb': f'{SCRATCH}/5X8M.pdb',
        'eval_35TL_experimental.pdb': f'{SCRATCH}/35TL.pdb',
    }
    for name, src in copies.items():
        dst = f'{INPUTS}/{name}'
        if not os.path.exists(dst):
            shutil.copy(src, dst)
        records[name] = dict(source=src, sha256=sha256(dst))
    records['germinal_repo_commit'] = subprocess.run(
        ['git', 'rev-parse', 'HEAD'], cwd=REPO, capture_output=True, text=True).stdout.strip()

    # ---- 1. antigen-antigen superposition: 5X8M A -> study A ----
    study_ag = parse_protein(f'{INPUTS}/study_target_pdl1_seedcomplex.pdb', 'A')
    donor = parse_protein(f'{INPUTS}/pose_donor_5X8M_durvalumab.pdb')
    donor_ag = {k: v for k, v in donor.items() if k[0] == 'A'}
    study_by_seq = OrderedDict()
    for k, r in study_ag.items():
        study_by_seq[r['resseq']] = r
    P, Q = [], []
    for k, r in donor_ag.items():
        num_study = r['resseq'] - 17
        if num_study in study_by_seq and 'CA' in r['atoms'] and 'CA' in study_by_seq[num_study]['atoms']:
            P.append(r['atoms']['CA'])
            Q.append(study_by_seq[num_study]['atoms']['CA'])
    P, Q = np.array(P), np.array(Q)
    R1, t1, rmsd1 = kabsch(P, Q)
    print(f'step1 antigen-antigen: {len(P)} CA pairs, RMSD {rmsd1:.3f} A')

    def to_study_frame(xyz):
        return np.array(xyz) @ R1.T + t1

    # donor VH/VL in study frame
    vh_don = {k: r for k, r in donor.items() if k[0] == 'B' and r['resseq'] <= 120}
    vl_don = {k: r for k, r in donor.items() if k[0] == 'C' and r['resseq'] <= 107}

    # ---- 2. split study scFv ----
    scfv = parse_protein(f'{INPUTS}/study_framework_scfv.pdb', 'A')
    seq = ''.join(THREE2ONE[r['resn']] for r in scfv.values())
    link = 'AGGGGSGGGGSGGGS'
    li = seq.find(link)
    vh_end = li
    vl_start = li + len(link) + 1
    vh_res = list(scfv.values())[:vh_end]
    vl_res = list(scfv.values())[vl_start - 1:]
    print(f'scFv: VH {len(vh_res)} aa, linker {len(link)}, VL {len(vl_res)} aa')

    # declared CDR boundaries (study lengths H1/H2/H3 = 8/8/13, L1/L2/L3 = 6/6/9)
    vh_seq, vl_seq = seq[:li], seq[vl_start - 1:]
    hcdr = {'H1': (26, 33), 'H2': (51, 58), 'H3': (97, 109)}
    def find(pat):
        return vl_seq.find(pat)
    l1s = find('RASQDVNTAVA'); l2s = find('SASFLY'); l3s = find('QQHYTTPPT')
    lcdr = {'L1': (l1s + 1, l1s + 6), 'L2': (l2s + 1, l2s + 6), 'L3': (l3s + 1, l3s + 9)}
    vh_cdr_pos = set()
    for a, b in hcdr.values():
        vh_cdr_pos.update(range(a, b + 1))
    vl_cdr_pos = set()
    for a, b in lcdr.values():
        vl_cdr_pos.update(range(a, b + 1))
    print('declared CDRs:',
          {k: vh_seq[a - 1:b] for k, (a, b) in hcdr.items()},
          {k: vl_seq[a - 1:b] for k, (a, b) in lcdr.items()})

    # ---- 3. scFv -> donor pose superposition (framework CA only) ----
    vh_by_num = {r['resseq']: r for r in vh_res}
    vl_by_num = {r['resseq']: r for r in vl_res}
    P2, Q2 = [], []
    vh_don_nums = {r['resseq'] for k, r in donor.items() if k[0] == 'B'}
    vl_don_nums = {r['resseq'] for k, r in donor.items() if k[0] == 'C'}
    for r in sorted(vh_don.values(), key=lambda r: r['resseq']):
        num = r['resseq']
        if num in vh_by_num and num not in vh_cdr_pos:
            if 'CA' in r['atoms'] and 'CA' in vh_by_num[num]['atoms']:
                P2.append(vh_by_num[num]['atoms']['CA'])
                Q2.append(to_study_frame(r['atoms']['CA']))
    for r in sorted(vl_don.values(), key=lambda r: r['resseq']):
        num = r['resseq']
        if num in vl_by_num and num not in vl_cdr_pos:
            if 'CA' in r['atoms'] and 'CA' in vl_by_num[num]['atoms']:
                P2.append(vl_by_num[num]['atoms']['CA'])
                Q2.append(to_study_frame(r['atoms']['CA']))
    P2, Q2 = np.array(P2), np.array(Q2)
    R2, t2, rmsd2, used2 = robust_kabsch(P2, Q2, cutoff=2.5)
    print(f'step2 scFv->donor pose: {len(used2)}/{len(P2)} framework CA pairs, RMSD {rmsd2:.3f} A')

    def xf(xyz):
        return np.array(xyz) @ R2.T + t2

    # ---- 4. verification ----
    ag_atoms = np.array([a for r in study_ag.values() for an, a in r['atoms'].items()
                         if not an.startswith('H')])
    fw_atoms = []
    cdr_atoms = []
    for r in vh_res:
        tgt = cdr_atoms if r['resseq'] in vh_cdr_pos else fw_atoms
        for an, a in r['atoms'].items():
            if not an.startswith('H'):
                tgt.append(xf(a))
    for r in vl_res:
        tgt = cdr_atoms if r['resseq'] in vl_cdr_pos else fw_atoms
        for an, a in r['atoms'].items():
            if not an.startswith('H'):
                tgt.append(xf(a))
    fw_atoms, cdr_atoms = np.array(fw_atoms), np.array(cdr_atoms)
    tree = cKDTree(ag_atoms)
    d_all, _ = tree.query(np.vstack([fw_atoms, cdr_atoms]))
    n_fw = len(fw_atoms)
    d_fw = d_all[:n_fw]
    d_cdr = d_all[n_fw:]
    print(f'framework vs antigen: min {d_fw.min():.2f} A, atoms<2.4A: {(d_fw < 2.4).sum()}, '
          f'atoms<3.0A: {(d_fw < 3.0).sum()}')
    print(f'(old) CDR region vs antigen: min {d_cdr.min():.2f} A '
          f'(resampled by design; reference only)')

    # hotspots adjacency
    hotspots = [37, 39, 41, 96, 98]
    tree_ab = cKDTree(np.vstack([fw_atoms, cdr_atoms]))
    for h in hotspots:
        r = study_by_seq[h]
        dist, _ = tree_ab.query(r['atoms']['CA'])
        print(f'hotspot A:{h} {THREE2ONE[r["resn"]]} CA -> nearest scFv atom: {dist:5.2f} A')

    if d_fw.min() < 2.2:
        print('WARNING: framework clash below 2.2 A')

    # ---- 5. write ----
    def write_pdb(path, res_lists, transform_chains):
        serial = 1
        with open(path, 'w') as f:
            for chain, res_list in res_lists:
                for r in res_list:
                    for aname, xyz in r['atoms'].items():
                        if aname.startswith('H'):
                            continue
                        p = xf(xyz) if chain in transform_chains else np.array(xyz)
                        f.write(f'ATOM  {serial:5d} {aname:>4s} {r["resn"]:3s} {chain:1s}'
                                f'{r["resseq"]:4d}{r["icode"]:1s}   '
                                f'{p[0]:8.3f}{p[1]:8.3f}{p[2]:8.3f}  1.00  0.00          {aname[0]:>2s}  \n')
                        serial += 1
            f.write('TER\nEND\n')

    write_pdb(f'{INPUTS}/antibody_framework_placed.pdb',
              [('H', vh_res), ('L', vl_res)], ('H', 'L'))
    write_pdb(f'{INPUTS}/antigen_pdl1_Vdomain.pdb', [('A', list(study_ag.values()))], ())
    write_pdb(f'{INPUTS}/placed_complex_framework.pdb',
              [('A', list(study_ag.values())), ('H', vh_res), ('L', vl_res)], ('H', 'L'))

    records.update({
        'scfv_layout': dict(total=len(seq), vh_len=len(vh_res), linker=link,
                            vl_len=len(vl_res), orientation='VH-first'),
        'declared_cdr_boundaries': {
            'H': {k: list(v) for k, v in hcdr.items()},
            'L': {k: list(v) for k, v in lcdr.items()},
            'numbering': 'chain-local 1-based (VH 1-120; VL 1-107 after linker removal)'},
        'pose_donor': dict(pdb='5X8M', antibody='durvalumab Fab',
                           vh_chain='B', vl_chain='C', antigen_chain='A',
                           antigen_ca_pairs=len(P), antigen_rmsd=round(rmsd1, 3),
                           framework_ca_pairs=len(used2), framework_rmsd=round(rmsd2, 3),
                           h5_coordinates_used=False),
        'placement_checks': dict(
            framework_min_heavy_dist=round(float(d_fw.min()), 2),
            framework_atoms_lt_2p4A=int((d_fw < 2.4).sum()),
            framework_atoms_lt_3p0A=int((d_fw < 3.0).sum())),
    })
    with open(f'{INPUTS}/prep_record.json', 'w') as f:
        json.dump(records, f, indent=2)
    print('wrote prep_record.json + 3 placed PDBs')


if __name__ == '__main__':
    main()
