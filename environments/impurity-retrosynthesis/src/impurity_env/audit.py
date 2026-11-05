"""Conservative, read-only audit of Boltzmann-style retrosynthesis exports.

No reaction feasibility, exact atom balance, patent precedent, experimental yield,
or INR cost is inferred. All diagnostics explicitly distinguish omitted inputs.
"""
from collections import Counter
import json
from pathlib import Path


def _rdkit():
    try:
        from rdkit import Chem
    except ImportError as exc:
        raise RuntimeError("RDKit is required for structural checks; no check was run") from exc
    return Chem


def _mol(chem, smiles):
    if not isinstance(smiles, str) or not smiles.strip():
        return None
    return chem.MolFromSmiles(smiles)


def _element_counts(mol):
    return Counter(atom.GetSymbol() for atom in mol.GetAtoms())


def _nonempty(value):
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return any(isinstance(x, str) and bool(x.strip()) for x in value)
    return False


def _walk(node):
    if not isinstance(node, dict):
        raise ValueError("route graph contains a non-object node")
    yield node
    children = node.get("children", [])
    if not isinstance(children, list):
        raise ValueError("route graph children must be a list")
    for child in children:
        yield from _walk(child)


def audit_export(raw, target_smiles, source_basename="unknown.json"):
    """Audit each original route ID and its graph; return JSON-serializable data."""
    chem = _rdkit()
    target = _mol(chem, target_smiles)
    if target is None:
        raise ValueError("target_smiles is missing or invalid")
    if not isinstance(raw, dict) or not raw:
        raise ValueError("export must be a nonempty top-level route dictionary")
    canonical = chem.MolToSmiles(target, isomericSmiles=True)
    routes = []
    for rid, wrapper in raw.items():
        if not isinstance(rid, str) or not rid or not isinstance(wrapper, dict):
            raise ValueError("invalid route ID or wrapper")
        root = wrapper.get("path")
        if not isinstance(root, dict):
            raise ValueError(f"route {rid}: missing path object")
        nodes = list(_walk(root))
        steps = []
        leaves = []
        for node in nodes:
            if not node.get("children"):
                leaves.append({"smiles": node.get("smile"), "parseable": _mol(chem, node.get("smile")) is not None,
                               "platform_building_block": node.get("building_block")})
            if not node.get("reaction_name"):
                continue
            product = _mol(chem, node.get("smile"))
            precursor_smiles = [child.get("smile") for child in node.get("children", [])]
            precursors = [_mol(chem, smi) for smi in precursor_smiles]
            parseable = product is not None and bool(precursors) and all(m is not None for m in precursors)
            missing = {}
            if parseable:
                available = Counter()
                for mol in precursors:
                    available.update(_element_counts(mol))
                missing = {symbol: n - available[symbol]
                           for symbol, n in _element_counts(product).items() if n > available[symbol]}
            steps.append({"node_id": node.get("id"), "reaction_label": node.get("reaction_name"),
                          "product_smiles": node.get("smile"), "listed_precursors": precursor_smiles,
                          "parseable_smiles": parseable,
                          "missing_heavy_element_source_in_listed_inputs": missing,
                          "has_traceable_citation": _nonempty(node.get("uspto_link")),
                          "has_procedure_text": _nonempty(node.get("procedure"))})
        root_mol = _mol(chem, root.get("smile"))
        root_match = root_mol is not None and chem.MolToSmiles(root_mol, isomericSmiles=True) == canonical
        flags = []
        if not root_match:
            flags.append("ROOT_SMILES_MISMATCH")
        if not steps:
            flags.append("NO_REACTION_NODES")
        if any(not x["parseable_smiles"] for x in steps) or any(not x["parseable"] for x in leaves):
            flags.append("INVALID_LISTED_SMILES")
        if any(x["missing_heavy_element_source_in_listed_inputs"] for x in steps):
            flags.append("MISSING_ELEMENT_SOURCE_IN_LISTED_INPUTS")
        if any(not x["has_traceable_citation"] for x in steps):
            flags.append("NO_TRACEABLE_STEP_CITATION")
        if any(not x["has_procedure_text"] for x in steps):
            flags.append("NO_PROCEDURE_TEXT")
        if any(x["reaction_label"] == "otherreaction" for x in steps):
            flags.append("UNSPECIFIED_REACTION_CLASS")
        routes.append({"route_id": rid, "root_smiles": root.get("smile"), "root_matches_supplied_target": root_match,
                       "reaction_node_count": len(steps), "starting_material_leaves": leaves, "steps": steps,
                       "flags": flags, "decision": "Hold pending evidence"})
    return {"audit_type": "computational_only_not_route_validation", "source_basename": source_basename,
            "target_smiles": target_smiles, "route_count": len(routes), "routes": routes}


def audit_file(path, target_smiles):
    """Read the export only; basename avoids publishing private filesystem paths."""
    file = Path(path)
    return audit_export(json.loads(file.read_text(encoding="utf-8")), target_smiles, file.name)
