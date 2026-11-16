#!/usr/bin/env python3
"""H5 reconstruction control (canonical): Boltz2 full-scFv prediction vs 35TL.

Sequence-anchored residue correspondence everywhere:
- PD-L1: predicted chain A residues indexed 0..113 mapped to experimental list.
- H5 VH/VL: experimental observed residues mapped into the full 120/107-aa
  construct positions (framework-completed termini, as submitted to Boltz2).

Metrics: PD-L1 self-fit CA RMSD, global complex CA RMSD (all observed residues,
single superposition), antigen-frame VH/VL placement error, per-CDR RMSD,
PD-L1 interface-residue recovery (labels = experimental antigen index).
"""
import json
import sys
from collections import OrderedDict

import numpy as np

sys.path.insert(0, '/home/boltzmann10/new_agent_scienece_env/science-environments/'
                   'environments/antibody_design/src/task_002_pdl1_epitope_targeted_scfv_design/'
                   'run1_epitope_abgen/code')
from prep_design_inputs import parse_protein, THREE2ONE, kabsch  # noqa: E402

SCRATCH = '/home/boltzmann10/.sci/cache/scratch/task002'
PRED_PDB = (f'{SCRATCH}/h5_control_v3_raw/boltz_outputs/boltz_results_1/'
            'predictions/1/1_model_0.pdb')
LINK = 'AGGGGSGGGGSGGGS'
FULL_VH = ('EVQLVESGGGLVQPGGSLRLSCAASSIDLEMYKIHWVRQAPGKGLEWVARINVGFDVTRYADSVKGR'
           'FTISADTSKNTAYLQMNSLRAEDTAVYYCWPYSIVMLPFHGYWGQGTLVTVSS')
FULL_VL = ('DIQMTQSPSSLSASVGDRVTITCRASQDVGKDVAWYQQKPGKAPKLLIYYYKFLYSGVPSRFSGSR'
           'SGTDFTLTISSLQPEDFATYYCLNANTGGITFGQGTKVEIK')
CDRS = {'H1': (26, 33), 'H2': (51, 58), 'H3': (97, 109),
        'L1': (24, 29), 'L2': (50, 55), 'L3': (89, 97)}


def subseq_map(observed, full):
    out, j = [], 0
    for c in observed:
        while j < len(full) and full[j] != c:
            j += 1
        assert j < len(full), 'alignment failed'
        out.append(j)
        j += 1
    return out


