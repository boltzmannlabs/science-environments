#!/usr/bin/env python3
"""Explorer mode (protocol v1.2): multi-strategy, adaptive design-space exploration.

For users who supply a TARGET (and little else). Instead of one linear pass:
  X1 strategy partition   model-led | rule-led | property-envelope sweep | diversity-led
  X2 cheap funnel         immune + GC + POTS + 6merDB vetoes on the union
  X3 tiered gate descent  walk ranked tiers evaluating the expensive off-target screen
                          until the panel quota fills (adaptively escapes saturated tiers)
  X4 brief-variant search rank survivors under safety/balanced/efficacy briefs ->
                          consensus vs divergence across requirement hypotheses
  X5 synthesis            Pareto front, consensus panel, PROPOSED brief for user confirmation

Selection never touches measured/published outcomes; benchmarks join labels post-hoc only.
Run under siRNA-Bench .venv with biotools on PATH.
"""
import argparse, csv, json, os, sys

BASE = "/home/boltzmann13/IMRAN/OCT26/siRNA-Bench"
sys.path.insert(0, f"{BASE}/src")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sirna_bench.adapters.offtarget import annotate_seed_pots, full_length_hits
from sirna_bench.adapters import seed_toxicity
from sirna_bench.adapters.efficacy import RnAiPredictAdapter
from immune_scan import scan as immune_scan
from rank_by_requirements import run as rank_run

def rc(s): return s.translate(str.maketrans("AUCG", "UAGC"))[::-1]

def rule_score(g):
    """Classical-feature composite (disclosed heuristics; not a published rule set)."""
    gc = (g.count("G") + g.count("C")) / len(g)
    s = 0.0
    s += 1.0 if 0.30 <= gc <= 0.52 else (0.4 if 0.30 <= gc <= 0.70 else 0.0)     # GC preference
    s += 0.5 if g[18] in "AU" else 0.0                                            # antisense 3' A/U偏好 proxy
    s -= 0.5 if any(b * 4 in g for b in "AUCG") else 0.0                          # homopolymer penalty
    s += 0.3 if len(set(g[i:i+7] for i in range(0, 3))) > 1 else 0.0              # trivial diversity guard
    return round(s, 3)

