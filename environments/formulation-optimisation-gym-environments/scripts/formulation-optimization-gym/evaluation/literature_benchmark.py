"""Unfitted one-endpoint literature sanity check; never a holdout validation."""
import argparse
import json
import math
from pathlib import Path


def benchmark(result: dict) -> dict:
    label = result.get("status", "")
    if not label.startswith("exploratory_assumption_conditional"):
        raise ValueError("expected assumption-conditioned scenario output")
    claim = result["literature_endpoint_sanity_check"]["claim"]
    literature_value = float(claim["percent_released"])
    if not math.isfinite(literature_value) or not 0 <= literature_value <= 100:
        raise ValueError("literature endpoint must be finite percent in [0,100]")
    f8 = next((r for r in result["published_recipe_scenario_comparators"]
               if r.get("research_label") == claim["formulation"]), None)
    if f8 is None:
        raise ValueError("literature recipe scenario comparator is missing")
    t = str(claim["time_h"])
    models = {}
    for model in ("first_order", "weibull"):
        stats = f8["simulated"]["profiles_percent"][model][t]
        p05, p50, p95 = (float(stats[k]) for k in ("p05", "p50", "p95"))
        if not all(math.isfinite(x) and 0 <= x <= 100 for x in (p05,p50,p95)) or not p05 <= p50 <= p95:
            raise ValueError(f"invalid scenario quantiles for {model}")
        models[model] = {
            "simulated_p05_percent": p05,
            "simulated_p50_percent": p50,
            "simulated_p95_percent": p95,
            "absolute_median_error_percentage_points": abs(p50-literature_value),
            "literature_endpoint_within_scenario_p05_p95": p05 <= literature_value <= p95,
        }
    return {
        "status": "sanity_check_only_NOT_validation",
        "holdout_benchmark_status": "not_evaluated",
        "n_literature_endpoints": 1,
        "claim": claim,
        "models": models,
        "interpretation": (
            "Scenario-to-literature discrepancy only. Scenario quantiles are assumptions-based draws, "
            "not predictive intervals. One author-reported endpoint cannot establish fit, model ranking, "
            "calibration, or product performance; no parameter fitting was performed."
        ),
        "excluded_study": {
            "doi": "10.5281/zenodo.1311884",
            "reason": "Table 6 extraction has missing/inconsistent cells and nonmonotonic values; numeric curation unresolved.",
        },
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    report=benchmark(json.loads(a.input.read_text()))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
    print(json.dumps({"status":report["status"],"n_endpoints":report["n_literature_endpoints"],
                      "absolute_median_errors_pp":{m:v["absolute_median_error_percentage_points"] for m,v in report["models"].items()},
                      "out":str(a.out)}))


if __name__ == "__main__":
    main()
