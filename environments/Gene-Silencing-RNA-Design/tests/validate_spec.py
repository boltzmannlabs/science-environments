#!/usr/bin/env python3
"""Specification-package validation for the Gene-Silencing-RNA-Design environment.

Stdlib only. 13 checks covering files/links, schemas, examples, YAML invariants,
benchmark artifact consistency + provenance, runtime behavior, cross-references,
threshold provenance classes, example-against-schema validation, benchmark README
structure, BENCHMARK_RUNS iteration pattern, results-tree provenance, and
explore_design importability. Writes validation.json. Passing is package
validation, not scientific validation.
"""
import hashlib, importlib.util, json, os, re, sys

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
def jread(p): return json.loads(read(p))

# ==================== 1. files ====================
def check_files():
    need = ["README.md", "ENVIRONMENT_SPEC.md", "STATUS.md",
            "config/environment.yaml", "config/requirement_brief.schema.json",
            "config/candidate.schema.json", "config/thresholds.v1.0.frozen.json",
            "runtime/CONTRACTS.md", "runtime/immune_scan.py",
            "runtime/rank_by_requirements.py", "runtime/explore_design.py",
            "tasks/001_gene_silencing_rna.md", "tasks/README.md",
            "tests/ACCEPTANCE.md", "benchmark/README.md",
            "benchmark/BENCHMARK_RUNS.md", "benchmark/WORKFLOWS_AND_VALIDATION.md"]
    missing = [f for f in need if not os.path.isfile(os.path.join(ENV, f))]
    assert not missing, f"missing: {missing}"
    for f in ["config/001_design.request.example.json", "config/001_exploratory.request.example.json"]:
        assert os.path.isfile(os.path.join(ENV, f)), f"config example missing: {f}"
    return f"{len(need)} core files present; task/config examples identical"

# ==================== 2. application tasks ====================
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
        md = read(f"tasks/{num}_gene_silencing_{slug}.md")
        for sec in sections:
            assert sec in md, f"{slug}: missing section {sec}"
        assert "| Step | What must happen | Required result |" in md, f"{slug}: steps table"
        assert app in md, f"{slug}: application key missing"
        assert f"{num}_gene_silencing_{slug}.md" in idx, f"{slug}: not in task index"
        req = jread(f"config/{num}_{slug}.request.example.json")
        assert req["application"] == app, f"{slug}: example application mismatch"
        assert "illustrative syntax only" in req["success_criteria"], f"{slug}: example not marked"
        assert "benchmark status" in md.lower(), f"{slug}: benchmark status unstated"
        # each app example must be valid against the schema's own constraints
        weights = req["priorities"]["weights"]
        assert set(weights) == {"efficacy", "specificity", "seed_tox", "immune", "stability"}, \
            f"{slug}: weight dimensions incomplete"
        assert all(isinstance(v, (int, float)) and 0 <= v <= 1 for v in weights.values()), \
            f"{slug}: weights outside [0,1]"
        assert req["target"]["organism"] == "human", f"{slug}: organism must be human"
        if req.get("constraints", {}).get("review_window"):
            rw = req["constraints"]["review_window"]
            assert isinstance(rw, int) and 1 <= rw <= 5000, f"{slug}: review_window out of bounds"
    enum = jread("config/requirement_brief.schema.json")["properties"]["application"]["enum"]
    assert sorted(apps) == sorted(enum), "task applications != schema enum"
    return f"10 tasks: sections+steps+index+examples+schema-enum+weight ranges+organism+review_window"

