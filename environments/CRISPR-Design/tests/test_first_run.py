#!/usr/bin/env python3
"""Run-validation tests for CRISPR-Design Run1 (task 002, KIF11).

Validates the executed run's artifacts: structure, coordinate integrity
(independent python re-extraction from the genome), scorer determinism,
the Lindel regression anchor, off-target positive/negative controls,
cross-endpoint sanity (Spearman), DRAFT-gate conformance, and provenance.
Stdlib only. Writes <run>/tests/run_tests.json.

Usage: python3 tests/test_first_run.py [run_dir]
"""
import csv
import hashlib
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = os.path.dirname(HERE)
BASE = "/home/boltzmann13/.sci/profiles/generate-sirna/workspace/crispr_design_gene_knockout_001_KIF11_GRCh38"
RSCRIPT = f"{BASE}/bootstrap/runtime/bin/Rscript"
LINDEL_ENV = f"{BASE}/runs/20261105T102927Z/lindel-runtime"
BOWTIE = f"{BASE}/bootstrap/runtime/bin/bowtie"
RUN = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    ENV, "results/002_knockout_gene_disruption/Run1_20261110")

results = {"run": RUN, "tests": [], "passed": 0, "failed": 0}


def check(name, fn):
    try:
        detail = fn()
        results["tests"].append({"test": name, "status": "PASS", "detail": detail})
        results["passed"] += 1
        print(f"  PASS  {name}: {detail}")
    except Exception as e:
        results["tests"].append({"test": name, "status": "FAIL", "detail": str(e)[:400]})
        results["failed"] += 1
        print(f"  FAIL  {name}: {str(e)[:400]}")


