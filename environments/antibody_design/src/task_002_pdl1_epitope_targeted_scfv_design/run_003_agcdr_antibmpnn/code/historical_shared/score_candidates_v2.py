#!/usr/bin/env python3
"""Score v2 Boltz2 prospective predictions of AntiBMPNN candidates (exact
CSV-derived sequences). Interface/epitope metrics vs H5 control, same protocol."""
import json
import sys

import numpy as np

sys.path.insert(0, '/home/boltzmann10/new_agent_scienece_env/science-environments/'
                   'environments/antibody_design/src/task_002_pdl1_epitope_targeted_scfv_design/'
                   'run1_epitope_abgen/code')
from prep_design_inputs import parse_protein, THREE2ONE  # noqa: E402

SCRATCH = '/home/boltzmann10/.sci/cache/scratch/task002'
HOTSPOTS = [37, 39, 41, 96, 98]
EPI = sorted({35, 36, 37, 38, 39, 40, 41, 42, 43, 45, 46, 47, 48, 49, 50, 51, 52,
              94, 95, 96, 97, 98, 99, 100, 105, 106, 107, 108})
VH_N, LINK_N = 120, 15


def interface(ant_list, ab_list, cutoff=5.0):
    A = [(i, np.array(x)) for i, r in enumerate(ant_list)
         for n, x in r['atoms'].items() if not n.startswith('H')]
    B = [np.array(x) for r in ab_list for n, x in r['atoms'].items() if not n.startswith('H')]
    out = set()
    for i, x in A:
        for y in B:
            if (x - y).dot(x - y) <= cutoff * cutoff:
                out.add(i)
                break
    return out


def main():
    ctrl = json.load(open(f'{SCRATCH}/h5_control_v3_analysis.json'))
    exp = parse_protein(f'{SCRATCH}/35TL.pdb')
    exp_ag = [r for k, r in exp.items() if k[0] == 'A']
    exp_ab = [r for k, r in exp.items() if k[0] in 'BC']
    h5_res = set(ctrl['interface_recovery']['experimental_interface_resSeq'])

    cands = json.load(open(f'{SCRATCH}/eval_candidates.json'))
    seqs = {f"cand{c['idx']}": c['scfv'] for c in cands}
    seqs['recomb_23'] = (seqs['cand2'][:135] + seqs['cand3'][135:])  # cand2 H3 + cand3 L3

    results = []
    for tag in ['cand0', 'cand1', 'cand2', 'cand3', 'recomb_23']:
        d = (f'{SCRATCH}/eval_{tag}_v2_raw/full/boltz_outputs/'
             f'boltz_results_1/predictions/1')
        conf = json.load(open(f'{d}/confidence_1_model_0.json'))
        pred = parse_protein(f'{d}/1_model_0.pdb')
        ag = [r for k, r in pred.items() if k[0] == 'A']
        scfv = [r for k, r in pred.items() if k[0] == 'B']
        seq = ''.join(THREE2ONE[r['resn']] for r in scfv)
        assert seq == seqs[tag], f'{tag} echo mismatch'
        iface = interface(ag, scfv)
        iface_study = {i + 1 for i in iface}   # prediction chain A numbered 1..114 = study numbering
        epi_hit = sorted(iface_study & set(EPI))
        hs_hit = sorted(iface_study & set(HOTSPOTS))
        h5_hit = sorted(iface_study & h5_res)
        # CDR3 contact involvement
        h3 = scfv[96:109]  # local 97-109
        cdr_atoms = [np.array(x) for r in scfv[96:109] + scfv[VH_N + LINK_N + 88: VH_N + LINK_N + 97]
                     for n, x in r['atoms'].items() if not n.startswith('H')]
        ag_atoms = [np.array(x) for r in ag for n, x in r['atoms'].items() if not n.startswith('H')]
        h3_contact = any((x - y).dot(x - y) <= 25.0 for x in cdr_atoms for y in ag_atoms)
        rec = dict(
            tag=tag,
            iptm=round(conf['iptm'], 4),
            complex_plddt=round(conf['complex_plddt'], 4),
            n_interface=len(iface),
            epitope_coverage=round(len(epi_hit) / len(EPI), 3),
            n_epitope_hits=len(epi_hit),
            hotspots_hit=hs_hit,
            h5_interface_recovery=round(len(h5_hit) / len(h5_res), 3),
            cdr3_contacts_antigen=h3_contact)
        results.append(rec)
        print(f"{tag}: ipTM {rec['iptm']}, pLDDT {rec['complex_plddt']}, "
              f"epitope cov {rec['epitope_coverage']} ({rec['n_epitope_hits']}/{len(EPI)}), "
              f"hotspots {hs_hit}, H5-iface rec {rec['h5_interface_recovery']}, "
              f"CDR3-contact {h3_contact}")

    print(f"\nH5 control: ipTM {ctrl['confidence']['iptm']}, "
          f"iface recovery {ctrl['interface_recovery']['fraction']}, "
          f"global RMSD {ctrl['global_complex_ca_rmsd']} A")
    json.dump(dict(h5_control_summary=dict(
                    iptm=ctrl['confidence']['iptm'],
                    interface_recovery=ctrl['interface_recovery']['fraction'],
                    global_rmsd_A=ctrl['global_complex_ca_rmsd']),
                  candidates=results),
              open(f'{SCRATCH}/candidate_eval_scores_v2.json', 'w'), indent=1)
    print('wrote candidate_eval_scores_v2.json')


if __name__ == '__main__':
    main()
