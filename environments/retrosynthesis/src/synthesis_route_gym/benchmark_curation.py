"""Outcome-blind curation; only ``tasks`` may enter agent-facing bundles."""
from collections import Counter, defaultdict
import csv
from hashlib import sha256
import json
import math
from pathlib import Path

from .chemistry import canonical_smiles
from .condition_domain import CONDITION_ROLES, FIXED_PARTNER, FIXED_PRECATALYST
from .data_partition import audit_assignments, record_keys, select_grouped_records

PILOT_BUDGET = {"max_actions": 80, "max_expansions": 12, "max_wall_seconds": 600,
                "max_llm_tokens": 200000, "top_k": 5}
MAX_REFERENCE_STEPS = 8


def _digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_seen_doyle(path: str | Path) -> list[dict]:
    """Adapt previously inspected Doyle rows for development only."""
    with Path(path).open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    records = []
    for index, row in enumerate(rows):
        try:
            conditions = {role: canonical_smiles(row[role]) for role in CONDITION_ROLES}
            target = canonical_smiles(row["rxn"].split(">>")[1])
            outcome = float(row["yield"])
            if not math.isfinite(outcome) or not 0 <= outcome <= 100:
                raise ValueError("Invalid outcome")
        except (KeyError, IndexError, TypeError, ValueError):
            raise ValueError(f"Invalid seen-development record at row {index}") from None
        records.append({"record_id": "doyle-" + _digest([index, target, conditions])[:24],
                        "target": target, "reactants": sorted([conditions["aryl halide"], FIXED_PARTNER]),
                        "conditions": {**conditions, "catalyst": FIXED_PRECATALYST},
                        "outcome_yield_percent": outcome,
                        "source_family": "doi:10.1126/science.aar5169",
                        "source_locator": f"DreherDoyle.csv#data-row={index + 1}"})
    return records


def _condition_tasks(records, partition):
    buckets = defaultdict(list)
    seen = set()
    for row in records:
        target = canonical_smiles(row["target"])
        reactants = tuple(sorted(canonical_smiles(x) for x in row["reactants"]))
        identity = _digest([target, reactants, row["conditions"]])
        if identity in seen:
            raise ValueError("Duplicate condition inputs: replicate handling must be declared before allocation")
        seen.add(identity)
        buckets[(row["source_family"], target, reactants)].append(row)
    tasks, labels, descriptors = [], [], []
    for key, rows in sorted(buckets.items()):
        task_id = "condition-" + _digest(key)[:24]
        ordered = sorted(rows, key=lambda r: _digest(r["record_id"]))
        candidates = [{"candidate_id": "c-" + _digest(row["record_id"])[:24],
                       "reactants": list(key[2]), "conditions": dict(row["conditions"])} for row in ordered]
        tasks.append({"task_id": task_id, "track": "measured_conditions", "partition": partition,
                      "target": key[1], "candidates": candidates, "budget": dict(PILOT_BUDGET)})
        labels.append({"task_id": task_id,
                       "outcomes": {c["candidate_id"]: row["outcome_yield_percent"] for c, row in zip(candidates, ordered)},
                       "source_locators": {c["candidate_id"]: row["source_locator"] for c, row in zip(candidates, ordered)},
                       "source_family": key[0], "outcome_scope": "recorded_percentage_yield"})
        descriptors.append({"record_id": task_id, "target": key[1], "source_keys": [key[0]],
                            "reaction_keys": [".".join(key[2]) + ">>" + key[1]], "partition": partition})
    return tasks, labels, descriptors