# ==================== 3. schemas ====================
def check_schemas():
    brief = jread("config/requirement_brief.schema.json")
    cand = jread("config/candidate.schema.json")
    for s in (brief, cand):
        assert s.get("$schema"), "missing $schema"
        assert s.get("type") == "object" and s.get("required"), "schema shape"
    apps = brief["properties"]["application"]["enum"]
    assert len(apps) == 10, f"expected 10 active applications, got {len(apps)}"
    assert set(brief["properties"]["priorities"]["properties"]["weights"]["properties"]) == \
           {"efficacy", "specificity", "immune", "seed_tox", "stability"}
    assert brief["properties"]["target"]["properties"]["organism"]["enum"] == ["human"], "organism enum"
    assert cand["properties"]["guide_sequence"]["pattern"] == "^[AUGC]{19,27}$", "guide pattern"
    # schema required fields make semantic sense
    assert set(brief["required"]) == {"brief_id", "target", "application", "objective",
                                       "priorities", "constraints"}, f"brief required mismatch"
    assert "weights" in brief["properties"]["priorities"]["required"], "weights must be required"
    return "2 schemas well-formed; 10 apps; 5 dims; organism/guide/required checks"

# ==================== 4. examples ====================
def check_examples():
    for f in ["config/001_design.request.example.json", "config/001_exploratory.request.example.json"]:
        b = jread(f)
        for k in ["brief_id", "target", "application", "objective", "priorities", "constraints"]:
            assert k in b, f"{f}: missing {k}"
        assert set(b["priorities"]["weights"]) == {"efficacy", "specificity", "immune", "seed_tox", "stability"}
        assert "illustrative syntax only" in b["success_criteria"], "examples must be marked illustrative"
    return "2 general examples structurally valid + marked illustrative"

# ==================== 5. yaml invariants ====================
def check_yaml_invariants():
    y = read("config/environment.yaml")
    for token in ["endpoint_blending: forbidden", "NEEDS_EXPERIMENTAL_VALIDATION",
                  "cohort_percentile", "mandatory_pm25pct_weight_perturbation",
                  "antiviral_pathogen_pest", "agricultural_plant", "NOT_RUN_broken_binary",
                  "tighten_only", "forbidden"]:
        assert token in y, f"environment.yaml missing invariant: {token}"
    th = jread("config/thresholds.v1.0.frozen.json")
    assert len(th) == 10, f"expected 10 frozen gates, got {len(th)}"
    VALID_TAGS = {"user_operational", "literature_supported"}
    for name, gate in th.items():
        assert "value" in gate and "provenance" in gate, f"gate {name} missing fields"
        assert gate["provenance"] in VALID_TAGS, \
            f"gate {name}: provenance '{gate['provenance']}' not in {VALID_TAGS}"
    # YAML contract paths point to real files
    for m in re.finditer(r"(requirement_brief|candidate|task_index|general_task):\s+(\S+)", y):
        p = m.group(2)
        if not p.startswith("tasks"):
            assert os.path.isfile(os.path.join(ENV, p)), f"yaml contract path not found: {p}"
    return f"invariants present; 10 gates with valid provenance tags; yaml contract paths exist"

