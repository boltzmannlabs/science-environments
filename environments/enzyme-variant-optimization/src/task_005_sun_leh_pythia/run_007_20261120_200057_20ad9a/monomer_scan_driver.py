import argparse
import os
import sys
import torch
import numpy as np
import pandas as pd
from Bio.PDB.Polypeptide import index_to_one

sys.path.insert(0, "retained-private-evidence/Pythia-e1943402092295ae96cde0c93073ddc933ffc433")
from pythia.model import AMPNN
from pythia.pdb_utils import read_pdb_to_protbb, get_neighbor

def load_model(ckpt_path, device):
    model = AMPNN(embed_dim=128, edge_dim=27, node_dim=28, dropout=0.2, layer_nums=3, token_num=21)
    model.load_state_dict(torch.load(ckpt_path, map_location=torch.device(device), weights_only=True))
    model.eval()
    model.to(device)
    return model

def scan_monomer(pdb_path, chain_id, model_c, model_p, device):
    # Extract single-chain PDB
    import tempfile
    with open(pdb_path) as f:
        lines = f.readlines()
    # Keep SEQRES, HEADER, etc. for the target chain; filter ATOM/HETATM by chain
    monomer_lines = []
    for L in lines:
        if L.startswith("ATOM") or L.startswith("HETATM"):
            if L[21] == chain_id:
                monomer_lines.append(L)
        elif L.startswith("SEQRES"):
            if L[11] == chain_id:
                monomer_lines.append(L)
        elif L.startswith(("HEADER","TITLE","COMPND","SOURCE","KEYWDS","EXPDTA","AUTHOR","REVDAT","JRNL","REMARK","END")):
            monomer_lines.append(L)
    # Write monomer PDB
    monomer_path = pdb_path.replace(".pdb", f"_{chain_id}_monomer.pdb")
    with open(monomer_path, "w") as f:
        f.writelines(monomer_lines)
    # Run Pythia scan on monomer
    protbb = read_pdb_to_protbb(monomer_path)
    node, edge, seq = get_neighbor(protbb, noise_level=0.0)
    seq_list = protbb.seq.squeeze(-1).long().tolist()
    resseq_list = protbb.resseq.squeeze(-1).long().tolist()
    chain_list = protbb.chain_num.squeeze(-1).long().tolist()
    L = len(seq_list)
    all_probs = []
    with torch.no_grad():
        for model in [model_c, model_p]:
            logits, _ = model(node.to(device), edge.to(device))
            prob = torch.softmax(logits, dim=-1).detach().cpu().numpy()
            all_probs.append(prob)
    rows = []
    for pos in range(L):
        native_aa_idx = seq_list[pos]
        for alt_aa_idx in range(20):
            energies = []
            for prob in all_probs:
                p_alt = prob[pos][alt_aa_idx]
                p_nat = prob[pos][native_aa_idx]
                energies.append(-np.log(p_alt / p_nat))
            rows.append({
                "context": "monomer_" + chain_id,
                "chain": chain_list[pos],
                "resseq": resseq_list[pos],
                "pos": pos + 1,
                "native_aa": index_to_one(native_aa_idx),
                "alt_aa": index_to_one(alt_aa_idx),
                "C_score": float(energies[0]),
                "P_score": float(energies[1]),
                "sum_score": float(energies[0] + energies[1]),
                "mean_score": float((energies[0] + energies[1]) / 2),
            })
    return pd.DataFrame(rows)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdb", required=True)
    parser.add_argument("--chain", required=True, choices=["A", "B"])
    parser.add_argument("--output_csv", required=True)
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()
    device = torch.device(args.device)
    model_c = load_model("retained-private-evidence/pythia-c.pt", device)
    model_p = load_model("retained-private-evidence/pythia-p.pt", device)
    df = scan_monomer(args.pdb, args.chain, model_c, model_p, device)
    df.to_csv(args.output_csv, index=False)
    print(f"Wrote {len(df)} rows for monomer {args.chain} to {args.output_csv}")

if __name__ == "__main__":
    main()
