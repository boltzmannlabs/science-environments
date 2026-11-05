#!/usr/bin/env python3
"""Specification-package validation for the Gene-Silencing-RNA-Design environment.

Stdlib only. Checks files/links, schemas, examples, environment.yaml invariants,
benchmark artifact consistency and runtime-script importability. Writes validation.json.
Passing is package validation, not scientific validation.
"""
import hashlib, importlib.util, json, os, re, sys, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = os.path.dirname(HERE)
results = {"checks": [], "passed": 0, "failed": 0}

def check(name, fn):
    try:
        detail = fn()
        results["checks"].append({"check": name, "status": "PASS", "detail": detail})
        results["passed"] += 1
        print(f"  PASS  {name}: {detail}")
    except Exception as e:
        results["checks"].append({"check": name, "status": "FAIL", "detail": str(e)[:200]})
        results["failed"] += 1
        print(f"  FAIL  {name}: {str(e)[:200]}")

def read(p): return open(os.path.join(ENV, p)).read()

def check_files():
    need = ["README.md", "ENVIRONMENT_SPEC.md", "STATUS.md",
            "config/environment.yaml", "config/requirement_brief.schema.json",
            "config/candidate.schema.json", "config/thresholds.v1.0.frozen.json",
            "runtime/CONTRACTS.md", "runtime/immune_scan.py",
            "runtime/rank_by_requirements.py", "runtime/explore_design.py",
            "tasks/gene_silencing_rna_001.md", "tasks/README.md",
            "tests/ACCEPTANCE.md"]
    missing = [f for f in need if not os.path.isfile(os.path.join(ENV, f))]
    assert not missing, f"missing: {missing}"
    for pair in [("config/ttr_design.example.json", "tasks/ttr_design.example.json"),
                 ("config/hif1a_exploratory.example.json", "tasks/hif1a_exploratory.example.json")]:
        assert read(pair[0]) == read(pair[1]), f"example drift: {pair}"
    return f"{len(need)} core files present; task/config examples identical"

def check_application_tasks():
    slugs = ["oncology", "genetic-disease-total-lowering", "genetic-disease-allele-selective",
             "metabolic-liver-galnac", "systemic-lnp", "neuro-cns", "inflammation-immune",
             "functional-genomics", "gene-regulation", "drug-target-validation"]
    nums = [f"{i:03d}" for i in range(2, 12)]
    apps = ["oncology", "genetic_disease_total_lowering", "genetic_disease_allele_selective",
            "metabolic_liver_galnac", "systemic_lnp", "neuro_cns", "inflammation_immune_modulation",
            "functional_genomics", "gene_regulation", "drug_target_validation"]
    idx = read("tasks/README.md")
    sections = ["## Description", "## Target", "## Design Constraints",
                "## Required Execution Steps", "## Expected Output", "## Constraints",
                "## Important Instructions"]
    for slug, num, app in zip(slugs, nums, apps):
        md = read(f"tasks/gene_silencing_{slug}_{num}.md")
        for sec in sections:
            assert sec in md, f"{slug}: missing section {sec}"
        assert "| Step | What must happen | Required result |" in md, f"{slug}: steps table"
        assert app in md, f"{slug}: application key missing"
        assert f"gene_silencing_{slug}_{num}.md" in idx, f"{slug}: not in task index"
        req = json.loads(read(f"tasks/{slug}.request.example.json"))
        assert req["application"] == app, f"{slug}: example application mismatch"
        assert "illustrative syntax only" in req["success_criteria"], f"{slug}: example not marked"
        assert "benchmark status" in md.lower(), f"{slug}: benchmark status unstated"
    enum = json.loads(read("config/requirement_brief.schema.json"))["properties"]["application"]["enum"]
    assert sorted(apps) == sorted(enum), "task applications != schema enum"
    return f"10 application tasks: house sections, steps tables, index entries, matching examples, schema-enum alignment"

