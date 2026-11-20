#!/usr/bin/env python3
"""Generate the four IgDesign execution configs for task_014 run_002.

Writes inputs/<exec>.yaml for hcdr3_1shot, hcdr3_best100, hcdr123_1shot,
hcdr123_best100 using the verified 6hhc_seqres.pdb (A=VL, B=VH, C=FXIa).
Region positions are 0-based within the truncated 120-aa VH variable domain,
verified against the released Osocimab-FXI.csv (HCDR1 25-32, HCDR2 50-57,
HCDR3 96-108).
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(HERE, "..")
IG = "/home/boltzmann10/agent_sci_boltpro_errors_tools/igdesign"

STRUCTURE = os.path.abspath(os.path.join(RUN, "inputs", "6hhc_seqres.pdb"))
CKPT_LM = f"{IG}/ckpts/igdesign_acvr2b_holdout.ckpt"
CKPT_PM = f"{IG}/ckpts/igmpnn_acvr2b_holdout.ckpt"

REGIONS = {
    "hcdr1": {"positions": list(range(25, 33)), "chain": "heavy"},
    "hcdr2": {"positions": list(range(50, 58)), "chain": "heavy"},
    "hcdr3": {"positions": list(range(96, 109)), "chain": "heavy"},
}

RUNS = [
    ("hcdr3_1shot", ["hcdr3"], 1, 1, 1, 0),
    ("hcdr3_best100", ["hcdr3"], 10, 10, 1, 1),
    ("hcdr123_1shot", ["hcdr1", "hcdr2", "hcdr3"], 1, 1, 1, 0),
    ("hcdr123_best100", ["hcdr1", "hcdr2", "hcdr3"], 10, 10, 1, 1),
]

TEMPLATE = """# IgDesign config: task_014 run_002 {exec} ({scope}, {n} sample(s), seed {seed})
structure_path: "{structure}"
lmdesign_checkpoint: "{ckpt_lm}"
pmpnn_checkpoint: "{ckpt_pm}"
save_path: "{save_path}"
region_order: {order}
lmdesign_num_decoding_orders: {n_ord}
lmdesign_num_pmpnn_seqs: {n_pm}
lmdesign_num_lm_seqs: 1
lmdesign_pmpnn_logit_temperature: 0.5
lmdesign_output_logit_temperature: 0.5
independent_loss: true
condition_on_light_chain: true
condition_on_antigen: true
predict_light_chain: false
batch_size: 1
num_batches: 1
random_seed: {seed}
epitope_idxs_or_all: all
antigen_chain_id: "C"
heavy_chain_id: "B"
light_chain_id: "A"
regions:
{regions}
"""


def main():
    for exec_id, order, n_ord, n_pm, n_lm, seed in RUNS:
        n = n_ord * n_pm * n_lm
        regions = ""
        for r in order:
            regions += f"  {r}:\n    positions: {REGIONS[r]['positions']}\n    chain: \"{REGIONS[r]['chain']}\"\n"
        save = os.path.abspath(os.path.join(
            RUN, "..", "..", "..", "results", "task_014_fxi_igdesign_cdr_redesign",
            "run_002_igdesign_native_reconstruction", "raw", f"{exec_id}_samples.csv"))
        os.makedirs(os.path.dirname(save), exist_ok=True)
        cfg = TEMPLATE.format(
            exec=exec_id, scope="+".join(order), n=n, seed=seed,
            structure=STRUCTURE, ckpt_lm=CKPT_LM, ckpt_pm=CKPT_PM,
            save_path=save, order=order, n_ord=n_ord, n_pm=n_pm,
            regions=regions)
        out = os.path.join(RUN, "inputs", f"{exec_id}.yaml")
        with open(out, "w") as f:
            f.write(cfg)
        print(f"WROTE {out} ({n} samples)")


if __name__ == "__main__":
    main()
