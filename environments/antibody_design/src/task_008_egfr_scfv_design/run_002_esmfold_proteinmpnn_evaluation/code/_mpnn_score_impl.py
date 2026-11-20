#!/usr/bin/env python3
"""run_002_esmfold_proteinmpnn_evaluation: ProteinMPNN score_only on ESMFold backbones, matched preparation.
For each ESMFold structure: score native(original) sequence AND, for candidate backbones,
the reference scFv on that backbone (matched original-vs-redesigned comparison).
Usage (under proteinmpnn env): _mpnn_score_impl.py <pdb_dir> <ref_seq_file> <out_json>"""
import json, os, sys, tempfile

sys.path.insert(0, '/home/boltzmann10/feb_work/ProteinMPNN')
from protein_mpnn_utils import parse_PDB  # noqa: E402
import torch  # noqa: E402
from protein_mpnn_utils import ProteinMPNN  # noqa: E402

pdb_dir, ref_file, out_json = sys.argv[1], sys.argv[2], sys.argv[3]
REF_SC = open(ref_file).read().split('\n', 1)[1].strip()

model = ProteinMPNN(ca_only=False, num_letters=21, node_features=128, k_neighbors=48)
ckpt = '/home/boltzmann10/feb_work/ProteinMPNN/model_weights/v_48_020.pt'
state = torch.load(ckpt, map_location='cpu')
model.load_state_dict(state)
model.eval()

out = {}
for f in sorted(os.listdir(pdb_dir)):
    if not f.endswith('.pdb'):
        continue
    name = f[:-4]
    parsed = parse_PDB(pdb_dir + '/' + f, input_chain_list=None)
    chain_str, chain_encoding, X, S, mask, resolutions, chain_M, chain_M_pos, omit_AA_mask, \
        tie_feaKinds, tied_pos_list_of_lists, pssm_coef, pssm_bias, pssm_opt, \
        deprecated_byres = parsed
    # simpler path: use the standard tuple
    (chain_str, S, L, mask, res_idx, chain_encoding_all, X, x_mask) = None, None, None, None, None, None, None, None
    import numpy as np
    from protein_mpnn_utils import StructureLoader
    loader = StructureLoader([parsed])
    for batch in loader:
        X, S, mask, lengths, chain_M, chain_encoding_all, chain_list_list, \
            S_list, chain_M_pos, omit_AA_mask, residue_idx, dihedral_mask, \
            tied_pos_list_of_lists, pssm_coef, pssm_bias, pssm_opt, byres_bias = batch
        with torch.no_grad():
            log_probs = model(X, S, mask, chain_M, residue_idx, chain_encoding_all)
            native_score = -(log_probs * torch.nn.functional.one_hot(S, 21)).sum(dim=(1, 2)) / (S.shape[1])
            global_native = -(log_probs * torch.nn.functional.one_hot(S, 21)).sum(dim=(1, 2)) / (S.shape[1] * mask.sum())
            # score the reference sequence on this backbone if different
            if name.startswith('cet_'):
                Sc = torch.tensor([[AA_ORDER.index(a) + 1 if a in AA_ORDER else 0 for a in REF_SC[:S.shape[1]]]]).repeat(S.shape[0], 1)
                sc_pad = torch.nn.functional.pad(Sc, (0, S.shape[1] - Sc.shape[1]), value=0)
                lp_ref = model(X, sc_pad, mask, chain_M, residue_idx, chain_encoding_all)
                ref_score = -(lp_ref * torch.nn.functional.one_hot(sc_pad, 21)).sum(dim=(1, 2)) / lengths.sum()
                out[name] = {'native_score': float(native_score.mean()),
                             'refseq_on_candidate_bb': float(ref_score.mean())}
            else:
                out[name] = {'native_score': float(native_score.mean())}
            print(name, out[name], flush=True)
json.dump(out, open(out_json, 'w'), indent=1)