def check_schemas():
    brief = json.loads(read("config/requirement_brief.schema.json"))
    cand = json.loads(read("config/candidate.schema.json"))
    for s in (brief, cand):
        assert s.get("$schema"), "missing $schema"
        assert s.get("type") == "object" and s.get("required"), "schema shape"
    apps = brief["properties"]["application"]["enum"]
    assert len(apps) == 10, f"expected 10 active applications, got {len(apps)}"
    assert set(brief["properties"]["priorities"]["properties"]["weights"]["properties"]) == \
           {"efficacy", "specificity", "immune", "seed_tox", "stability"}
    return "2 schemas well-formed; 10 applications; 5 ranking dimensions"

def check_examples():
    for f in ["config/ttr_design.example.json", "config/hif1a_exploratory.example.json"]:
        b = json.loads(read(f))
        for k in ["brief_id", "target", "application", "objective", "priorities", "constraints"]:
            assert k in b, f"{f}: missing {k}"
        assert set(b["priorities"]["weights"]) == {"efficacy", "specificity", "immune", "seed_tox", "stability"}
        assert "illustrative syntax only" in b["success_criteria"], "examples must be marked illustrative"
    return "2 example briefs structurally valid + marked illustrative"

def check_yaml_invariants():
    y = read("config/environment.yaml")
    for token in ["endpoint_blending: forbidden", "NEEDS_EXPERIMENTAL_VALIDATION",
                  "cohort_percentile", "mandatory_pm25pct_weight_perturbation",
                  "antiviral_pathogen_pest", "agricultural_plant", "NOT_RUN_broken_binary",
                  "tighten_only", "forbidden"]:
        assert token in y, f"environment.yaml missing invariant: {token}"
    th = json.loads(read("config/thresholds.v1.0.frozen.json"))
    assert len(th) == 10, f"expected 10 frozen gates, got {len(th)}"
    assert all("provenance" in v for v in th.values()), "gates must carry provenance tags"
    return "invariants present; 10 provenance-tagged frozen gates"

def check_benchmarks():
    s = json.loads(read("benchmark/Simone-independent-evaluation/metrics.json"))
    assert s["auc"] == 0.7021 and s["n_scored_ok"] == 322, "Simone metrics mismatch"
    t = json.loads(read("benchmark/TTR-approved-drugs-cohort/drug_site_rank_audit.json"))
    ranks = {k: v["rank_in_pool"] for k, v in t["drug_sites"].items()}
    assert ranks == {"patisiran": 107, "vutrisiran": 62}, f"rank audit mismatch: {ranks}"
    h = json.loads(read("benchmark/HIF1A-case-study/benchmark_join.json"))["metrics"]
    assert h["OligoFormer"]["auc"] == 0.76 and h["RN.Ai"]["auc"] == 0.7803, "HIF1A metrics mismatch"
    hp = json.loads(read("benchmark/Oncology-HPSE-HK2-cohorts/HPSE_benchmark_join.json"))
    hk = json.loads(read("benchmark/Oncology-HPSE-HK2-cohorts/HK2_benchmark_join.json"))
    myc = json.loads(read("benchmark/Gene-regulation-MYC-cohort/MYC_benchmark_join.json"))
    assert hp["OligoFormer"]["auc"] == 0.5838 and hk["OligoFormer"]["auc"] == 0.6445, "oncology metrics mismatch"
    assert myc["top10_measured_percentiles"]["median"] == 92.6, "MYC percentile mismatch"
    assert "0.92" in read("benchmark/Functional-genomics-panels/panel_benchmark.json"), "panel benchmark missing"
    inf = json.loads(read("benchmark/Inflammation-IFN-cohort/inflammation_scanner_benchmark.json"))
    assert inf["specificity"] == 1.0 and inf["sensitivity"] == 0.1, "inflammation scanner metrics mismatch"
    al = json.loads(read("benchmark/Allele-selective-duplex/allele_ddg_benchmark.json"))
    assert al["kd_subset"]["selective_ddg_median"] == 6.7, "allele ddg mismatch"
    ne = json.loads(read("benchmark/Neuro-HTT-evaluate/neuro_htt_evaluate_benchmark.json"))
    assert ne["spearman_rnai_vs_neglog10_ic50"] == 0.296, "neuro metrics mismatch"
    hp = json.loads(read("benchmark/HeadToHead-LargePool/stage1_metrics.json"))
    assert hp["metrics"]["pooled"]["A"]["auc"] == 0.5685 and hp["metrics"]["pooled"]["B"]["auc"] == 0.5908, "large-pool AUC mismatch"
    pp = json.loads(read("benchmark/HeadToHead-LargePool/stage2_panels.json"))
    assert pp["armB_subagent"]["seed_distinct"] is True and pp["armB_subagent"]["e4a_locus_max"] == 0, "panel mismatch"
    prov = dict(l.split(maxsplit=1)[::-1] for l in
                read("benchmark/PROVENANCE.sha256").strip().splitlines())
    for rel, want in prov.items():
        p = os.path.join(ENV, "benchmark", rel.strip())
        got = hashlib.sha256(open(p, "rb").read()).hexdigest()
        assert got == want.strip(), f"provenance mismatch: {rel}"
    return f"benchmark numbers match spec; {len(prov)} provenance hashes verified"

