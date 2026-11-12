#!/usr/bin/env python3
"""Run the released tFold-Ag evaluation paths for task 003.

This script deliberately keeps the screening and CDR-H3 recovery populations
separate. It uses the released tFold test-set MSA, labels, masked design FASTA
files, native structures and tFold model checkpoints.
"""
from __future__ import annotations

import argparse
import csv
import gc
import json
import os
from pathlib import Path
from typing import Any

import torch


def load_fasta(path: Path) -> dict[str, str]:
    seqs: dict[str, str] = {}
    current = None
    chunks: list[str] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            if current is not None:
                seqs[current] = "".join(chunks)
            current = line[1:].split()[0]
            chunks = []
        else:
            chunks.append(line)
    if current is not None:
        seqs[current] = "".join(chunks)
    return seqs


def make_chains(h: str, l: str, antigen: str, msa: list[str], deletion_matrix: Any) -> list[dict[str, Any]]:
    return [
        {"id": "H", "sequence": h},
        {"id": "L", "sequence": l},
        {"id": "A", "sequence": antigen, "msa": msa, "deletion_matrix": deletion_matrix},
    ]


def score_one(predictor: Any, chains: list[dict[str, Any]], chunk_size: int, icf_path: str | None = None) -> dict[str, float]:
    _, outputs = predictor.infer(chains, icf_path=icf_path, chunk_size=chunk_size)
    complex_id = "H:L:A"
    scores = outputs[complex_id]["3d"]["tmsc_dict"]
    out = {"ipTM": float(scores["iptm"].detach().cpu().item())}
    if "ptm" in scores:
        out["pTM"] = float(scores["ptm"].detach().cpu().item())
    return out


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")


def run_screen(args: argparse.Namespace) -> None:
    from tfold.model.pretrain import alpha_fold_4_ptm, esm_ppi_650m_ab, tfold_ag_base
    from tfold.deploy import AgPredictor
    from tfold.protein.parser import parse_a3m

    data = Path(args.data)
    pd1 = data / "PD-1"
    msa, deletion_matrix = parse_a3m((pd1 / "target.a3m").read_text())
    antigen = msa[0]
    labels = {}
    for line in (pd1 / "labels.txt").read_text().splitlines():
        name, label = line.split()
        labels[name] = int(label)

    from tfold.utils import setup
    setup(True, seed=args.seed)
    device = torch.device(args.device)
    predictor = AgPredictor(
        ppi_path=esm_ppi_650m_ab(),
        psp_path=alpha_fold_4_ptm(),
        ag_path=tfold_ag_base(),
    ).to(device)
    predictor.eval()

    out_rows: list[dict[str, Any]] = []
    ids = [x.strip() for x in (pd1 / "prot_ids.txt").read_text().splitlines() if x.strip()]
    if args.extra_fasta:
        ids += [x.strip() for x in args.extra_fasta.split(",") if x.strip()]
    ids = ids[args.start - 1:args.stop if args.stop else None]
    fasta_dir = pd1 / "fasta.files"
    for i, name in enumerate(ids, 1):
        if name in labels:
            fpath = fasta_dir / f"{name}.fasta"
        else:
            fpath = Path(args.extra_dir) / f"{name}.fasta"
        seqs = load_fasta(fpath)
        try:
            scores = score_one(predictor, make_chains(seqs["H"], seqs["L"], antigen, msa, deletion_matrix), args.chunk_size)
            row = {"id": name, "label": labels.get(name), "status": "completed", **scores}
        except Exception as exc:
            row = {"id": name, "label": labels.get(name), "status": "failed", "error": repr(exc)}
            torch.cuda.empty_cache()
        out_rows.append(row)
        if i % args.flush_every == 0 or i == len(ids):
            write_jsonl(Path(args.output), out_rows)
        print(json.dumps(row), flush=True)
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


