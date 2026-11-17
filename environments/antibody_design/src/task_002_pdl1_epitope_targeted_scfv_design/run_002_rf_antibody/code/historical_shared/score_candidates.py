#!/usr/bin/env python3
"""Score the 4 AntiBMPNN candidates' Boltz2 prospective predictions.
Metrics: ipTM, complex pLDDT, PD-L1 interface recovery (against the H5
experimental interface and the declared 28-residue epitope), CDR contact
placement. All compared to the H5 control run in the same protocol."""
import json
import sys
from collections import OrderedDict

import numpy as np

sys.path.insert(0, '/home/boltzmann10/new_agent_scienece_env/science-environments/'
                   'environments/antibody_design/src/task_002_pdl1_epitope_targeted_scfv_design/'
                   'run1_epitope_abgen/code')
from prep_design_inputs import parse_protein, THREE2ONE  # noqa: E402

SCRATCH = '/home/boltzmann10/.sci/cache/scratch/task002'
AG_LEN = 114  # PD-L1 chain A in predictions
HOTSPOTS = [37, 39, 41, 96, 98]
EPI = sorted({35,36,37,38,39,40,41,42,43,45,46,47,48,49,50,51,52,94,95,96,97,98,99,100,105,106,107,108})
VH_N, LINK_N, VL_N = 120, 15, 107


def chain_seq(res_dict):
    return ''.join(THREE2ONE[r['resn']] for _, r in sorted(res_dict.items()))


def interface(ant_list, ab_list, cutoff=5.0):
    """ antigen residue indices (0-based within antigen) contacting antibody """
    A = [(i, np.array(x)) for i, r in enumerate(ant_list)
         for n, x in r['atoms'].items() if not n.startswith('H')]
    B = [np.array(x) for r in ab_list for n, x in r['atoms'].items() if not n.startswith('H')]
    out = set()
    for i, x in A:
        for y in B:
            if (x - y).dot(x - y) <= cutoff * cutoff:
                out.add(i); break
    return out


def main():
    cands = json.load(open(f'{SCRATCH}/eval_candidates.json'))
    ctrl = json.load(open(f'{SCRATCH}/h5_control_v3_analysis.json'))
    exp = parse_protein(f'{SCRATCH}/35TL.pdb')
    exp_ag = [r for k, r in exp.items() if k[0] == 'A']
    exp_vh = [r for k, r in exp.items() if k[0] == 'B']
    exp_vl = [r for k, r in exp.items() if k[0] == 'C']
    h5_interface = interface(exp_ag, exp_vh + exp_vl)
    print(f'H5 experimental PD-L1 interface: {len(h5_interface)} residues')

    results = []
    for c in cands:
        tag = f"cand{c['idx']}"
        d = f'{SCRATCH}/eval_{tag}_raw/full/boltz_outputs/boltz_results_1/predictions/1'
        conf = json.load(open(f'{d}/confidence_1_model_0.json'))
        pred = parse_protein(f'{d}/1_model_0.pdb')
        ag = [r for k, r in pred.items() if k[0] == 'A']
        scfv = [r for k, r in pred.items() if k[0] == 'B']
        pred_seq = ''.join(THREE2ONE[r['resn']] for r in scfv)
        assert pred_seq == c['scfv'], f'{tag} sequence echo mismatch'
        # scFv local numbering: VH 1..120, link 121..135, VL 136..242
        vh = scfv[:VH_N]
        vl = scfv[VH_N + LINK_N:]
        iface = interface(ag, scfv)
        # map 0-based antigen idx -> study numbering (pred chain A is study antigen 1-115, first res F1)
        # prediction chain A numbering starts at 1 (F1); idx i -> residue i+1
        iface_study = {i + 1 for i in iface}
        epi_hit = sorted(iface_study & set(EPI))
        hs_hit = sorted(iface_study & set(HOTSPOTS))
        h5_rec = len(iface_study & {exp_ag[i][0] if False else 0 for i in []}) # placeholder
        # H5 interface resSeqs from control analysis
        h5_res = set(ctrl['interface_recovery']['experimental_interface_resSeq'])
        h5_hit = sorted(iface_study & h5_res)
        rec = dict(
            tag=tag, idx=c['idx'],
            iptm=round(conf['iptm'], 4), complex_plddt=round(conf['complex_plddt'], 4),
            protein_iptm=round(conf.get('protein_iptm', conf['iptm']), 4),
            H3=c['H3'], L3=c['L3'], mut_H=c['mut_H'], mut_L=c['mut_L'],
            n_interface=len(iface),
            n_epitope_hits=len(epi_hit), epitope_coverage=round(len(epi_hit)/len(EPI), 3),
            hotspots_hit=hs_hit,
            h5_interface_recovery=round(len(h5_hit)/len(h5_res), 3),
            h5_interface_hits=len(h5_hit))
        results.append(rec)
        print(f"{tag}: ipTM {rec['iptm']}, pLDDT {rec['complex_plddt']}, "
              f"epitope coverage {rec['epitope_coverage']}, hotspots {hs_hit}, "
              f"H5-interface recovery {rec['h5_interface_recovery']}")

    print(f"\nH5 control (same protocol): ipTM {ctrl['confidence']['iptm']}, "
          f"interface recovery {ctrl['interface_recovery']['fraction']}, "
          f"global RMSD {ctrl['global_complex_ca_rmsd']} A")
    out = f'{SCRATCH}/candidate_eval_scores.json'
    json.dump(dict(h5_control=ctrl, candidates=results), open(out, 'w'), indent=1)
    print('wrote', out)


if __name__ == '__main__':
    main()
