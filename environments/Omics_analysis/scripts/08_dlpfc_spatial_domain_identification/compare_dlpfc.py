#!/usr/bin/env python3
"""Compare an agent's output for dlpfc_spatial_domain_identification with the hidden reference labels
(manual layer annotation of DLPFC sample 151673, Maynard et al. 2021, Nat Neurosci, doi 10.1038/s41593-020-00787-0).
Usage: python3 -I compare_dlpfc.py SPATIAL_DOMAINS.csv DOMAIN_MARKERS.csv ANSWERS.json REPORT.txt HIDDEN_LABELS.csv INPUT.h5ad OUT.json
No weights, no overall score, no pass/fail."""
import sys, re, json, hashlib, platform
import numpy as np, pandas as pd, anndata as ad, sklearn, scipy
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score, homogeneity_completeness_v_measure
from sklearn.neighbors import NearestNeighbors

dom_p, mk_p, ans_p, rep_p, ref_p, h5_p, out_p = sys.argv[1:8]
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
LAYERS = ["Layer_1", "Layer_2", "Layer_3", "Layer_4", "Layer_5", "Layer_6", "WM"]

dom = pd.read_csv(dom_p); mk = pd.read_csv(mk_p); ans = json.load(open(ans_p)); rep = open(rep_p).read()
ref = pd.read_csv(ref_p)
a = ad.read_h5ad(h5_p); xy = pd.DataFrame(a.obsm["spatial"], index=a.obs_names)

ids = {"agent_rows": len(dom), "agent_ids_unique": bool(dom.spot_id.is_unique), "reference_rows": len(ref),
       "input_spots": a.n_obs, "agent_ids_equal_input_ids": set(dom.spot_id) == set(a.obs_names),
       "agent_ids_equal_reference_ids": set(dom.spot_id) == set(ref.spot_id)}
d = dom.merge(ref, on="spot_id", how="inner")
lab = d.dropna(subset=["truth"])

# --- agreement with the reference on labelled spots ---
hom, comp, v = homogeneity_completeness_v_measure(lab.truth, lab.domain_id)
agreement = {"spots_compared": len(lab), "spots_without_reference_label": int(d.truth.isna().sum()),
    "adjusted_rand_index": round(adjusted_rand_score(lab.truth, lab.domain_id), 4),
    "normalized_mutual_information": round(normalized_mutual_info_score(lab.truth, lab.domain_id), 4),
    "homogeneity": round(hom, 4), "completeness": round(comp, 4)}
ct = pd.crosstab(lab.domain_id, lab.truth).reindex(columns=LAYERS, fill_value=0)
contingency = {str(k): {l: int(r[l]) for l in LAYERS} for k, r in ct.iterrows()}

# per agent domain: reference composition
per_domain = {}
for k, r in ct.iterrows():
    n = int(r.sum()); top = r.idxmax()
    per_domain[str(k)] = {"n_labelled_spots": n, "dominant_reference_label": top, "dominant_share": round(r[top] / n, 3),
        "share_in_each_label": {l: round(r[l] / n, 3) for l in LAYERS}}
# per reference label: which agent domain holds most of it
per_label = {}
for l in LAYERS:
    c = ct[l]; per_label[l] = {"n_spots": int(c.sum()), "best_agent_domain": int(c.idxmax()), "share_in_best_domain": round(c.max() / c.sum(), 3)}

# --- spatial coherence (6 nearest spots by coordinate) ---
nn = NearestNeighbors(n_neighbors=7).fit(xy.values); idx = nn.kneighbors(xy.values)[1][:, 1:]
def coh(series):
    v = series.reindex(xy.index).values; ok = pd.notna(v)
    return round(float(np.mean([(v[i] == v[idx[i]]).mean() for i in range(len(v)) if ok[i]])), 4)
coherence = {"agent_6nn_same_domain": coh(d.set_index("spot_id").domain_id), "reference_6nn_same_label": coh(d.set_index("spot_id").truth)}

# --- agent interpretation claims that name a layer, tested against the reference ---
claims = {"2": ("white-matter-like", ["WM"]), "1": ("upper/supragranular-like", ["Layer_1", "Layer_2", "Layer_3"])}
interp = {k: {"agent_claim": name, "reference_labels_counted": labs, "share_of_labelled_spots_in_those_labels":
              round(float(ct.loc[int(k), labs].sum() / ct.loc[int(k)].sum()), 3)} for k, (name, labs) in claims.items()}