def run_aar(args: argparse.Namespace) -> None:
    from tfold.model.pretrain import alpha_fold_4_ptm, esm_ppi_650m_ab, tfold_ag_ppi
    from tfold.deploy import AgPredictor
    from tfold.protein.parser import parse_a3m
    from tfold.utils import setup

    data = Path(args.data)
    root = data / "SAbDab-22H2-DesignAb"
    msa_dir = root / "msa.files"
    fasta_dir = root / "fasta.files"
    masked_dir = root / "fasta.files.design" / "cdr-h3"
    icf_dir = Path(args.icf_dir)
    setup(True, seed=args.seed)
    device = torch.device(args.device)
    predictor = AgPredictor(
        ppi_path=esm_ppi_650m_ab(),
        psp_path=alpha_fold_4_ptm(),
        ag_path=tfold_ag_ppi(),
    ).to(device)
    predictor.eval()

    rows: list[dict[str, Any]] = []
    ids = [x.strip() for x in (root / "prot_ids.txt").read_text().splitlines() if x.strip()]
    ids = ids[args.start - 1:args.stop if args.stop else None]
    for i, name in enumerate(ids, 1):
        native = load_fasta(fasta_dir / f"{name}.fasta")
        masked = load_fasta(masked_dir / f"{name}.fasta")
        msa_stem = "_".join(name.split("_")[::len(name.split("_")) - 1])
        msa, deletion_matrix = parse_a3m((msa_dir / f"{msa_stem}.a3m").read_text())
        h_mask = masked["H"]
        mask_pos = [j for j, aa in enumerate(h_mask) if aa == "X"]
        chains = make_chains(h_mask, masked["L"], msa[0], msa, deletion_matrix)
        icf = str(icf_dir / f"{name}.pt")
        try:
            if args.single_step:
                inputs, outputs = predictor.infer(chains, icf_path=icf, chunk_size=args.chunk_size)
            else:
                inputs, outputs = predictor.generate(chains, icf_path=icf, chunk_size=args.chunk_size)
            pred_ligand = outputs["H:L:A"]["1d"]["seq"]
            pred_h = pred_ligand[: len(h_mask)]
            native_h = native["H"]
            correct = sum(pred_h[j] == native_h[j] for j in mask_pos)
            row = {
                "id": name,
                "status": "completed",
                "masked_length": len(mask_pos),
                "correct": correct,
                "AAR": correct / len(mask_pos) if mask_pos else None,
                "predicted_cdrh3": "".join(pred_h[j] for j in mask_pos),
                "native_cdrh3": "".join(native_h[j] for j in mask_pos),
            }
        except Exception as exc:
            row = {"id": name, "status": "failed", "error": repr(exc)}
            torch.cuda.empty_cache()
        rows.append(row)
        if i % args.flush_every == 0 or i == len(ids):
            write_jsonl(Path(args.output), rows)
        print(json.dumps(row), flush=True)
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="mode", required=True)
    s = sub.add_parser("screen")
    s.add_argument("--data", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--extra-fasta", default="")
    s.add_argument("--extra-dir", default="")
    s.add_argument("--start", type=int, default=1)
    s.add_argument("--stop", type=int, default=0)
    s.add_argument("--device", default="cuda:0")
    s.add_argument("--chunk-size", type=int, default=256)
    s.add_argument("--seed", type=int, default=42)
    s.add_argument("--flush-every", type=int, default=1)
    s.set_defaults(func=run_screen)
    a = sub.add_parser("aar")
    a.add_argument("--data", required=True)
    a.add_argument("--icf-dir", required=True)
    a.add_argument("--output", required=True)
    a.add_argument("--start", type=int, default=1)
    a.add_argument("--stop", type=int, default=0)
    a.add_argument("--single-step", action="store_true")
    a.add_argument("--device", default="cuda:0")
    a.add_argument("--chunk-size", type=int, default=256)
    a.add_argument("--seed", type=int, default=42)
    a.add_argument("--flush-every", type=int, default=1)
    a.set_defaults(func=run_aar)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