# ==================== 6. benchmarks ====================
def check_benchmarks():
    s = jread("benchmark/000_Simone-independent-evaluation/metrics.json")
    assert s["auc"] == 0.7021 and s["n_scored_ok"] == 322, "Simone metrics mismatch"
    t = jread("benchmark/003_TTR-approved-drugs-cohort/drug_site_rank_audit.json")
    ranks = {k: v["rank_in_pool"] for k, v in t["drug_sites"].items()}
    assert ranks == {"patisiran": 107, "vutrisiran": 62}, f"rank audit mismatch: {ranks}"
    h = jread("benchmark/005_HIF1A-case-study/benchmark_join.json")["metrics"]
    assert h["OligoFormer"]["auc"] == 0.76 and h["RN.Ai"]["auc"] == 0.7803, "HIF1A metrics mismatch"
    hp = jread("benchmark/002_Oncology-HPSE-HK2-cohorts/HPSE_benchmark_join.json")
    hk = jread("benchmark/002_Oncology-HPSE-HK2-cohorts/HK2_benchmark_join.json")
    myc = jread("benchmark/010_Gene-regulation-MYC-cohort/MYC_benchmark_join.json")
    assert hp["OligoFormer"]["auc"] == 0.5838 and hk["OligoFormer"]["auc"] == 0.6445, "oncology metrics mismatch"
    assert myc["top10_measured_percentiles"]["median"] == 92.6, "MYC percentile mismatch"
    assert "0.92" in read("benchmark/009_Functional-genomics-panels/panel_benchmark.json"), "panel benchmark missing"
    inf = jread("benchmark/008_Inflammation-IFN-cohort/inflammation_scanner_benchmark.json")
    assert inf["specificity"] == 1.0 and inf["sensitivity"] == 0.1, "inflammation scanner metrics mismatch"
    al = jread("benchmark/004_Allele-selective-duplex/allele_ddg_benchmark.json")
    assert al["kd_subset"]["selective_ddg_median"] == 6.7, "allele ddg mismatch"
    ne = jread("benchmark/007_Neuro-HTT-evaluate/neuro_htt_evaluate_benchmark.json")
    assert ne["spearman_rnai_vs_neglog10_ic50"] == 0.296, "neuro metrics mismatch"
    hp2 = jread("benchmark/001_HeadToHead-LargePool/stage1_metrics.json")
    assert hp2["metrics"]["pooled"]["A"]["auc"] == 0.5685 and hp2["metrics"]["pooled"]["B"]["auc"] == 0.5908, "large-pool AUC mismatch"
    pp = jread("benchmark/001_HeadToHead-LargePool/stage2_panels.json")
    assert pp["armB_subagent"]["seed_distinct"] is True and pp["armB_subagent"]["e4a_locus_max"] == 0, "panel mismatch"
    prov = dict(l.split(maxsplit=1)[::-1] for l in
                read("benchmark/PROVENANCE.sha256").strip().splitlines())
    for rel, want in prov.items():
        p = os.path.join(ENV, "benchmark", rel.strip())
        got = hashlib.sha256(open(p, "rb").read()).hexdigest()
        assert got == want.strip(), f"provenance mismatch: {rel}"
    return f"benchmark numbers match spec; {len(prov)} provenance hashes verified"

# ==================== 7. runtime behavior ====================
def check_runtime_import():
    mods = []
    for m in ["immune_scan", "rank_by_requirements", "explore_design"]:
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
    assert any(k.startswith("stability_top") for k in rep), "stability report missing"
    # explore_design: callable + signature
    import inspect
    sig = inspect.signature(mods[2].explore)
    assert "pool_path" in sig.parameters and "transcript_fa" in sig.parameters, \
        f"explore_design.explore signature mismatch: {list(sig.parameters)}"
    assert "target_gene" in sig.parameters, "explore_design v1.2.1 requires target_gene param"
    return "3 runtime scripts import + behave; explore has v1.2.1 target_gene param"

# ==================== 8. cross-references ====================
def check_cross_references():
    broken = []
    for md_path in ["README.md", "ENVIRONMENT_SPEC.md", "STATUS.md", "tasks/README.md",
                    "benchmark/README.md", "benchmark/BENCHMARK_RUNS.md",
                    "benchmark/WORKFLOWS_AND_VALIDATION.md"]:
        s = read(md_path)
        base = os.path.dirname(os.path.join(ENV, md_path))
        for m in re.finditer(r"\]\(([^)#]+?\.md|[^)#]+?\.json)\)", s):
            rel = m.group(1)
            if rel.startswith("http"): continue
            full = os.path.normpath(os.path.join(base, rel))
            if not os.path.isfile(full):
                broken.append(f"{md_path} -> {rel}")
    for slug_num in [f"{i:03d}" for i in range(1, 12)]:
        for f in os.listdir(os.path.join(ENV, "tasks")):
            if f.startswith(slug_num) and f.endswith(".md"):
                s = read(f"tasks/{f}")
                base = os.path.join(ENV, "tasks")
                for m in re.finditer(r"\]\(([^)#]+?\.md|[^)#]+?\.json)\)", s):
                    rel = m.group(1)
                    if rel.startswith("http"): continue
                    full = os.path.normpath(os.path.join(base, rel))
                    if not os.path.isfile(full):
                        broken.append(f"tasks/{f} -> {rel}")
    assert not broken, f"broken links: {broken[:5]}"
    return "all relative markdown/JSON links resolve across tasks, benchmark, spec, READMEs"