# --- markers the paper names for orientation: SNAP25 (gray matter), MOBP (white matter), PCP4 (layer 5) ---
named = {}
for g in ["SNAP25", "MOBP", "PCP4"]:
    s = mk[mk.gene == g]
    named[g] = [{"domain": int(r.domain_id), "rank": int(r["rank"]), "adjusted_p_value": float(r.adjusted_p_value)} for _, r in s.iterrows()]

# --- consistency of the agent's own files ---
sizes = dom.domain_id.value_counts().sort_index()
size_ok = {int(k): int(ans["supporting_evidence"][str(k)]["spatial_metrics"]["spots"]) == int(v) for k, v in sizes.items()}
consistency = {"n_domains_in_answers_equals_csv": ans["n_domains"] == dom.domain_id.nunique(),
    "spots_analyzed_equals_csv_rows": ans["spots_analyzed"] == len(dom),
    "domain_sizes_in_answers_equal_csv": size_ok,
    "reported_6nn_coherence": ans["spatial_coherence"]["six_nearest_neighbor_same_domain_fraction"],
    "recomputed_6nn_coherence": coherence["agent_6nn_same_domain"],
    "marker_rows_per_domain": {str(k): int(v) for k, v in mk.groupby("domain_id").size().items()},
    "marker_columns": list(mk.columns)}

out = {"task_id": "dlpfc_spatial_domain_identification",
 "reference": {"labels_file": "DLPFC_151673_hidden_labels.csv (columns spot_id, truth)",
   "source": "Maynard et al. 2021, Nature Neuroscience, doi 10.1038/s41593-020-00787-0", "sample": "151673",
   "labels": LAYERS, "reference_label_counts": {k: int(v) for k, v in ref.truth.value_counts().items()},
   "spots_without_label": int(ref.truth.isna().sum())},
 "paper_reported": {"design": "12 Visium samples from 3 neurotypical adult donors (two pairs of adjacent sections per donor)",
   "spots_total": 47681, "spots_assigned_to": "six cortical layers or white matter (manual, 'supervised' annotation)",
   "orientation_markers": {"SNAP25": "gray matter / neurons", "MOBP": "white matter / oligodendrocytes", "PCP4": "layer 5"},
   "evaluation_used_in_paper": "adjusted Rand index against the manual layer annotation as gold standard (values are in Figure 7F, not extracted here)"},
 "agent_reported": {"spots_input": ans["spots_input"], "spots_analyzed": ans["spots_analyzed"], "n_domains": ans["n_domains"],
   "domain_interpretations": ans["domain_interpretations"], "domain_markers": ans["domain_markers"],
   "model": ans["model"], "reported_coherence": ans["spatial_coherence"], "limitations": ans["limitations"]},
 "metrics": {"identifiers": ids, "agreement": agreement, "per_agent_domain": per_domain, "per_reference_label": per_label,
   "contingency_agent_domain_by_reference_label": contingency, "spatial_coherence": coherence,
   "interpretation_claims_that_name_a_layer": interp, "paper_named_markers_in_agent_marker_tables": named,
   "agent_file_consistency": consistency},
 "notes": ["The reference is a manual annotation of 7 labels. The agent's number of domains was not fixed, so ARI and NMI are used because they do not need matching labels.",
   "28 spots have no reference label and are left out of the agreement metrics. They are counted in the coherence of the agent's domains.",
   "Domains the agent called 'uncertain' are not scored as errors by these metrics. per_agent_domain shows which reference labels they contain.",
   "The reference is itself a manual annotation, not an independent truth."],
 "provenance": {"inputs_sha256": {"spatial_domains.csv": sha(dom_p), "domain_markers.csv": sha(mk_p), "answers.json": sha(ans_p),
     "analysis_report.txt": sha(rep_p), "hidden_labels.csv": sha(ref_p), "agent_input.h5ad": sha(h5_p)},
   "script_sha256": sha(__file__),
   "scorer": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__, "scipy": scipy.__version__,
              "scikit-learn": sklearn.__version__, "anndata": ad.__version__}}}
json.dump(out, open(out_p, "w"), indent=2)
print(json.dumps({"ids": ids, "agreement": agreement, "coherence": coherence, "interp": interp, "named": named, "consistency": consistency}, indent=1))