def main():
    exp = parse_protein(f'{SCRATCH}/35TL.pdb')
    pred = parse_protein(PRED_PDB)
    aa = lambda rs: ''.join(THREE2ONE[r['resn']] for r in rs)

    exp_ag = [(k[1], r) for k, r in exp.items() if k[0] == 'A']
    exp_vh = [(k[1], r) for k, r in exp.items() if k[0] == 'B']
    exp_vl = [(k[1], r) for k, r in exp.items() if k[0] == 'C']
    pred_a = [r for k, r in pred.items() if k[0] == 'A']
    pred_b = [r for k, r in pred.items() if k[0] == 'B']

    assert aa(pred_b) == FULL_VH + LINK + FULL_VL, 'prediction sequence mismatch'
    m_ag = subseq_map(aa([r for _, r in exp_ag]), aa(pred_a))
    m_vh = subseq_map(aa([r for _, r in exp_vh]), FULL_VH)
    m_vl = subseq_map(aa([r for _, r in exp_vl]), FULL_VL)

    ca = lambda r: np.array(r['atoms']['CA'])
    pv = lambda p1: pred_b[p1 - 1]                     # 1-based VH position
    pl = lambda p1: pred_b[120 + len(LINK) + p1 - 1]   # 1-based VL position

    # PD-L1 self-fit
    P = np.array([ca(pred_a[m_ag[i]]) for i in range(len(exp_ag))])
    Q = np.array([ca(r) for _, r in exp_ag])
    Rag, tag, rmsd_ag = kabsch(P, Q)
    print(f'PD-L1 CA RMSD self-aligned: {rmsd_ag:.3f} A ({len(P)} res)')

    # global fit
    P2 = list(P); Q2 = list(Q)
    for i, (_, r) in enumerate(exp_vh):
        P2.append(ca(pv(m_vh[i] + 1))); Q2.append(ca(r))
    for i, (_, r) in enumerate(exp_vl):
        P2.append(ca(pl(m_vl[i] + 1))); Q2.append(ca(r))
    P2, Q2 = np.array(P2), np.array(Q2)
    Rg, tg, rmsd_global = kabsch(P2, Q2)
    print(f'GLOBAL complex CA RMSD vs 35TL: {rmsd_global:.3f} A ({len(P2)} res)')

    # antigen-frame placement
    def place(mp, lst, getter, R, t):
        ds = [np.sum((R @ ca(getter(mp[i] + 1)) + t - ca(r)) ** 2) for i, (_, r) in enumerate(lst)]
        return float(np.sqrt(np.mean(ds)))
    err_vh = place(m_vh, exp_vh, pv, Rag, tag)
    err_vl = place(m_vl, exp_vl, pl, Rag, tag)
    print(f'antigen-frame placement: VH {err_vh:.3f} A, VL {err_vl:.3f} A')

    # per-CDR
    per_cdr = {}
    for name, (a, b) in CDRS.items():
        if name[0] == 'H':
            ds = [np.sum((Rg @ ca(pv(m_vh[i] + 1)) + tg - ca(r)) ** 2)
                  for i, (_, r) in enumerate(exp_vh) if a <= m_vh[i] + 1 <= b]
        else:
            ds = [np.sum((Rg @ ca(pl(m_vl[i] + 1)) + tg - ca(r)) ** 2)
                  for i, (_, r) in enumerate(exp_vl) if a <= m_vl[i] + 1 <= b]
        per_cdr[name] = dict(rmsd=round(float(np.sqrt(np.mean(ds))), 3), n=len(ds))
        print(f'  {name}: {per_cdr[name]["rmsd"]:.3f} A ({len(ds)} res)')

    # interface recovery keyed by experimental antigen index
    def interface(ant_list, ab_lists, cutoff=5.0):
        A = [(i, np.array(x)) for i, r in enumerate(ant_list)
             for n, x in r['atoms'].items() if not n.startswith('H')]
        B = [np.array(x) for lst in ab_lists for r in lst
             for n, x in r['atoms'].items() if not n.startswith('H')]
        out = set()
        for i, x in A:
            for y in B:
                if (x - y).dot(x - y) <= cutoff * cutoff:
                    out.add(i); break
        return out

    exp_int = interface([r for _, r in exp_ag],
                        [[r for _, r in exp_vh], [r for _, r in exp_vl]])
    pred_ag_t = [dict(atoms={n: Rg @ np.array(x) + tg for n, x in r['atoms'].items()
                             if not n.startswith('H')})
                 for r in pred_a]
    pred_ab_t = [dict(atoms={n: Rg @ np.array(x) + tg for n, x in r['atoms'].items()
                             if not n.startswith('H')})
                 for r in pred_b]
    pred_int = interface([pred_ag_t[m_ag[i]] for i in range(len(exp_ag))],
                         [pred_ab_t])
    rec = len(exp_int & pred_int) / len(exp_int)
    print(f'PD-L1 interface-residue recovery: {len(exp_int & pred_int)}/{len(exp_int)} '
          f'= {rec:.3f}')
    exp_res = [exp_ag[i][0] for i in sorted(exp_int)]
    print('  exp interface resSeq:', exp_res)

    record = dict(
        comparison=('Boltz2 prediction of full H5 scFv (120-aa VH + 15-aa G4S linker '
                    '+ 107-aa VL; framework-completed termini) in complex with PD-L1 '
                    'vs experimental 35TL cryo-EM; sequence-anchored correspondence'),
        pdl1_ca_rmsd_selfaligned=round(rmsd_ag, 3),
        global_complex_ca_rmsd=round(rmsd_global, 3),
        antigen_frame_placement=dict(VH=round(err_vh, 3), VL=round(err_vl, 3)),
        per_cdr=per_cdr,
        interface_recovery=dict(n_experimental=len(exp_int), n_predicted=len(pred_int),
                                recovered=len(exp_int & pred_int),
                                fraction=round(rec, 3),
                                experimental_interface_resSeq=exp_res),
        confidence=dict(iptm=0.9265, protein_iptm=0.9265, complex_plddt=0.9208,
                        complex_iplddt=0.9044),
        published_benchmark=dict(
            metric='H5 AF3-predicted vs cryo-EM global CA RMSD (Germinal Fig. 4A)',
            value_A=1.25))
    out = f'{SCRATCH}/h5_control_v3_analysis.json'
    json.dump(record, open(out, 'w'), indent=2)
    print('wrote', out)


if __name__ == '__main__':
    main()