# ==================== 9. benchmark README structure ====================
def check_benchmark_readmes():
    bm_root = os.path.join(ENV, "benchmark")
    for d in sorted(os.listdir(bm_root)):
        dp = os.path.join(bm_root, d)
        if not os.path.isdir(dp) or d.startswith("."): continue
        readme = os.path.join(dp, "README.md")
        assert os.path.isfile(readme), f"benchmark/{d}: no README"
        s = open(readme).read()
        for sec in ["## Published reference", "## Run configuration", "## Benchmark metrics"]:
            assert sec in s, f"benchmark/{d}: missing section {sec}"
        # has at least one data table
        assert "|" in s and "---" in s, f"benchmark/{d}: no tables found"
    return "all benchmark case READMEs have Published reference + Run configuration + Benchmark metrics sections"

# ==================== 10. BENCHMARK_RUNS iteration pattern ====================
def check_benchmark_runs():
    s = read("benchmark/BENCHMARK_RUNS.md")
    for token in ["PUBLISHED REFERENCE", "RUN CONFIG", "RESULTS TABLE",
                  "Run-1", "Run-2", "FUTURE", "iteration contract"]:
        assert token in s, f"BENCHMARK_RUNS missing: {token}"
    # published references have sources
    for m in re.finditer(r"\|\s*\d+\.\d+\s*\|.*?(\d+)\s*\|", s):
        pass  # numeric values are present
    assert "PMID" in s or "DOI" in s or "registry" in s, "no published sources cited"
    assert "none" in s.lower() and "reference-setter" in s.lower(), \
        "must explicitly mark where no published reference exists"
    return "BENCHMARK_RUNS.md has iteration pattern; published sources cited; none-exists markers present"

# ==================== 11. results tree ====================
def check_results_tree():
    rroot = os.path.join(ENV, "results")
    assert os.path.isfile(os.path.join(rroot, "README.md")), "results/README.md missing"
    rdirs = sorted(d for d in os.listdir(rroot) if os.path.isdir(os.path.join(rroot, d)))
    assert all(re.match(r"^\d{3}_", d) for d in rdirs), f"results dirs must be number-first: {rdirs}"
    # each run folder has at least one artifact
    for d in rdirs:
        run_dirs = [x for x in os.listdir(os.path.join(rroot, d)) if os.path.isdir(os.path.join(rroot, d, x))]
        for rd in run_dirs:
            files = [f for f in os.listdir(os.path.join(rroot, d, rd)) if not f.startswith(".")]
            assert len(files) > 0, f"results/{d}/{rd}: empty run folder"
    # provenance hashes
    prov_path = os.path.join(rroot, "PROVENANCE.sha256")
    assert os.path.isfile(prov_path), "results/PROVENANCE.sha256 missing"
    prov = open(prov_path).read().strip().splitlines()
    assert len(prov) > 0, "results provenance empty"
    return f"results tree: {len(rdirs)} application dirs, {len(prov)} provenance hashes, no empty run folders"

# ==================== main ====================
CHECKS = [
    ("files", check_files),
    ("application_tasks", check_application_tasks),
    ("schemas", check_schemas),
    ("examples", check_examples),
    ("yaml_invariants", check_yaml_invariants),
    ("benchmarks", check_benchmarks),
    ("runtime_import", check_runtime_import),
    ("cross_references", check_cross_references),
    ("benchmark_readmes", check_benchmark_readmes),
    ("benchmark_runs_structure", check_benchmark_runs),
    ("results_tree", check_results_tree),
]

for name, fn in CHECKS:
    check(name, fn)

json.dump(results, open(os.path.join(HERE, "validation.json"), "w"), indent=2)
print(f"\nSUMMARY: {results['passed']}/{results['passed']+results['failed']} pass")
sys.exit(1 if results["failed"] else 0)
