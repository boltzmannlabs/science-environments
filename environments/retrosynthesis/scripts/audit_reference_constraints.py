"""Static reference compatibility with actual environment gates, not feasibility.

No search or LLM is run. The public result omits all reference identities and
structures; rejected record identifiers remain in a separate private result.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import time

from rdkit import rdBase
from synthesis_route_gym import validation
from synthesis_route_gym.route_data import load_stock
from synthesis_route_gym.schemas import Constraints, InventoryItem, RouteCandidate, Task


def audit_records(records, common_stock, max_steps=8):
    if not isinstance(records, list) or not records:
        raise ValueError("Reference records must be a nonempty array")
    identifiers = [record.get("record_id") for record in records if isinstance(record, dict)]
    if len(identifiers) != len(records) or any(not isinstance(value, str) or not value for value in identifiers):
        raise ValueError("Invalid reference identifiers")
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("Duplicate reference identifiers")
    with rdBase.BlockLogs():
        inventory = tuple(InventoryItem(smiles=value) for value in common_stock)
        template = Task(task_id="reference-constraint-audit", target="C", inventory=inventory,
                        constraints=Constraints(max_steps=max_steps), evidence=())
    hard, unknown, occurrences, quantity = Counter(), Counter(), Counter(), Counter()
    gates = Counter()
    ineligible, reasons = [], {}
    accepted = 0
    for record in records:
        with rdBase.BlockLogs():
            try:
                route = RouteCandidate.model_validate(record["reference_route"])
            except (KeyError, ValueError, TypeError):
                # Pydantic messages can echo private chemistry; never serialize them.
                raise ValueError("Reference route failed schema validation") from None
            # Only a schema-validated canonical target changes; the frozen stock
            # and constraints are reused without revalidating stock per target.
            task = template.model_copy(update={"target": route.target})
            assessment = validation.assess_route(task, route)
        hard_codes = {finding.code for finding in assessment.findings if finding.severity == "error"}
        unknown_codes = {finding.code for finding in assessment.findings if finding.severity == "unknown"}
        hard.update(hard_codes)
        unknown.update(unknown_codes)
        occurrences.update(finding.code for finding in assessment.findings if finding.severity == "error")
        quantity.update([assessment.quantity_status])
        gate_values = {
            "graph_valid": assessment.graph_valid,
            "inventory_complete": assessment.inventory_complete,
            "constraint_compliant": assessment.constraint_compliant,
            "quantity_not_requested": assessment.quantity_status == "not_requested",
            "not_acquisition_only": not assessment.acquisition_only,
        }
        gates.update(name for name, passed in gate_values.items() if passed)
        passes = all(gate_values.values())
        accepted += int(passes)
        if not passes:
            ineligible.append(record["record_id"])
            reasons[record["record_id"]] = {
                "hard_finding_codes": sorted(hard_codes),
                "failed_gates": sorted(name for name, passed in gate_values.items() if not passed),
            }
    public = {
        "schema_version": "srg-reference-constraint-audit.v1",
        "reference_records": len(records), "common_stock_items": len(inventory),
        "max_steps": max_steps, "task_scope": "identity_only_no_target_amount_no_added_reagents_no_trusted_evidence",
        "validation_entrypoint": "synthesis_route_gym.validation.assess_route",
        "acceptance_rule": "environment._submit_deterministic_gates_with_quantity_not_requested",
        "deterministically_accepted_records": accepted,
        "ineligible_records": len(ineligible),
        "gate_pass_records": dict(sorted(gates.items())),
        "quantity_status_records": dict(sorted(quantity.items())),
        "hard_finding_records": dict(sorted(hard.items())),
        "hard_finding_occurrences": dict(sorted(occurrences.items())),
        "unknown_finding_records": dict(sorted(unknown.items())),
        "scientific_feasibility_established": False,
        "interpretation": "Reference compatibility with current deterministic gates only. Missing co-reagents are not repaired or treated as known. Unknown evidence and conditions are not hard failures under this task.",
    }
    private = {
        "schema_version": "srg-private-reference-constraint-audit.v1",
        "ineligible_record_ids": sorted(ineligible),
        "ineligible_reasons": dict(sorted(reasons.items())),
    }
    return public, private


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--references", type=Path, required=True)
    parser.add_argument("--stock", type=Path, required=True)
    parser.add_argument("--public-output", type=Path, required=True)
    parser.add_argument("--private-output", type=Path, required=True)
    parser.add_argument("--max-steps", type=int, default=8)
    args = parser.parse_args()
    inputs = {args.references.resolve(), args.stock.resolve()}
    outputs = [args.public_output.resolve(), args.private_output.resolve()]
    if outputs[0] == outputs[1] or any(path in inputs or path.exists() for path in outputs):
        parser.error("Outputs must be distinct new files and must not overwrite inputs")
    started = time.monotonic()
    raw = args.references.read_bytes()
    stock_raw = args.stock.read_bytes()
    public, private = audit_records(json.loads(raw), load_stock(args.stock), args.max_steps)
    provenance = {
        "reference_sha256": hashlib.sha256(raw).hexdigest(),
        "stock_sha256": hashlib.sha256(stock_raw).hexdigest(),
        "validator_sha256": hashlib.sha256(Path(validation.__file__).read_bytes()).hexdigest(),
    }
    public = {**public, **provenance, "elapsed_seconds": round(time.monotonic() - started, 3)}
    private = {**private, **provenance}
    for path, result in ((args.private_output, private), (args.public_output, public)):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x") as handle:
            json.dump(result, handle, sort_keys=True, indent=2)
            handle.write("\n")
    print(json.dumps(public, sort_keys=True))


if __name__ == "__main__":
    main()