def explore(pool_path, transcript_fa, panel_size=6, tier_cap=60, verbose=True, target_gene=None):
    pool = list(csv.DictReader(open(pool_path)))
    for p in pool: p["score"] = float(p["oligoformer_native_score"])
    pool.sort(key=lambda r: -r["score"])
    N = len(pool)

    # X1 strategies
    S = {}
    S["model_led"] = pool[:200]
    S["rule_led"] = sorted(pool, key=lambda r: -rule_score(r["guide_sequence"]))[:200]
    # property-envelope sweep: GC in {0.30-0.45, 0.40-0.55, 0.45-0.60} x duplex band windows are
    # approximated post-hoc on the union via dimension values; sweep partitions by GC envelope
    for i, (lo, hi) in enumerate([(0.30, 0.45), (0.40, 0.55), (0.45, 0.60)]):
        S[f"sweep_gc{lo}-{hi}"] = [r for r in pool
                                   if lo <= (r["guide_sequence"].count("G")+r["guide_sequence"].count("C"))/19 <= hi][:150]
    # diversity-led: greedy site-spread over mid-tier (ranks 200-1200) — the region linear runs underuse
    mid = pool[200:1200]
    div, last = [], -10**9
    for r in mid:
        if abs(int(r["target_start"]) - last) >= 60:
            div.append(r); last = int(r["target_start"])
        if len(div) >= 150: break
    S["diversity_led"] = div
    union, seen = [], set()
    for k, rows in S.items():
        for r in rows:
            key = r["candidate_id"]
            if key not in seen:
                seen.add(key); r["_strategy"] = k; union.append(r)
    if verbose: print(f"X1 strategies: {[(k, len(v)) for k, v in S.items()]} -> union {len(union)}")

    # X2 cheap funnel
    survivors = []
    for r in union:
        g = r["guide_sequence"]
        gc = (g.count("G") + g.count("C")) / len(g)
        if not (0.30 <= gc <= 0.70): continue
        imm = immune_scan(g)["guide"]
        if imm["UGUGU_tlr7"]: continue
        pots = annotate_seed_pots(g).pots_percentile
        if pots is None or pots > 90: continue
        via = seed_toxicity.lookup("x", g).viability
        if via is None or via < 50: continue
        r.update({"gc": round(gc, 3), "pots": round(pots, 2), "viability": round(via, 2)})
        survivors.append(r)
    if verbose: print(f"X2 cheap funnel: {len(survivors)} survivors")

    # X3 tiered gate descent on the expensive screen (off-target <= 10)
    survivors.sort(key=lambda r: -r["score"])
    clean, evaluated = [], 0
    for r in survivors:
        if len(clean) >= max(panel_size * 3, 18): break
        if evaluated >= tier_cap: break
        hits = len([h for h in full_length_hits(r["guide_sequence"], None, target_gene=target_gene)
                    if not h.is_intended_target])  # v1.2.1: locus-scoped E4a (scope-explicit)
        evaluated += 1
        r["full_len_hits"] = hits
        if hits <= 10: clean.append(r)
    if verbose: print(f"X3 tiered descent: {evaluated} expensive screens -> {len(clean)} gate-clean "
                      f"(tier escape: clean found at rank-depth {clean[0]['score'] if clean else 'NONE'})")

    # X3b adaptive constraint re-anchoring (disclosed; PROPOSED — user confirms):
    # if the absolute gate is unsatisfiable within budget, characterize THIS target's hit
    # distribution on a stratified sample and re-anchor the constraint cohort-relative
    # (lowest quartile of the target's own distribution) — v1.1 percentile principle.
    adaptation = None
    if len(clean) == 0 and survivors:
        K = min(40, len(survivors))
        step = max(1, len(survivors) // K)
        sample = survivors[::step][:K]
        shits = [len([h for h in full_length_hits(r["guide_sequence"], None, target_gene=target_gene) if not h.is_intended_target]) for r in sample]
        evaluated += len(shits)
        for r, h in zip(sample, shits): r["full_len_hits"] = h
        srt = sorted(shits)
        q25 = srt[len(srt)//4]; med = srt[len(srt)//2]
        adaptation = {
            "original_constraint": "full_length_offtarget_hits <= 10 (frozen gate)",
            "diagnosis": f"saturated for this target: stratified sample n={len(shits)} "
                         f"min={srt[0]} q25={q25} median={med} max={srt[-1]} — absolute cap unreachable",
            "re_anchored_constraint": f"cohort-relative: hits <= q25 of target's own distribution ({q25})",
            "status": "PROPOSED constraint adaptation — requires user confirmation; frozen gate NOT changed",
        }
        for r in survivors:
            if len(clean) >= max(panel_size * 3, 18) or evaluated >= tier_cap + 80: break
            if r.get("full_len_hits") is None:
                r["full_len_hits"] = len([h for h in full_length_hits(r["guide_sequence"], None, target_gene=target_gene) if not h.is_intended_target])
                evaluated += 1
            if r["full_len_hits"] <= q25 and r not in clean:
                r["rel_gate_only"] = True
                clean.append(r)
        if verbose: print(f"X3b re-anchored descent (q25={q25}): total screens {evaluated} -> {len(clean)} relatively-clean")

    # X4 brief-variant ranking (3 requirement hypotheses)
    seq = "".join(l.strip() for l in open(transcript_fa) if not l.startswith(">")).replace("T", "U")
    ad = RnAiPredictAdapter()
    for r in clean:
        i = int(r["target_start"]) - 1
        ctx = seq[max(0, i-19): i+19+19]
        r["eff_RN.Ai-Predict"] = ad.predict_pair(r["guide_sequence"], ctx).raw_score
        r["seed_tox_viability_avg_human"] = r["viability"]
        r["pots_seed_percentile"] = r["pots"]
    flags = [immune_scan(r["guide_sequence"]) for r in clean]
    briefs = {
      "safety_first":  {"weights": {"efficacy": .30, "specificity": .25, "immune": .30, "seed_tox": .10, "stability": .05}},
      "balanced":      {"weights": {"efficacy": .35, "specificity": .25, "immune": .15, "seed_tox": .15, "stability": .10}},
      "efficacy_first": {"weights": {"efficacy": .55, "specificity": .15, "immune": .05, "seed_tox": .10, "stability": .15}},
    }
    variants = {}
    for name, w in briefs.items():
        b = {"priorities": {"hard_vetoes": ["immune_ugugu"], "weights": w["weights"], "min_standards": {}},
             "constraints": {"panel_size": panel_size, "seed_distinct": True}}
        variants[name] = rank_run(clean, b, flags, name)
    panels = {n: [m["candidate_id"] for m in v["panel"]] for n, v in variants.items()}
    from collections import Counter
    tally = Counter(c for p in panels.values() for c in p)
    consensus = [c for c, t in tally.items() if t >= 2]

    # X5 Pareto front (efficacy vs specificity proxy) on clean set
    pts = sorted(clean, key=lambda r: -(r.get("eff_RN.Ai-Predict") or 0))
    front, best_pots = [], -1
    for r in pts:  # maximize efficacy, then keep only pots improvements
        if r["pots"] < best_pots or best_pots == -1:
            front.append(r["candidate_id"]); best_pots = r["pots"]
    return {"strategies": {k: len(v) for k, v in S.items()}, "union": len(union),
            "survivors_x2": len(survivors), "expensive_screens": evaluated,
            "gate_clean": len(clean), "constraint_adaptation": adaptation,
            "brief_variant_panels": panels,
            "consensus_panel": consensus,
            "pareto_front_efficacy_vs_pots": front[:10],
            "proposed_brief": "balanced (see brief_variant stability; confirm with user)",
            "clean_candidates": clean, "variants": variants}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", required=True, help="generation all_ranked_candidates.csv")
    ap.add_argument("--transcript", required=True, help="RNA transcript FASTA")
    ap.add_argument("--out", required=True)
    ap.add_argument("--target-gene", default=None, help="gene symbol for locus-scoped E4a (v1.2.1); REQUIRED for correct off-target semantics — warn if omitted")
    a = ap.parse_args()
    if a.target_gene is None:
        print("WARNING (v1.2.1): --target-gene omitted; E4a will count SAME-GENE isoform hits as off-targets (scope loss).", file=sys.stderr)
    rep = explore(a.pool, a.transcript, target_gene=a.target_gene)
    json.dump(rep, open(a.out, "w"), indent=2)
    print(json.dumps({k: v for k, v in rep.items() if k not in ("clean_candidates", "variants")}, indent=2))
