#!/usr/bin/env python3
"""Requirement-aware ranking (protocol v1.1 §3): brief -> vetoes -> weighted cohort-percentile
ordering -> sensitivity (weight perturbation) -> seed-distinct panel.

Input: candidates CSV with battery dimensions + a brief JSON (schema in
references/requirements_and_ranking.md). Output: ranked CSV + JSON report.
Demo briefs + data live in 09_requirement_ranking_demo/.
"""
import argparse, csv, json, sys

DIM_MAP = {  # dimension -> (column, direction +1 good/-1 bad)
    "efficacy":   ("eff_RN.Ai-Predict", +1),     # primary efficacy endpoint (brief may switch to E2b)
    "specificity":("pots_seed_percentile", -1),   # specificity proxy: lower off-target propensity
    "seed_tox":   ("seed_tox_viability_avg_human", +1),
    "stability":  ("guide_target_duplex_delta_g_kcal_mol", -1),  # more negative = more stable duplex
}

def load_candidates(path):
    rows = list(csv.DictReader(open(path)))
    for r in rows:
        for col, _ in DIM_MAP.values():
            if r.get(col) not in (None, "", "None"):
                r[col] = float(r[col])
    return rows

def pct_rank(vals):
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    out = [0.0] * len(vals)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]: j += 1
        for k in range(i, j + 1): out[order[k]] = (i + j) / 2 / max(1, len(vals) - 1)
        i = j + 1
    return out

def normalized_dims(rows):
    norm = {}
    for dim, (col, sgn) in DIM_MAP.items():
        vals = [r.get(col) for r in rows]
        if any(v is None for v in vals):
            norm[dim] = None; continue
        pr = pct_rank(vals)
        norm[dim] = [pr[i] if sgn > 0 else 1 - pr[i] for i in range(len(rows))]
    return norm

def score_and_rank(rows, norm, weights):
    S = []
    for i in range(len(rows)):
        s = 0.0
        for dim, w in weights.items():
            if norm.get(dim) is None or w <= 0: continue
            s += w * norm[dim][i]
        S.append(round(s, 4))
    order = sorted(range(len(rows)), key=lambda i: -S[i])
    ranks = [0] * len(rows)
    for rk, i in enumerate(order, 1): ranks[i] = rk
    return S, ranks

def apply_vetoes(rows, brief, immune_flags):
    keep, veto_log = [], []
    for i, r in enumerate(rows):
        ok = True
        for v in brief.get("priorities", {}).get("hard_vetoes", []):
            if v == "immune_ugugu" and immune_flags[i]["guide"]["UGUGU_tlr7"]:
                ok = False; veto_log.append((r.get("candidate_id", i), v))
        mins = brief.get("priorities", {}).get("min_standards", {})
        if "rnai" in mins and r.get("eff_RN.Ai-Predict") is not None and r["eff_RN.Ai-Predict"] < mins["rnai"]:
            ok = False; veto_log.append((r.get("candidate_id", i), f"rnai<{mins['rnai']}"))
        if ok: keep.append(i)
    return keep, veto_log

def jaccard(a, b):
    a, b = set(a), set(b)
    return round(len(a & b) / len(a | b), 3) if a | b else 1.0

def run(rows, brief, immune_flags, label):
    keep, vetoes = apply_vetoes(rows, brief, immune_flags)
    kept = [rows[i] for i in keep]
    kept_flags = [immune_flags[i] for i in keep]
    norm = normalized_dims(kept)
    w = brief["priorities"]["weights"]
    S, ranks = score_and_rank(kept, norm, w)
    k = brief.get("constraints", {}).get("panel_size", 6)
    top = sorted(range(len(kept)), key=lambda i: ranks[i])[:k]
    # sensitivity: +-25% per weight + equal weights
    sens = {}
    for dim in w:
        for sgn in (+1, -1):
            w2 = dict(w); w2[dim] = round(max(0.0, w[dim] + sgn * 0.25 * w[dim]), 4)
            _, r2 = score_and_rank(kept, norm, w2)
            top2 = sorted(range(len(kept)), key=lambda i: r2[i])[:k]
            sens[f"{dim}{'+25%' if sgn>0 else '-25%'}"] = jaccard([kept[i].get('candidate_id', i) for i in top],
                                                                  [kept[i].get('candidate_id', i) for i in top2])
    w_eq = {d: 1.0 for d in w}
    _, r_eq = score_and_rank(kept, norm, w_eq)
    top_eq = sorted(range(len(kept)), key=lambda i: r_eq[i])[:k]
    sens["equal_weights"] = jaccard([kept[i].get('candidate_id', i) for i in top],
                                    [kept[i].get('candidate_id', i) for i in top_eq])
    panel = []
    seen = set()
    for i in sorted(range(len(kept)), key=lambda i: ranks[i]):
        if not brief.get("constraints", {}).get("seed_distinct", True): pass
        elif kept[i].get("guide_sequence") and kept[i]["guide_sequence"][1:8] in seen: continue
        seen.add(kept[i].get("guide_sequence", "")[1:8])
        panel.append({"candidate_id": kept[i].get("candidate_id"), "S": S[i],
                      "guide": kept[i].get("guide") or kept[i].get("guide_sequence"),
                      "seed": (kept[i].get("guide") or kept[i].get("guide_sequence") or "")[1:8]})
        if len(panel) >= k: break
    return {"brief_label": label, "n_input": len(rows), "n_after_vetoes": len(kept),
            "vetoes": vetoes, "weights": w, "panel": panel,
            "stability_top{}_jaccard".format(k): sens,
            "disclosure": "S is a preference ordering under the stated weights for review triage; "
                          "not an efficacy estimate; not comparable across briefs."}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidates", required=True)
    ap.add_argument("--brief", required=True, help="JSON brief or @file with JSON")
    ap.add_argument("--immune", help="immune flags JSON list (from immune_scan cohort mode)")
    ap.add_argument("--label", default="brief")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    rows = load_candidates(a.candidates)
    brief = json.load(open(a.brief.lstrip("@"))) if a.brief.startswith("@") else json.loads(a.brief)
    if a.immune:
        flags = json.load(open(a.immune))
    else:
        sys.path.insert(0, __file__.rsplit("/", 1)[0])
        from immune_scan import scan
        flags = [scan(r.get("guide") or r.get("guide_sequence")) for r in rows]
    rep = run(rows, brief, flags, a.label)
    out = a.out or f"ranking_{a.label}.json"
    json.dump(rep, open(out, "w"), indent=2)
    print(json.dumps(rep, indent=2))

if __name__ == "__main__":
    main()
