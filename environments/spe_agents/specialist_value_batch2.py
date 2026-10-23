"""Batch 2 specialist-on/off analysis protocol."""

from __future__ import annotations

import time
from typing import Any, Mapping

from .specialist_value import CommandProvider, combined_usage


WARNING_CODES = (
    "basis_metadata_mismatch",
    "counterpoise_evidence_missing",
    "duplicate_geometry",
    "fragment_geometry_mismatch",
    "missing_required_reference",
    "property_label_mismatch",
    "reference_identity_mismatch",
    "truncated_grid_artifact",
    "unsupported_thermodynamic_claim",
)

QUANTITY_SCOPES = (
    "electron_density_and_esp_artifacts",
    "fixed_geometry_cluster_interaction_energy",
    "fixed_geometry_conformer_energy_difference",
    "fixed_geometry_noncovalent_interaction_energy",
    "fixed_geometry_solvation_cluster_interaction_energy",
)


def response_schema() -> dict[str, Any]:
    return {
        "disposition": "accept|reject|review",
        "selected_records": ["labels safe to use"],
        "excluded_records": ["labels rejected or withheld"],
        "warning_codes": ["exact codes from warning_code_vocabulary"],
        "quantity_scope": "exactly one value from quantity_scope_vocabulary",
        "values": {
            "key from case.output_contract.value_keys_when_supported": "number|string|array"
        },
        "explanation": "concise evidence-based explanation",
    }


def analysis_payload(
    case: Mapping[str, Any],
    *,
    role: str,
    specialist_contract: Mapping[str, Any] | None = None,
    specialist_recommendation: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "protocol": "boltzmann-spe-specialist-analysis-batch2-v1",
        "role": role,
        "objective": (
            "Audit only the supplied immutable Boltzmann SPE records. Return the structured "
            "scientific decision; do not run calculations, repair evidence, or infer missing data."
        ),
        "case": dict(case),
        "common_rules": [
            "A converged total energy does not validate a malformed or mislabeled property artifact.",
            "Interaction terms require exact fragment identity, cluster-extracted geometries, and matched electronic settings.",
            "Counterpoise correction requires explicit ghost-basis component evidence.",
            "Use review when valid evidence can be retained but a requested property, comparison, or claim must be withheld.",
            "Return record labels exactly as supplied and use case.output_contract.quantity_scope verbatim.",
            "Return every supported key named in case.output_contract.value_keys_when_supported; do not invent unavailable values.",
            "A fixed-geometry cluster electronic difference is not a solvation free energy, binding free energy, or thermochemical strain energy.",
        ],
        "warning_code_vocabulary": list(WARNING_CODES),
        "quantity_scope_vocabulary": list(QUANTITY_SCOPES),
        "response_schema": response_schema(),
        "hidden_reference_policy": "Expected answers are evaluator-only and unavailable here.",
    }
    if specialist_contract is not None:
        payload["specialist_contract"] = dict(specialist_contract)
    if specialist_recommendation is not None:
        payload["specialist_recommendation"] = dict(specialist_recommendation)
        payload["objective"] = (
            "Independently verify the specialist recommendation against the public case and "
            "common rules, then return the final structured decision."
        )
    return payload


def run_arm(
    case: Mapping[str, Any],
    *,
    arm: str,
    provider: CommandProvider,
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    started = time.perf_counter()
    calls: list[dict[str, Any]] = []
    if arm == "agent-scientist":
        response = provider.request(analysis_payload(case, role="general-controller"))
        calls.append({"role": "general-controller", "response": response})
        final = response
    elif arm == "agent-scientist-plus-specialist":
        specialist = provider.request(
            analysis_payload(case, role="spe-specialist", specialist_contract=contract)
        )
        calls.append({"role": "spe-specialist", "response": specialist})
        final = provider.request(
            analysis_payload(
                case,
                role="general-controller-review",
                specialist_recommendation={
                    key: value
                    for key, value in specialist.items()
                    if key != "agent_scientist_usage"
                },
            )
        )
        calls.append({"role": "general-controller-review", "response": final})
    else:
        raise ValueError(f"unknown arm: {arm}")
    return {
        "case_id": case["case_id"],
        "environment_id": case["environment_id"],
        "arm": arm,
        "wall_seconds": time.perf_counter() - started,
        "calls": calls,
        "response": {
            key: value for key, value in final.items() if key != "agent_scientist_usage"
        },
        "usage": combined_usage(calls),
    }
