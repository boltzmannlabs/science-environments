"""Yield inference and explicit heuristic route utility; no success probabilities."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from functools import lru_cache
import json
import math
from pathlib import Path

import numpy as np
from rdkit import Chem
from rdkit.Chem import rdFingerprintGenerator
from .condition_domain import CONDITION_ROLES, condition_roles_match_step

COMPONENTS = CONDITION_ROLES
FP_SIZE = 128
FEATURE_VERSION = "morgan-radius2-chiral-128-per-role.v1"
MODEL_SCHEMA = "condition-ranker.v1"


@lru_cache(maxsize=8192)
def _fingerprint(smiles: str) -> tuple[int, ...]:
    if not isinstance(smiles, str) or not smiles or len(smiles) > 10000:
        raise ValueError("A nonempty molecular SMILES is required")
    molecule = Chem.MolFromSmiles(smiles)
    if molecule is None:
        raise ValueError("Invalid molecular SMILES in condition features")
    generator = rdFingerprintGenerator.GetMorganGenerator(
        radius=2, fpSize=FP_SIZE, includeChirality=True)
    return tuple(int(v) for v in generator.GetFingerprintAsNumPy(molecule))


def condition_features(rows: Sequence[Mapping]) -> np.ndarray:
    """Use only declared chemical inputs; never inspect yield or outcome fields."""
    vectors = []
    for row in rows:
        if any(component not in row for component in COMPONENTS):
            raise ValueError("Condition input requires: " + ", ".join(COMPONENTS))
        vectors.append(tuple(v for c in COMPONENTS for v in _fingerprint(row[c])))
    return np.asarray(vectors, dtype=np.float32).reshape(len(rows), len(COMPONENTS) * FP_SIZE)


def _validate_tree(tree: Mapping, n_features: int) -> None:
    fields = ("left", "right", "feature", "threshold", "value")
    if any(not isinstance(tree.get(k), list) for k in fields):
        raise ValueError("Malformed model tree arrays")
    size = len(tree["left"])
    if not size or size > 100000 or any(len(tree[k]) != size for k in fields):
        raise ValueError("Invalid model tree size")
    for i in range(size):
        left, right, feature = (tree[k][i] for k in fields[:3])
        if any(type(v) is not int for v in (left, right, feature)):
            raise ValueError("Tree indices must be integers")
        if not all(type(tree[k][i]) in (float, int) and math.isfinite(tree[k][i])
                   for k in ("threshold", "value")):
            raise ValueError("Tree values must be finite")
        if left == right == -1:
            continue
        if not (i < left < size and i < right < size and 0 <= feature < n_features):
            raise ValueError("Tree child or feature index is invalid or cyclic")


class ConditionRanker:
    """ExtraTrees inference from JSON, without pickle or executable model loads."""

    def __init__(self, artifact: Mapping):
        if artifact.get("schema_version") != MODEL_SCHEMA:
            raise ValueError("Unsupported condition model schema")
        if artifact.get("n_features") != len(COMPONENTS) * FP_SIZE:
            raise ValueError("Incompatible condition feature count")
        trees = artifact.get("trees")
        if not isinstance(trees, list) or not 1 <= len(trees) <= 2048:
            raise ValueError("Model needs a bounded, nonempty tree ensemble")
        for tree in trees:
            _validate_tree(tree, artifact["n_features"])
        self._artifact = json.loads(json.dumps(artifact, allow_nan=False))

    @classmethod
    def load(cls, path: str | Path) -> "ConditionRanker":
        path = Path(path)
        if path.stat().st_size > 100_000_000:
            raise ValueError("Condition model exceeds the 100 MB loading limit")
        return cls(json.loads(path.read_text()))

    @property
    def metadata(self) -> dict:
        return json.loads(json.dumps(self._artifact.get("metadata", {})))

    def _predict_array(self, x: np.ndarray) -> np.ndarray:
        estimates = []
        for tree in self._artifact["trees"]:
            left = np.asarray(tree["left"])
            right = np.asarray(tree["right"])
            feature = np.asarray(tree["feature"])
            threshold = np.asarray(tree["threshold"])
            node = np.zeros(len(x), dtype=int)
            active = np.flatnonzero(left[node] != -1)
            while len(active):
                current = node[active]
                take_left = x[active, feature[current]] <= threshold[current]
                node[active] = np.where(take_left, left[current], right[current])
                active = np.flatnonzero(left[node] != -1)
            estimates.append(np.asarray(tree["value"])[node])
        return np.mean(estimates, axis=0)

    def predict(self, rows: Sequence[Mapping]) -> list[dict]:
        if not rows:
            return []
        predictions = self._predict_array(condition_features(rows))
        metadata = self.metadata
        residual = metadata.get("validation_residual_q90")
        if residual is not None and (not math.isfinite(residual) or residual < 0):
            raise ValueError("Invalid residual uncertainty band")
        known = metadata.get("training_component_smiles", {})
        return [{
            "predicted_yield_percent": float(np.clip(prediction, 0, 100)),
            "lower_yield_percent": None if residual is None else float(max(0, prediction - residual)),
            "upper_yield_percent": None if residual is None else float(min(100, prediction + residual)),
            "interval_kind": "validation_residual_band_not_coverage_guarantee",
            "evidence_status": "predicted",
            "model_version": metadata.get("model_version", "unknown"),
            "domain": "Dreher-Doyle Buchwald-Hartwig conditions",
            "unseen_components": [c for c in COMPONENTS if c in known and row[c] not in known[c]],
        } for row, prediction in zip(rows, predictions)]


def rank_routes(routes: Sequence[Mapping], condition_ranker: ConditionRanker | None = None) -> list[dict]:
    """Rank records, preserving unknowns; bottleneck yield is not overall yield.

    The trained yield model is used only for steps carrying an explicit
    `condition_inputs` role mapping (or legacy `conditions` mapping). Prose
    condition tuples cannot be inferred into model inputs. The route score
    itself is a declared surrogate heuristic, not a learned route ranker.
    Legacy records without a quantity status are treated as `not_requested`
    (structural inventory only); an empty route is never synthesis-eligible.
    """
    ranked = []
    for route in routes:
        steps = route.get("steps", [])
        values = []
        applied_count = 0
        refused_count = 0
        for step in steps:
            predicted_yield = step.get("predicted_yield")
            conditions = step.get("condition_inputs")
            if conditions is None:
                conditions = step.get("conditions")
            if (condition_ranker is not None and isinstance(conditions, Mapping)
                    and all(component in conditions for component in COMPONENTS)):
                if condition_roles_match_step(step):
                    predicted_yield = condition_ranker.predict([conditions])[0]["predicted_yield_percent"] / 100
                    applied_count += 1
                else:
                    refused_count += 1
            if predicted_yield is not None:
                if not isinstance(predicted_yield, (float, int)) or not math.isfinite(predicted_yield) or not 0 <= predicted_yield <= 1:
                    raise ValueError("Step predicted_yield must be a fraction in [0, 1]")
            values.append(predicted_yield)
        known = [v for v in values if v is not None]
        unknown_count = len(values) - len(known)
        bottleneck = min(known) if known else None
        quantity_status = route.get("quantity_status", "not_requested")
        acquisition_only = bool(route.get("acquisition_only", not steps))
        eligible = bool(steps and route.get("graph_valid") is True and route.get("inventory_complete") is True
                        and route.get("constraint_compliant", True) is True
                        and quantity_status in {"complete", "not_requested"} and not acquisition_only)
        utility = (bottleneck or 0) - 0.1 * unknown_count - 0.01 * len(steps)
        ranked.append({
            "route_id": route["route_id"], "eligible": eligible,
            "score": utility, "score_kind": "heuristic_utility_not_success_probability",
            "route_utility_kind": "declared_surrogate_heuristic",
            "bottleneck_predicted_yield": bottleneck,
            "unknown_step_count": unknown_count, "step_count": len(steps),
            "condition_model_applied_step_count": applied_count,
            "condition_model_refused_step_count": refused_count,
            "quantity_status": quantity_status, "acquisition_only": acquisition_only,
            "model_version": condition_ranker.metadata.get("model_version") if applied_count else None,
            "review_status": route.get("review_status", "pending"),
        })
    return sorted(ranked, key=lambda r: (-int(r["eligible"]), -r["score"], r["route_id"]))
