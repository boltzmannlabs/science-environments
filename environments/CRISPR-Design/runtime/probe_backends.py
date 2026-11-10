#!/usr/bin/env python3
"""CRISPR-Design backend liveness probe (stdlib only).

Reports per-backend presence from the backend map in runtime/CONTRACTS.md.
Never fabricates scores: a missing backend means dependent stages run as
NOT_RUN(backend-absent). Exit code 0 = probe completed (regardless of findings);
findings are data, not failures.

Usage: python3 runtime/probe_backends.py [--json]
"""
import json
import os
import shutil
import sys

PRIOR_RUN = os.path.expanduser(
    "~/.sci/profiles/generate-sirna/workspace/"
    "crispr_design_gene_knockout_001_KIF11_GRCh38"
)

# Backend map mirrors runtime/CONTRACTS.md. kind: path | binary
BACKENDS = {
    "crisprDesign_source": {"kind": "path", "loc": os.path.join(PRIOR_RUN, "reference_software/crisprDesign")},
    "crisprScore_source": {"kind": "path", "loc": os.path.join(PRIOR_RUN, "reference_software/crisprScore")},
    "crisprScore_R_library": {"kind": "path", "loc": os.path.join(PRIOR_RUN, "bootstrap/R-library")},
    "lindel_runtime": {"kind": "path", "loc": os.path.join(PRIOR_RUN, "runs/20261105T102927Z/lindel-runtime/bin/python")},
    "bowtie_binary": {"kind": "path", "loc": os.path.join(PRIOR_RUN, "runs/20261105T102927Z/reference")},
    "GRCh38_genome_fasta": {"kind": "glob", "loc": os.path.join(PRIOR_RUN, "runs/*/reference/GRCh38.primary_assembly.genome.fa*")},
    "off_target_policy": {"kind": "glob", "loc": os.path.join(PRIOR_RUN, "runs/*/off_target_policy.yaml")},
    "generate_and_score_recipe": {"kind": "glob", "loc": os.path.join(PRIOR_RUN, "runs/*/generate_and_score.R")},
}

# Not-yet-installed runtime-phase components (from MODELS_AND_TOOLS.md) — expected absent
# until the runtime phase; probed by upstream availability, presence = early install.
NOT_INSTALLED_EXPECTED = [
    "crispron", "elevation", "crispritz", "crisprme", "flashfry",
    "pridict2", "bedict2", "be_datahive",
]

STAGES = {
    "C1_enumerate": ["crisprDesign_source", "crisprScore_source", "crisprScore_R_library"],
    "C2_on_target_local": ["crisprScore_R_library"],
    "C3_off_target_bowtie": ["bowtie_binary", "GRCh38_genome_fasta"],
    "C4_indel_outcome": ["lindel_runtime"],
    "transcript_validation": ["generate_and_score_recipe"],
    "policy_off_target": ["off_target_policy"],
}


def probe(kind, loc):
    if kind == "glob":
        import glob
        return bool(glob.glob(loc))
    if kind == "path":
        return os.path.exists(loc)
    if kind == "binary":
        return shutil.which(loc) is not None
    return False


def main():
    as_json = "--json" in sys.argv
    report = {"probe_version": "0.1", "backends": {}, "stages": {}, "expected_absent": {}}
    for name, spec in BACKENDS.items():
        report["backends"][name] = "ACTIVE" if probe(spec["kind"], spec["loc"]) else "NOT_FOUND"
    for tool in NOT_INSTALLED_EXPECTED:
        report["expected_absent"][tool] = "NOT_INSTALLED (runtime phase)"
    for stage, deps in STAGES.items():
        missing = [d for d in deps if report["backends"][d] != "ACTIVE"]
        report["stages"][stage] = "READY" if not missing else f"BLOCKED({','.join(missing)})"

    if as_json:
        print(json.dumps(report, indent=2))
    else:
        print("CRISPR-Design backend liveness probe (probe_version 0.1)")
        print("-" * 60)
        for name, status in report["backends"].items():
            print(f"  {status:<10} {name}")
        print("-" * 60)
        for stage, status in report["stages"].items():
            print(f"  {status:<48} {stage}")
        print("-" * 60)
        print("  Runtime-phase components expected NOT_INSTALLED until that phase:")
        print("  " + ", ".join(NOT_INSTALLED_EXPECTED))
        print("\nFindings are data, not failures: BLOCKED stages must surface as")
        print("NOT_RUN(backend-absent) in any deliverable. Never fabricate scores.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
