#!/usr/bin/env python3
"""Task 002 open-source structural benchmark.

This script does not generate designs. It converts retained Boltz-2 mmCIF
complexes into a chain-mapped PDB representation, then runs reproducible
candidate-level structure/interface analyses and a native-vs-predicted H5
DockQ check.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable

import numpy as np
from Bio.PDB import MMCIFParser, PDBIO, PDBParser, Select
from Bio.PDB.Chain import Chain
from Bio.PDB.Model import Model
from Bio.PDB.Structure import Structure
from Bio.PDB.Residue import Residue

AA3 = {
    "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C",
    "GLN": "Q", "GLU": "E", "GLY": "G", "HIS": "H", "ILE": "I",
    "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F", "PRO": "P",
    "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V",
}
HYDROPHOBIC = set("ACFILMPVWY")
DONOR_ELEMENTS = {"N", "O", "S"}
ACCEPTOR_ELEMENTS = {"N", "O", "S"}


def run(cmd: list[str], *, cwd: Path | None = None) -> tuple[int, str, str]:
    p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    return p.returncode, p.stdout, p.stderr


def residues(chain) -> list[Residue]:
    return [r for r in chain if r.id[0] == " "]


def copy_residue(res: Residue, new_id: int) -> Residue:
    r = res.copy()
    r.id = (" ", new_id, " ")
    return r


def save_structure(structure: Structure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    io = PDBIO()
    io.set_structure(structure)
    io.save(str(path))


def standardize_candidate(cif_path: Path, out_path: Path) -> dict:
    parser = MMCIFParser(QUIET=True)
    source = parser.get_structure(cif_path.stem, str(cif_path))[0]
    antibody = source["scfv"]
    antigen = source["pdl1"]
    ab_res = residues(antibody)
    ag_res = residues(antigen)
    if len(ab_res) < 136 or len(ag_res) < 10:
        raise ValueError(f"Unexpected candidate chain lengths: {len(ab_res)}, {len(ag_res)}")

    # Retained scFv convention: VH 1-120, linker 121-135, VL 136-end.
    vh_res = ab_res[:120]
    vl_res = ab_res[135:]
    s = Structure(out_path.stem)
    m = Model(0)
    s.add(m)
    for chain_id, source_res in [("A", ag_res), ("B", vh_res), ("C", vl_res)]:
        c = Chain(chain_id)
        for i, r in enumerate(source_res, 1):
            c.add(copy_residue(r, i))
        m.add(c)
    save_structure(s, out_path)
    return {
        "source": str(cif_path),
        "standardized_pdb": str(out_path),
        "chain_map": {"A": "PD-L1 antigen", "B": "VH", "C": "VL"},
        "source_chain_lengths": {"scfv": len(ab_res), "pdl1": len(ag_res)},
        "standardized_chain_lengths": {"A": len(ag_res), "B": len(vh_res), "C": len(vl_res)},
        "linker_residues_removed": 15,
    }


def load_atoms(path: Path, chains: set[str] | None = None):
    st = PDBParser(QUIET=True).get_structure(path.stem, str(path))[0]
    atoms = []
    for c in st:
        if chains and c.id not in chains:
            continue
        for r in residues(c):
            for a in r:
                if a.element == "H":
                    continue
                atoms.append((c.id, r, a))
    return atoms


def residue_sequence(chain) -> str:
    return "".join(AA3.get(r.resname.upper(), "X") for r in residues(chain))


def chain_sequences(path: Path) -> dict[str, str]:
    st = PDBParser(QUIET=True).get_structure(path.stem, str(path))[0]
    return {c.id: residue_sequence(c) for c in st}


def interface_metrics(path: Path, hotspot_residues: set[int]) -> dict:
    ab_atoms = load_atoms(path, {"B", "C"})
    ag_atoms = load_atoms(path, {"A"})
    pairs = []
    for c1, r1, a1 in ab_atoms:
        for c2, r2, a2 in ag_atoms:
            d = float(np.linalg.norm(a1.coord - a2.coord))
            if d <= 5.0:
                pairs.append((c1, r1, a1, c2, r2, a2, d))
    residue_pairs = {(x[0], x[1].id[1], x[3], x[4].id[1]) for x in pairs}
    interface_ab_res = {(x[0], x[1].id[1]) for x in pairs}
    interface_ag_res = {x[4].id[1] for x in pairs}
    min_dist = min((x[-1] for x in pairs), default=None)
    hotspot_pairs = [x for x in pairs if x[4].id[1] in hotspot_residues]
    hotspot_touched = sorted({x[4].id[1] for x in hotspot_pairs})

    # Conservative heavy-atom donor/acceptor approximation; hydrogens and
    # explicit donor angles are absent in the retained predicted structures.
    hb_pairs = set()
    for x in pairs:
        c1, r1, a1, c2, r2, a2, d = x
        e1 = (a1.element or a1.get_name()[0]).upper()
        e2 = (a2.element or a2.get_name()[0]).upper()
        if d <= 3.5 and ((e1 in DONOR_ELEMENTS and e2 in ACCEPTOR_ELEMENTS) or (e2 in DONOR_ELEMENTS and e1 in ACCEPTOR_ELEMENTS)):
            hb_pairs.add((c1, r1.id[1], a1.get_name(), c2, r2.id[1], a2.get_name()))

    # Germinal-like interface CDR percentage using IMGT numbering where the
    # installed ANARCI backend is available. The exact Rosetta metric is not
    # claimed; this is a sequence-position-resolved open-source proxy.
    cdr_positions: set[tuple[str, int]] = set()
    cdr_status = "not_run"
    try:
        from abnumber import Chain as AbChain
        st = PDBParser(QUIET=True).get_structure(path.stem, str(path))[0]
        for cid, label in [("B", "H"), ("C", "L")]:
            seq = residue_sequence(st[cid])
            ab = AbChain(seq, scheme="imgt")
            for pos, aa in ab:
                if pos.get_region() in {"CDR1", "CDR2", "CDR3"}:
                    cdr_positions.add((cid, pos.number))
        cdr_status = "executed"
    except Exception as e:
        cdr_status = f"failed:{type(e).__name__}:{e}"
    cdr_interface = sum((c, n) in cdr_positions for c, n in interface_ab_res)
    percent_interface_cdr = (cdr_interface / len(interface_ab_res)) if interface_ab_res else None
    hydrophobic_interface = sum(AA3.get(r.resname.upper(), "X") in HYDROPHOBIC for c, n in interface_ab_res for r in [PDBParser(QUIET=True).get_structure(path.stem, str(path))[0][c][(" ", n, " ")]])
    return {
        "interface_atom_contact_pairs_5A": len(pairs),
        "interface_residue_pairs_5A": len(residue_pairs),
        "interface_antibody_residue_count_5A": len(interface_ab_res),
        "interface_antigen_residue_count_5A": len(interface_ag_res),
        "interface_min_heavy_atom_distance_A": min_dist,
        "hotspot_residues": sorted(hotspot_residues),
        "hotspot_residues_touched": hotspot_touched,
        "hotspot_contact_pairs_5A": len(hotspot_pairs),
        "interface_hbond_heavy_atom_proxy_count": len(hb_pairs),
        "interface_cdr_residue_count_imgt_proxy": cdr_interface,
        "interface_cdr_fraction_imgt_proxy": percent_interface_cdr,
        "interface_hydrophobic_residue_count_proxy": hydrophobic_interface,
        "cdr_mapping_status": cdr_status,
        "contact_definition": "all heavy atoms, antibody chains B/C versus antigen chain A, <=5.0 A",
        "hbond_definition": "heavy-atom donor/acceptor element proxy <=3.5 A; no donor-angle validation",
    }


def split_chains(src: Path, out_dir: Path, stem: str) -> tuple[Path, Path, Path]:
    st = PDBParser(QUIET=True).get_structure(src.stem, str(src))[0]
    paths = {}
    for name, keep in [("complex", {"A", "B", "C"}), ("antibody", {"B", "C"}), ("antigen", {"A"})]:
        s = Structure(f"{stem}_{name}")
        m = Model(0)
        s.add(m)
        for cid in sorted(keep):
            if cid not in st:
                continue
            c = st[cid].copy()
            m.add(c)
        p = out_dir / f"{stem}_{name}.pdb"
        save_structure(s, p)
        paths[name] = p
    return paths["complex"], paths["antibody"], paths["antigen"]


def freesasa_metrics(complex_pdb: Path, antibody_pdb: Path, antigen_pdb: Path) -> dict:
    try:
        import freesasa
        vals = {"complex": freesasa.calc(freesasa.Structure(str(complex_pdb))).totalArea(), "antibody": freesasa.calc(freesasa.Structure(str(antibody_pdb))).totalArea(), "antigen": freesasa.calc(freesasa.Structure(str(antigen_pdb))).totalArea()}
        vals["buried_surface_area_A2"] = (vals["antibody"] + vals["antigen"] - vals["complex"]) / 2.0
        vals["tool_status"] = "executed"
        vals["definition"] = "FreeSASA total SASA; BSA=(antibody+antigen-complex)/2"
        return vals
    except Exception as e:
        return {"tool_status": f"failed:{type(e).__name__}:{e}"}


def parse_prodigy(text: str) -> dict:
    out = {}
    pats = {
        "predicted_binding_affinity_kcal_mol": r"Predicted binding affinity \(kcal\.mol-1\):\s*([-+0-9.eE]+)",
        "predicted_kd_M": r"Predicted dissociation constant \(M\) at 25\.0.*?:\s*([-+0-9.eE]+)",
        "intermolecular_contacts": r"No\. of intermolecular contacts:\s*(\d+)",
        "interface_residues": r"No\. of interface residues:\s*(\d+)",
    }
    for k, p in pats.items():
        m = re.search(p, text)
        if m:
            out[k] = float(m.group(1)) if "." in m.group(1) or "e" in m.group(1).lower() else int(m.group(1))
    out["raw_stdout"] = text
    return out


def run_prodigy(exe: str, pdb: Path, raw_dir: Path, name: str) -> dict:
    rc, stdout, stderr = run([exe, str(pdb), "--selection", "B,C", "A"])
    (raw_dir / f"{name}_prodigy.stdout.txt").write_text(stdout)
    (raw_dir / f"{name}_prodigy.stderr.txt").write_text(stderr)
    result = parse_prodigy(stdout)
    result["returncode"] = rc
    result["tool_status"] = "executed" if rc == 0 and "predicted_binding_affinity" in "".join(result.keys()) else f"failed_returncode_{rc}"
    return result


def run_dockq(python: str, dockq_py: str, model: Path, native: Path, raw_dir: Path) -> dict:
    cmd = [python, dockq_py, str(model), str(native), "--mapping", "ABC:ABC", "--short"]
    rc, stdout, stderr = run(cmd)
    (raw_dir / "h5_dockq.stdout.txt").write_text(stdout)
    (raw_dir / "h5_dockq.stderr.txt").write_text(stderr)
    result = {"returncode": rc, "command": cmd, "tool_status": "executed" if rc == 0 else f"failed_returncode_{rc}", "stdout": stdout}
    total = re.search(r"Total DockQ over (\d+) native interfaces:\s*([0-9.]+)", stdout)
    if total:
        result["total_native_interfaces"] = int(total.group(1))
        result["total_dockq"] = float(total.group(2))
    interfaces = []
    pat = re.compile(r"DockQ ([0-9.]+) iRMSD ([0-9.]+) LRMSD ([0-9.]+) fnat ([0-9.]+) fnonnat ([0-9.]+) F1 ([0-9.]+) clashes (\d+) mapping ([A-Z]+):([A-Z]+)")
    for m in pat.finditer(stdout):
        interfaces.append({"dockq": float(m.group(1)), "iRMSD": float(m.group(2)), "LRMSD": float(m.group(3)), "fnat": float(m.group(4)), "fnonnat": float(m.group(5)), "F1": float(m.group(6)), "clashes": int(m.group(7)), "model_chains": m.group(8), "native_chains": m.group(9)})
    result["interfaces"] = interfaces
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--result-root", type=Path, required=True)
    ap.add_argument("--output-root", type=Path, required=True)
    ap.add_argument("--h5-pred", type=Path, required=True)
    ap.add_argument("--native-35tl", type=Path, required=True)
    ap.add_argument("--prodigy", default="prodigy")
    ap.add_argument("--dockq-python", default=sys.executable)
    ap.add_argument("--dockq-script", required=True)
    ap.add_argument("--hotspots", default="37,39,41,96,98")
    args = ap.parse_args()
    args.output_root.mkdir(parents=True, exist_ok=True)
    raw_dir = args.output_root / "raw"
    pdb_dir = args.output_root / "standardized_pdb"
    raw_dir.mkdir(parents=True, exist_ok=True)
    pdb_dir.mkdir(parents=True, exist_ok=True)
    hotspots = {int(x) for x in args.hotspots.split(",") if x}

    shortlist = []
    with (args.result_root / "shortlist.csv").open() as f:
        shortlist = list(csv.DictReader(f))
    candidates = {r["candidate_id"]: r for r in shortlist}
    candidate_cifs = {p.name.split("_scfv_pdl1_model_0")[0]: p for p in (args.result_root / "structures").glob("*_scfv_pdl1_model_0.cif")}
    records = []
    for cid in [r["candidate_id"] for r in shortlist]:
        cif = candidate_cifs[cid]
        pdb = pdb_dir / f"{cid}.pdb"
        mapping = standardize_candidate(cif, pdb)
        complex_pdb, antibody_pdb, antigen_pdb = split_chains(pdb, pdb_dir, cid)
        im = interface_metrics(complex_pdb, hotspots)
        fs = freesasa_metrics(complex_pdb, antibody_pdb, antigen_pdb)
        prod = run_prodigy(args.prodigy, complex_pdb, raw_dir, cid)
        rec = {"candidate_id": cid, **mapping, **im, "freesasa": fs, "prodigy": prod}
        records.append(rec)

    h5_dockq = run_dockq(args.dockq_python, args.dockq_script, args.h5_pred, args.native_35tl, raw_dir)
    tool_versions = {}
    for label, cmd in [("prodigy", [args.prodigy, "--help"]), ("dockq", [args.dockq_python, args.dockq_script, "--help"])]:
        rc, stdout, stderr = run(cmd)
        tool_versions[label] = {"returncode": rc, "help_head": (stdout or stderr)[:1000]}
    tool_versions["python"] = sys.version
    try:
        import Bio, numpy
        tool_versions["biopython"] = Bio.__version__
        tool_versions["numpy"] = numpy.__version__
    except Exception:
        pass
    try:
        import freesasa
        tool_versions["freesasa"] = getattr(freesasa, "__version__", "unknown")
    except Exception:
        pass
    try:
        from abnumber import __version__ as abnumber_version
        tool_versions["abnumber"] = abnumber_version
    except Exception:
        pass

    output = {
        "task_id": "task_002_pdl1_epitope_targeted_scfv_design",
        "scope": "shortlisted five candidates plus H5 prediction/native reference",
        "benchmark_reference": "Task 002 benchmark; Germinal H5/PD-L1 PDB 35TL; published H5 RMSD 1.25 A",
        "candidate_chain_mapping": "A=PD-L1, B=VH, C=VL; linker residues removed from candidate scFv for chain-separated structural tools",
        "hotspots": sorted(hotspots),
        "candidate_results": records,
        "h5_dockq": h5_dockq,
        "tool_versions": tool_versions,
        "limitations": [
            "Candidate Prodigy values are model estimates, not affinity measurements.",
            "The interface CDR fraction and H-bond values are open-source proxies, not PyRosetta InterfaceAnalyzerMover outputs.",
            "Exact Germinal iAlign IS against the complete PDB/OAS/design-set database was not reproduced because standalone ialign.pl was not available in the environment.",
            "H5 DockQ is a same-complex prediction-vs-native comparison; applying DockQ to novel candidates against H5 would be a non-like-for-like sequence/structure comparison and is not reported as a pass/fail benchmark.",
        ],
    }
    (args.output_root / "open_source_benchmark.json").write_text(json.dumps(output, indent=2) + "\n")
    with (args.output_root / "candidate_metrics.csv").open("w", newline="") as f:
        fields = ["candidate_id", "interface_atom_contact_pairs_5A", "interface_residue_pairs_5A", "interface_antibody_residue_count_5A", "interface_antigen_residue_count_5A", "interface_min_heavy_atom_distance_A", "hotspot_residues_touched", "hotspot_contact_pairs_5A", "interface_hbond_heavy_atom_proxy_count", "interface_cdr_fraction_imgt_proxy", "interface_hydrophobic_residue_count_proxy", "buried_surface_area_A2", "predicted_binding_affinity_kcal_mol", "predicted_kd_M", "intermolecular_contacts", "prodigy_status"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in records:
            prod = r.get("prodigy", {})
            fs = r.get("freesasa", {})
            w.writerow({
                "candidate_id": r["candidate_id"],
                "interface_atom_contact_pairs_5A": r.get("interface_atom_contact_pairs_5A"),
                "interface_residue_pairs_5A": r.get("interface_residue_pairs_5A"),
                "interface_antibody_residue_count_5A": r.get("interface_antibody_residue_count_5A"),
                "interface_antigen_residue_count_5A": r.get("interface_antigen_residue_count_5A"),
                "interface_min_heavy_atom_distance_A": r.get("interface_min_heavy_atom_distance_A"),
                "hotspot_residues_touched": ";".join(map(str, r.get("hotspot_residues_touched", []))),
                "hotspot_contact_pairs_5A": r.get("hotspot_contact_pairs_5A"),
                "interface_hbond_heavy_atom_proxy_count": r.get("interface_hbond_heavy_atom_proxy_count"),
                "interface_cdr_fraction_imgt_proxy": r.get("interface_cdr_fraction_imgt_proxy"),
                "interface_hydrophobic_residue_count_proxy": r.get("interface_hydrophobic_residue_count_proxy"),
                "buried_surface_area_A2": fs.get("buried_surface_area_A2"),
                "predicted_binding_affinity_kcal_mol": prod.get("predicted_binding_affinity_kcal_mol"),
                "predicted_kd_M": prod.get("predicted_kd_M"),
                "intermolecular_contacts": prod.get("intermolecular_contacts"),
                "prodigy_status": prod.get("tool_status"),
            })
    print(json.dumps({"output": str(args.output_root / "open_source_benchmark.json"), "n_candidates": len(records), "h5_dockq_status": h5_dockq.get("tool_status")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