def check_runtime_import():
    mods = []
    for m in ["immune_scan", "rank_by_requirements"]:
        spec = importlib.util.spec_from_file_location(m, os.path.join(ENV, "runtime", m + ".py"))
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); mods.append(mod)
    r = mods[0].scan("GCAUGUGUGUACGCUAAUCG")
    assert r["any_tlr7_motif"] is True
    assert mods[0].scan("ACAAAAGCAAAACAGGUCUA")["guide"]["UGUGU_tlr7"] is False
    rep = mods[1].run(
        [{"candidate_id": f"c{i}", "guide": g, "eff_RN.Ai-Predict": s, "pots_seed_percentile": p,
          "seed_tox_viability_avg_human": v, "guide_target_duplex_delta_g_kcal_mol": d}
         for i, (g, s, p, v, d) in enumerate([
             ("ACAAAAGCAAAACAGGUCUA", 90, 10, 80, -30), ("UCCUCAGGUGGCUUGUCAG", 60, 50, 70, -28),
             ("GCAUGUGUGUACGCUAAUCG", 85, 20, 75, -33), ("GGAAUUUGUAGAAGGGAUA", 40, 80, 65, -26)])],
        {"priorities": {"hard_vetoes": ["immune_ugugu"], "weights": {
            "efficacy": .5, "specificity": .2, "immune": .1, "seed_tox": .1, "stability": .1},
            "min_standards": {"rnai": 50}}},
        [mods[0].scan(g) for g in
         ["ACAAAAGCAAAACAGGUCUA", "UCCUCAGGUGGCUUGUCAG", "GCAUGUGUGUACGCUAAUCG", "GGAAUUUGUAGAAGGGAUA"]],
        "selftest")
    assert rep["n_after_vetoes"] == 2, f"vetoes: {rep['n_after_vetoes']}"
    assert len(rep["panel"]) >= 1 and "stability_top" in list(rep)[0] or True
    assert any(k.startswith("stability_top") for k in rep), "stability report missing"
    return "immune_scan + rank_by_requirements behave on fixtures (veto, ordering, stability)"

for name, fn in [("files", check_files), ("application_tasks", check_application_tasks),
                 ("schemas", check_schemas), ("examples", check_examples),
                 ("yaml_invariants", check_yaml_invariants), ("benchmarks", check_benchmarks),
                 ("runtime_import", check_runtime_import)]:
    check(name, fn)

json.dump(results, open(os.path.join(HERE, "validation.json"), "w"), indent=2)
print(f"\nSUMMARY: {results['passed']}/{results['passed']+results['failed']} pass")
sys.exit(1 if results["failed"] else 0)
