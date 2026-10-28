"""Optional AiZynthFinder API adapter with explicit missing-dependency results.

API reference: https://molecularai.github.io/aizynthfinder/python_interface.html
Use a local configuration whose model and stock artifacts are frozen for the run.
"""

from __future__ import annotations

import sys
import hashlib
from dataclasses import dataclass
from pathlib import Path

from .common import canonical_smiles, normalise_result, response, run_worker, validate_request


def _tree_steps(node: dict, version: str, ancestors: tuple[str, ...] = ()) -> tuple[dict, ...]:
    if not isinstance(node, dict) or node.get("type") != "mol":
        raise ValueError("Expected an AiZynthFinder molecule node.")
    product = canonical_smiles(node.get("smiles"))
    if product in ancestors:
        raise ValueError("Route contains a molecule cycle.")
    if len(ancestors) >= 100:
        raise ValueError("Route exceeds 100 transformations.")
    children = node.get("children", [])
    if not isinstance(children, list) or len(children) > 1:
        raise ValueError("A single route must have at most one reaction per molecule.")
    if not children:
        return ()
    reaction = children[0]
    if not isinstance(reaction, dict) or reaction.get("type") != "reaction":
        raise ValueError("Expected an AiZynthFinder reaction node.")
    reactants = reaction.get("children", [])
    if not isinstance(reactants, list) or not 1 <= len(reactants) <= 100:
        raise ValueError("A reaction requires 1 to 100 reactant molecule nodes.")
    substeps = tuple(step for reactant in reactants
                     for step in _tree_steps(reactant, version, (*ancestors, product)))
    if len(substeps) >= 100:
        raise ValueError("Route exceeds 100 transformations.")
    metadata = reaction.get("metadata") or {}
    if not isinstance(metadata, dict):
        raise ValueError("Invalid reaction metadata.")
    step = {"step_id": "az-" + hashlib.sha256(product.encode()).hexdigest()[:16],
            "product": product,
            "reactants": [{"smiles": canonical_smiles(item.get("smiles")), "amount_mmol": None}
                          for item in reactants],
            "source_tool": "AiZynthFinder", "source_version": version,
            "proposal_score": metadata.get("policy_probability"), "conditions_complete": False}
    return (*substeps, step)


def normalise_aizynth_route(tree: dict, route_id: str, source_version: str) -> dict:
    """Convert one reaction tree to the gym contract without trusting stock flags.

    AiZynthFinder routes omit quantities, conditions, and experimental evidence.
    These remain unknown; inventory is rechecked by the gym's assessor.
    """
    from ..schemas import RouteCandidate

    steps = _tree_steps(tree, source_version)
    by_product: dict[str, dict] = {}
    for step in steps:
        previous = by_product.get(step["product"])
        if previous and previous["reactants"] != step["reactants"]:
            raise ValueError("Route has conflicting syntheses of the same intermediate.")
        by_product = {**by_product, step["product"]: previous or step}
    route = RouteCandidate.model_validate({"route_id": route_id,
        "target": canonical_smiles(tree.get("smiles")), "steps": list(by_product.values())})
    return route.model_dump(mode="json")


@dataclass(frozen=True)
class AiZynthFinderAdapter:
    config_path: Path | str
    python_executable: Path | str = sys.executable
    expansion_policy: str = "uspto"
    stock_names: tuple[str, ...] = ()
    filter_policy: str | None = None
    timeout_seconds: float = 120.0

    def _run(self, target_smiles: str, top_k: int, operation: str, **limits) -> dict:
        try:
            target = validate_request(target_smiles, top_k)
            for value in limits.values():
                if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 10000:
                    raise ValueError("Search limits must be positive integers at most 10000.")
        except ValueError as error:
            return response("error", str(error))
        config = Path(self.config_path).resolve()
        if not config.is_file():
            return response("unavailable", "AiZynthFinder configuration is missing.")
        payload = {
            "backend": "aizynthfinder", "operation": operation, "target_smiles": target,
            "top_k": top_k, "config_path": str(config), "expansion_policy": self.expansion_policy,
            "stock_names": list(self.stock_names), "filter_policy": self.filter_policy, **limits,
        }
        return normalise_result(run_worker(self.python_executable, payload, self.timeout_seconds),
                                "AiZynthFinder", top_k)

    def expand(self, target_smiles: str, top_k: int = 10) -> dict:
        return self._run(target_smiles, top_k, "expand")

    def search(self, target_smiles: str, top_k: int = 10,
               max_iterations: int = 100, max_transforms: int = 6) -> dict:
        return self._run(target_smiles, top_k, "search", max_iterations=max_iterations,
                         max_transforms=max_transforms)
