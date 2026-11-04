#!/usr/bin/env python3
"""immune_scan.py — siRNA innate-immune hazard flags (sequence-only).

Implements the published rule-set specified in
~/IMRAN/NOV26/siRNA-Design-Task-Specific/01_tools/open_source/specificity_structure_immune_tools.md
(verified 2026-11-03; no open-source scanner existed, so this implements it):

  UGUGU motif     TLR7/8 activation necessary-and-sufficient motif
                  (Hornung et al. Nat Med 2005, PMID 15723075; Judge et al. NBT 2005, PMID 15778705)
  GU fraction     GU-richness hazard (Judge 2005); flag top decile of cohort
  UUUU in 5' half U-rich 5' region risk (TLR7/8)
  len >= 21       TLR3 class effect — sequence-INDEPENDENT (Kleinman et al. Nature 2008, PMID 18368052):
                  every >=21-nt clinical-format duplex trips this channel; mitigation is chemistry/formulation
  5'-triphosphate RIG-I ligand — only in-vitro-transcribed RNA (Hornung et al. Science 2006, PMID 17038590);
                  synthetic siRNA lacks 5'ppp (flag only when ivt=True)

These are HAZARD FILTERS, not calibrated probabilities. Species- and route-dependent.
Chemical modification (2'-OMe/2'-F) suppresses TLR7/8 signaling but is NOT sequence-evaluable.

Both strands are scanned (innate sensing is not strand-exclusive). Output: JSON dict per sequence.
Usage:
  python3 immune_scan.py --guide ACGU... [--passenger ACGU...] [--ivt] [--cohort cohort.csv]
Cohort CSV needs a guide_sequence column; adds cohort_decile fields (requires >=10 rows).
MIT.
"""
import argparse
import csv
import json
import re
import sys

TLR7_MOTIF = re.compile(r"UGUGU")
U_RICH_5PRIME = re.compile(r"UUUU")


def _gu_fraction(seq: str) -> float:
    if len(seq) < 2:
        return 0.0
    dinucs = sum(seq.count(d) for d in ("GU", "UG"))
    return dinucs / (len(seq) - 1)


def scan_strand(seq: str, ivt: bool = False) -> dict:
    s = seq.upper().replace("T", "U")
    if set(s) - set("AUCG"):
        raise ValueError(f"non-RNA characters in sequence: {sorted(set(s) - set('AUCG'))}")
    half = s[: max(1, len(s) // 2)]
    return {
        "UGUGU_tlr7": bool(TLR7_MOTIF.search(s)),
        "UGUGU_count": len(TLR7_MOTIF.findall(s)),
        "GU_fraction": round(_gu_fraction(s), 4),
        "U_rich_5prime": bool(U_RICH_5PRIME.search(s[:10])),
        "len_ge21_tlr3_class": len(s) >= 21,
        "fivetriphosphate_rig_i": bool(ivt),  # only meaningful for IVT RNA
        "length": len(s),
        "u_rich_5prime_region": half,
    }


def scan(guide: str, passenger: str | None = None, ivt: bool = False) -> dict:
    out = {"guide": scan_strand(guide, ivt)}
    if passenger:
        out["passenger"] = scan_strand(passenger, ivt)
    out["any_tlr7_motif"] = out["guide"]["UGUGU_tlr7"] or out.get("passenger", {}).get("UGUGU_tlr7", False)
    out["interpretation_notes"] = [
        "Hazard filter, not calibrated probability (species/route dependent).",
        "TLR3 length flag is a class effect; mitigation is chemistry/formulation, not sequence.",
        "5'ppp flag applies only to in-vitro-transcribed RNA (synthetic siRNA is RIG-I-inert).",
        "2'-OMe/2'-F modifications suppress TLR7/8 signaling but are not sequence-evaluable here.",
    ]
    return out


def add_cohort_deciles(rows: list[dict]) -> list[dict]:
    """Flag top decile GU fraction across the cohort (Judge 2005 GU-richness criterion)."""
    guides = [r.get("guide", {}).get("GU_fraction", 0.0) for r in rows]
    if len(guides) < 10:
        for r in rows:
            r["cohort_decile"] = None
        return rows
    import statistics
    sorted_g = sorted(guides)
    def decile_of(v):
        below = sum(1 for g in sorted_g if g <= v)
        return min(10, max(1, int(10 * below / len(sorted_g)) + (1 if below == 0 else 0)))
    for r, v in zip(rows, guides):
        r["cohort_decile"] = decile_of(v)
        r["GU_top_decile_flag"] = r["cohort_decile"] == 10
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description="siRNA innate-immune hazard scan (both strands)")
    ap.add_argument("--guide", required=True, help="guide (antisense) 5'->3' RNA, T accepted")
    ap.add_argument("--passenger", default=None, help="passenger (sense) 5'->3' RNA")
    ap.add_argument("--ivt", action="store_true", help="in-vitro-transcribed RNA (adds RIG-I 5'ppp flag)")
    ap.add_argument("--cohort", default=None, help="CSV with guide_sequence column for decile flags")
    a = ap.parse_args()
    if a.cohort:
        rows = []
        with open(a.cohort) as f:
            for rec in csv.DictReader(f):
                rows.append(scan(rec["guide_sequence"], rec.get("passenger_sequence"), a.ivt))
        rows = add_cohort_deciles(rows)
        json.dump(rows, sys.stdout, indent=2)
    else:
        json.dump(scan(a.guide, a.passenger, a.ivt), sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