def read_rows(name):
    with open(os.path.join(RUN, name), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_fai(fa):
    idx = {}
    with open(fa + ".fai", encoding="utf-8") as f:
        for line in f:
            n, ln, off, lb, lw = line.split("\t")[:5]
            idx[n] = (int(ln), int(off), int(lb), int(lw))
    return idx


def fetch(fa, idx, chrom, start, end):
    """1-based closed fetch."""
    ln, off, lb, lw = idx[chrom]
    out = []
    with open(fa, "rb") as f:
        for pos in range(start, end + 1):
            f.seek(off + (pos - 1) // lb * lw + (pos - 1) % lb)
            out.append(f.read(1).decode())
    return "".join(out).upper()


def revcomp(s):
    return s.translate(str.maketrans("ACGT", "TGCA"))[::-1]


def spearman(a, b):
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    ra, rb = ranks(a), ranks(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    da = math.sqrt(sum((x - ma) ** 2 for x in ra))
    db = math.sqrt(sum((y - mb) ** 2 for y in rb))
    return num / (da * db) if da and db else float("nan")


# ---------- T1 artifacts ----------
def t1():
    need = ["candidate_pool.csv", "off_target_sites.csv", "gate_log.csv",
            "ranked_shortlist.csv", "run_record_stage1.json", "run_record_stage2.json",
            "00_inputs/requirement_brief.json", "00_inputs/thresholds.json",
            "bowtie_alignments.tsv"]
    missing = [n for n in need if not os.path.isfile(os.path.join(RUN, n))]
    if missing:
        raise AssertionError(f"missing artifacts: {missing}")
    pool = read_rows("candidate_pool.csv")
    req_cols = {"candidate_id", "guide_sequence", "pam", "chromosome", "start", "end",
                "strand", "rs1_score", "rs3_seq_hsu2013", "crisprater_score",
                "crisprscan_t7", "frameshift_score", "gate_status",
                "weighted_preference_score", "evidence_tier"}
    missing_cols = req_cols - set(pool[0].keys())
    if missing_cols:
        raise AssertionError(f"pool missing columns: {missing_cols}")
    return f"{len(pool)} pool rows, {len(need)} artifacts present"


# ---------- T2 coordinate integrity (independent extraction) ----------
def t2():
    pool = [r for r in read_rows("candidate_pool.csv") if r["activity_status"] == "SCORED"]
    step = max(1, len(pool) // 40)
    sample = pool[::step][:40]
    fa = os.path.join(RUN, "reference/GRCh38.primary_assembly.genome.fa")
    idx = read_fai(fa)
    bad = []
    for r in sample:
        s, e, strand = int(r["start"]), int(r["end"]), r["strand"]
        spacer = fetch(fa, idx, r["chromosome"], s, e)
        if strand == "-":
            spacer = revcomp(spacer)
            pam = revcomp(fetch(fa, idx, r["chromosome"], s - 3, s - 1))
        else:
            pam = fetch(fa, idx, r["chromosome"], e + 1, e + 3)
        if spacer != r["guide_sequence"] or pam != r["pam"]:
            bad.append(r["candidate_id"])
    if bad:
        raise AssertionError(f"coordinate mismatches: {bad[:5]}")
    return f"{len(sample)} guides re-extracted from genome: spacer+PAM exact"


# ---------- T3 determinism (rescore fixture) ----------
def t3():
    fixture = os.path.join(RUN, "determinism_fixture_spacers.txt")
    spacers = [l.strip() for l in open(fixture) if l.strip()][:20]
    r = subprocess.run([RSCRIPT, "-e", f'''
.libPaths(c("{BASE}/bootstrap/R-library",.libPaths()))
suppressPackageStartupMessages(library(crisprScore))
sp <- c({",".join('"%s"' % s for s in spacers)})
s30 <- paste0("ACGT", sp, "AGG", "CCT")
a <- getRuleSet1Scores(s30)$score
b <- vapply(sp, function(x) getCRISPRaterScores(x)$score, numeric(1))
cat(paste(sprintf("%.12f,%.12f", a, b), collapse=";"))
'''], capture_output=True, text=True, timeout=600)
    out = r.stdout.strip().splitlines()[-1]
    pairs = [x.split(",") for x in out.split(";")]
    pool = {row["guide_sequence"]: row for row in read_rows("candidate_pool.csv")
            if row["activity_status"] == "SCORED"}
    mism = []
    for spacer, (rs1, cr) in zip(spacers, pairs):
        row = pool.get(spacer)
        if row is None:
            mism.append(f"{spacer}:absent")
            continue
        if abs(float(row["rs1_score"]) - float(rs1)) > 1e-9 or \
           abs(float(row["crisprater_score"]) - float(cr)) > 1e-9:
            mism.append(row["candidate_id"])
    if mism:
        raise AssertionError(f"nondeterministic rescores: {mism[:5]}")
    return f"{len(spacers)} guides rescored: RS1+CRISPRater bit-stable (<=1e-9)"


# ---------- T4 Lindel regression anchor ----------
def t4():
    x = ("ACCTTTTAATCGA" + "TGCTGATGCTAGATATTAAG" + "TGG" +
         "CTTTTAATCGATGCTGATGCTAGATATTA")
    assert len(x) == 65
    r = subprocess.run([RSCRIPT, "-e", f'''
.libPaths(c("{BASE}/bootstrap/R-library",.libPaths()))
suppressPackageStartupMessages(library(crisprScore))
cat(sprintf("%.6f", getLindelScores("{x}", condaEnv="{LINDEL_ENV}")$score))
'''], capture_output=True, text=True, timeout=600)
    score = float(r.stdout.strip().splitlines()[-1])
    if abs(score - 0.798) > 0.0006:
        raise AssertionError(f"Lindel anchor drifted: {score} vs 0.798")
    return f"documented 65-mer -> {score} (anchor 0.798, tol 6e-4)"


# ---------- T5 off-target controls ----------
def t5():
    short = read_rows("ranked_shortlist.csv")
    gates = {r["candidate_id"]: r for r in read_rows("gate_log.csv")}
    missing = [r["candidate_id"] for r in short
               if not r["intended_hit_count"] or int(r["intended_hit_count"]) < 1]
    if missing:
        raise AssertionError(f"intended locus not recovered: {missing}")
    decoy = "ACGTTGCTAGCTTAACGATC"
    pool_seqs = {r["guide_sequence"] for r in read_rows("candidate_pool.csv")}
    assert decoy not in pool_seqs
    fa = os.path.join(RUN, "reference/decoy.fasta")
    with open(fa, "w") as f:
        f.write(">decoy\n" + decoy + "\n")
    r = subprocess.run([BOWTIE, "-a", "-v", "3", "-f", fa,
                        os.path.join(RUN, "reference/GRCh38.bowtie.idx")],
                       capture_output=True, text=True, timeout=600)
    if r.stdout.strip():
        raise AssertionError(f"decoy matched genome: {r.stdout[:100]}")
    return (f"intended locus recovered {len(short)}/{len(short)}; "
            f"decoy 20-mer -> 0 alignments (positive+negative controls pass)")


# ---------- T6 cross-endpoint sanity ----------
def t6():
    pool = [r for r in read_rows("candidate_pool.csv") if r["activity_status"] == "SCORED"]
    def col(c):
        return [float(r[c]) for r in pool]
    pairs = {("rs1_score", "rs3_seq_hsu2013"): None,
             ("crisprater_score", "rs3_seq_hsu2013"): None,
             ("rs1_score", "crisprater_score"): None}
    out = []
    for a, b in pairs:
        s = spearman(col(a), col(b))
        if not math.isfinite(s):
            raise AssertionError(f"{a} vs {b}: non-finite Spearman (degenerate variance)")
        out.append(f"{a.split('_')[0]}~{b.split('_')[0]}={s:.3f}")
    return "; ".join(out) + " (recorded; no threshold asserted)"


# ---------- T7 gate conformance ----------
def t7():
    short = read_rows("ranked_shortlist.csv")
    if len(short) > 6:
        raise AssertionError(f"panel size {len(short)} > 6")
    for r in short:
        if r["gate_status"] != "PASS":
            raise AssertionError(f"{r['candidate_id']} gate_status={r['gate_status']}")
        if "TTTT" in r["guide_sequence"]:
            raise AssertionError(f"{r['candidate_id']} poly-T in shortlist")
        if int(r["off_target_count_0mm"] or 0) > 0:
            raise AssertionError(f"{r['candidate_id']} has 0mm non-intended off-target")
    ivs = sorted((int(r["start"]), int(r["end"])) for r in short)
    for (s1, e1), (s2, _) in zip(ivs, ivs[1:]):
        if s2 <= e1:
            raise AssertionError("panel sites overlap (site-distinct violated)")
    return (f"{len(short)} guides: all PASS, poly-T-free, 0 exact off-targets, "
            f"site-distinct")


# ---------- T8 provenance ----------
def t8():
    rec1 = json.load(open(os.path.join(RUN, "run_record_stage1.json")))
    rec2 = json.load(open(os.path.join(RUN, "run_record_stage2.json")))
    for rec, keys in ((rec1, ["endpoints", "crisprScore", "rs3_env"]),
                      (rec2, ["weights", "thresholds_version", "bowtie_version"])):
        for k in keys:
            if k not in rec:
                raise AssertionError(f"run record missing {k}")
    for f in ("00_inputs/requirement_brief.json", "00_inputs/thresholds.json"):
        h = hashlib.sha256(open(os.path.join(RUN, f), "rb").read()).hexdigest()
        results.setdefault("hashes", {})[f] = h
    return "engine versions + weights + threshold version recorded; brief+thresholds hashed"


if __name__ == "__main__":
    print(f"Validating executed run: {RUN}")
    for name, fn in [("artifacts", t1), ("coordinate_integrity", t2),
                     ("determinism_rescore", t3), ("lindel_regression_anchor", t4),
                     ("offtarget_controls", t5), ("cross_endpoint_spearman", t6),
                     ("gate_conformance", t7), ("provenance", t8)]:
        check(name, fn)
    with open(os.path.join(RUN, "tests/run_tests.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\n{results['passed']} passed, {results['failed']} failed -> tests/run_tests.json")
    sys.exit(1 if results["failed"] else 0)