def _route_tasks(selected, stock, seed):
    # Choose removed stock without reference leaves or reaction answers.
    removed = sorted(stock, key=lambda value: _digest([seed, "stock-perturbation", value]))[:max(1, len(stock) // 10)]
    tasks, labels, task_groups = [], [], []
    for row in selected:
        for variant, exclusions in (("full", []), ("restricted", removed)):
            task_id = "route-" + _digest([seed, row["record_id"], variant])[:24]
            tasks.append({"task_id": task_id, "track": "reference_route", "partition": row["partition"],
                          "target": row["target"], "inventory_exclusions": list(exclusions),
                          "constraints": {"max_steps": MAX_REFERENCE_STEPS}, "budget": dict(PILOT_BUDGET)})
            closed = set(row["stock"]) <= set(stock) - set(exclusions)
            labels.append({"task_id": task_id, "reference_route": row["reference_route"],
                           "source_locator": row["source_locator"], "reference_inventory_closed": closed,
                           "inventory_reference_scope": "reference_only_not_proof_that_no_alternative_exists"})
            task_groups.append({"task_id": task_id, "record_id": row["record_id"],
                                "group_id": row["group_id"], "partition": row["partition"], "variant": variant})
    return tasks, labels, task_groups


def prepare_tasks(route_records, stock, condition_records, doyle_records, *, quotas, seed,
                  training_overlap_record_ids=()):
    """Prepare public/private inputs without inspecting outcome rankings."""
    common_stock = sorted({canonical_smiles(s) for s in stock})
    if not common_stock:
        raise ValueError("Common stock must not be empty")
    fresh_tasks, fresh_labels, fresh_groups = _condition_tasks(condition_records, "sealed_final")
    seen_tasks, seen_labels, seen_groups = _condition_tasks(doyle_records, "development")
    condition_groups = fresh_groups + seen_groups
    reserved = {key for row in condition_groups for key in record_keys(row)}
    cross_track = {r["record_id"] for r in route_records if reserved.intersection(record_keys(r))}
    stock_set = set(common_stock)
    ineligible = {r["record_id"] for r in route_records
                  if not 1 <= r["step_count"] <= MAX_REFERENCE_STEPS or not set(r["stock"]) <= stock_set
                  or canonical_smiles(r["target"]) in stock_set}
    training_overlap = set(training_overlap_record_ids)
    allocation = select_grouped_records(route_records, quotas, seed=seed,
                                         excluded_record_ids=cross_track | ineligible | training_overlap)
    assignments = allocation["assignments"] + [
        {"record_id": row["record_id"], "partition": row["partition"], "selected": True,
         "group_id": "condition-source-" + _digest(row["source_keys"])[:24]} for row in condition_groups]
    combined_audit = audit_assignments(list(route_records) + condition_groups, assignments)
    tasks, labels, task_groups = _route_tasks(allocation["selected"], common_stock, seed)
    selected = allocation["selected"]
    report = {"allocation": allocation["audit"], "combined_overlap_audit": combined_audit,
              "route_targets": len(selected), "route_tasks_including_stock_variants": len(tasks),
              "route_targets_by_partition": dict(Counter(row["partition"] for row in selected)),
              "condition_tasks_by_partition": {"sealed_final": len(fresh_tasks), "development": len(seen_tasks)},
              "condition_records_by_partition": {"sealed_final": len(condition_records), "development": len(doyle_records)},
              "cross_track_excluded_records": len(cross_track),
              "reference_eligibility_excluded_records": len(ineligible),
              "available_training_overlap_excluded_records": len(training_overlap),
              "common_stock_count": len(common_stock),
              "route_diversity": {"step_counts": dict(sorted(Counter(r["step_count"] for r in selected).items())),
                                  "with_stereochemistry": sum(r["has_stereo"] for r in selected),
                                  "convergent": sum(r["convergent"] for r in selected)},
              "final_run_authorized": False,
              "data_status": "candidate_final_cohort_access_boundary_tested_pending_full_protocol_seal",
              "source_family_independence": "PaRoutes_document_groups_verified_patent_families_unresolved",
              "condition_final_independent_source_groups": len({r["source_family"] for r in condition_records})}
    return {"tasks": tasks + fresh_tasks + seen_tasks, "labels": labels + fresh_labels + seen_labels,
            "assignments": assignments, "task_groups": task_groups,
            "group_links": allocation["links"], "report": report}
