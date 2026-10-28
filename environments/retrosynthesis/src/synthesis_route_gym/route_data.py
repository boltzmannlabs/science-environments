"""Strict PaRoutes reference-data parser. Outputs belong to the private evaluator.

``stock`` in a parsed record means reference leaves, never an agent inventory.
Load the official common stock separately with :func:`load_stock`.
Document IDs are not patent-family assignments. Unknown provenance shares one
conservative grouping key across files; per-row IDs must never replace it.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re

from rdkit import Chem, rdBase
from rdkit.Chem.Scaffolds import MurckoScaffold

from .chemistry import canonical_smiles
from .schemas import MaterialUse, ReactionStep, RouteCandidate

UNRESOLVED_SOURCE = "unresolved:paroutes"
_DOCUMENT = re.compile(r"^[A-Z]{2}(?:RE|PP|D|H)?\d{5,}[A-Z]?\d?$")


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _canonical(value: object) -> str:
    # RDKit parse logs contain molecular strings: keep private references private.
    with rdBase.BlockLogs():
        try:
            return canonical_smiles(value)
        except (TypeError, ValueError) as error:
            raise ValueError("Invalid molecular structure in reference record") from None


def _metadata(node: dict) -> dict:
    value = node.get("metadata", {})
    if not isinstance(value, dict):
        raise ValueError("Node metadata must be an object")
    return value


def _documents(node: dict) -> tuple[str, ...]:
    metadata = _metadata(node)
    explicit = tuple(metadata[key] for key in ("patent_id", "document_id")
                     if key in metadata)
    if any(not isinstance(value, str) or not value.strip() or len(value) > 200
           for value in explicit):
        raise ValueError("Invalid explicit source document identifier")
    # PaRoutes V2 reaction metadata uses patent;paragraph;reaction_index IDs.
    identifier = metadata.get("ID")
    first = identifier.split(";", 1)[0] if isinstance(identifier, str) else ""
    inferred = (first,) if _DOCUMENT.fullmatch(first) else ()
    return tuple(sorted(set((*explicit, *inferred))))


def _children(node: dict) -> list:
    children = node.get("children", [])
    if not isinstance(children, list):
        raise ValueError("Node children must be an array")
    return children


@dataclass(frozen=True)
class _Tree:
    target: str
    reactions: tuple[tuple[str, tuple[str, ...]], ...] = ()
    leaves: tuple[str, ...] = ()
    documents: tuple[tuple[str, ...], ...] = ()
    reaction_locators: tuple[str, ...] = ()
    molecules: tuple[str, ...] = ()
    convergent: bool = False


def _walk(node: object, ancestors: frozenset[str], identities: frozenset[int], depth: int) -> _Tree:
    if depth > 100:
        raise ValueError("Reference route exceeds depth limit")
    if not isinstance(node, dict) or node.get("type") != "mol":
        raise ValueError("Expected a molecule node")
    if id(node) in identities:
        raise ValueError("Reference object cycle")
    _metadata(node)
    target = _canonical(node.get("smiles"))
    if target in ancestors:
        raise ValueError("Reference molecular cycle")
    children = _children(node)
    if not children:
        return _Tree(target=target, leaves=(target,), molecules=(target,))
    if len(children) != 1:
        raise ValueError("Molecule must have exactly one producing reaction")
    reaction = children[0]
    if not isinstance(reaction, dict) or reaction.get("type") != "reaction":
        raise ValueError("Expected a reaction node")
    if id(reaction) in identities or reaction is node:
        raise ValueError("Reference object cycle")
    metadata = _metadata(reaction)
    precursors = _children(reaction)
    if not precursors or len(precursors) > 100:
        raise ValueError("Reaction requires between 1 and 100 reactant nodes")
    branches = tuple(_walk(child, ancestors | {target}, identities | {id(node), id(reaction)}, depth + 1)
                     for child in precursors)
    reactants = tuple(sorted(branch.target for branch in branches))
    return _Tree(
        target=target,
        reactions=((target, reactants),) + tuple(item for branch in branches for item in branch.reactions),
        leaves=tuple(item for branch in branches for item in branch.leaves),
        documents=(_documents(reaction),) + tuple(item for branch in branches for item in branch.documents),
        reaction_locators=((metadata.get("ID") if isinstance(metadata.get("ID"), str) else ""),)
                          + tuple(item for branch in branches for item in branch.reaction_locators),
        molecules=(target,) + tuple(item for branch in branches for item in branch.molecules),
        convergent=sum(bool(branch.reactions) for branch in branches) >= 2 or any(branch.convergent for branch in branches),
    )


def _source_identity(root: dict, tree: _Tree) -> dict:
    fallback = _documents(root)
    per_step = tuple(documents or fallback for documents in tree.documents)
    documents = sorted({document for group in per_step for document in group})
    incomplete = any(not group for group in per_step)
    status = ("unresolved" if not documents else "partial_documents" if incomplete
              else "resolved_document" if len(documents) == 1 else "multiple_documents")
    source_keys = [f"patent:{document}" for document in documents]
    return {
        "source_family": source_keys[0] if status == "resolved_document" else UNRESOLVED_SOURCE,
        "source_keys": source_keys + ([UNRESOLVED_SOURCE] if incomplete else []),
        "source_documents": documents,
        "source_identity_status": status,
        "patent_family_status": "unknown",
        "source_identity_scope": "document_not_verified_patent_family",
        "reaction_source_locators": sorted(set(value for value in tree.reaction_locators if value)),
    }


def _has_stereo(smiles: str) -> bool:
    molecule = Chem.MolFromSmiles(smiles)
    return any(atom.GetChiralTag() != Chem.ChiralType.CHI_UNSPECIFIED for atom in molecule.GetAtoms()) or any(
        bond.GetStereo() != Chem.BondStereo.STEREONONE for bond in molecule.GetBonds())


def parse_paroutes_record(tree: object, source_id: str, index: int) -> dict:
    """Parse one alternating tree; reject ambiguity without echoing chemistry.

    ``source_id`` identifies a frozen dataset version, not a patent/family.
    ``index`` is the zero-based JSON array position and remains in the locator.
    Repeated leaves are allowed; repeated produced molecules and molecules used
    both as stock leaves and produced intermediates are rejected, because the
    current RouteCandidate graph cannot represent those occurrences distinctly.
    """
    if (not isinstance(source_id, str) or not source_id or len(source_id) > 180
            or any(ord(char) < 32 for char in source_id)):
        raise ValueError("Invalid dataset source identifier")
    if isinstance(index, bool) or not isinstance(index, int) or index < 0:
        raise ValueError("Record index must be a nonnegative integer")
    parsed = _walk(tree, frozenset(), frozenset(), 0)
    if not parsed.reactions or len(parsed.reactions) > 100:
        raise ValueError("Reference route requires between 1 and 100 steps")
    products = tuple(product for product, _ in parsed.reactions)
    if len(products) != len(set(products)):
        raise ValueError("Ambiguous repeated product in reference route")
    if set(products) & set(parsed.leaves):
        raise ValueError("Ambiguous leaf also used as produced product")
    reactions = sorted(parsed.reactions)
    reaction_keys = sorted(".".join(reactants) + ">>" + product for product, reactants in reactions)
    fingerprint = _digest({"target": parsed.target, "reactions": reaction_keys})
    identifier = "paroutes-" + _digest([source_id, index, fingerprint])[:24]
    steps = tuple(ReactionStep(
        step_id=f"step-{number:03d}", product=product,
        reactants=tuple(MaterialUse(smiles=value) for value in reactants),
        source_tool="PaRoutes reference extraction", source_version=source_id,
    ) for number, (product, reactants) in enumerate(reactions))
    route = RouteCandidate(route_id=identifier, target=parsed.target, steps=steps)
    scaffold = MurckoScaffold.MurckoScaffoldSmiles(smiles=parsed.target, includeChirality=False)
    return {
        "record_id": identifier, "target": parsed.target, "source_id": source_id,
        **_source_identity(tree, parsed),
        "source_locator": f"{source_id}#/{index}",
        "route_fingerprint": fingerprint, "reaction_keys": reaction_keys,
        "intermediate_keys": sorted(set(products) - {parsed.target}),
        "molecule_keys": sorted(set(products)),
        "scaffold": scaffold,
        "reference_route": route.model_dump(mode="json"),
        "stock": sorted(set(parsed.leaves)),
        "step_count": len(steps),
        "has_stereo": any(_has_stereo(value) for value in set(parsed.molecules)),
        "convergent": parsed.convergent,
    }


def load_paroutes(path: str | Path, source_id: str) -> list[dict]:
    """Load an entire reference array strictly; never silently skip bad rows.

    For a curation audit, call ``parse_paroutes_record`` per row and retain
    rejected indices/reasons privately before selecting an eligible cohort.
    """
    try:
        data = json.loads(Path(path).read_text())
    except (json.JSONDecodeError, RecursionError, UnicodeError):
        raise ValueError("Invalid reference JSON") from None
    if not isinstance(data, list):
        raise ValueError("Reference JSON must contain a route array")
    rows = []
    for index, tree in enumerate(data):
        try:
            row = parse_paroutes_record(tree, source_id, index)
        except (ValueError, RecursionError) as error:
            raise ValueError(f"Invalid reference record at index {index}: {type(error).__name__}") from None
        rows = [*rows, row]
    return rows


def load_stock(path: str | Path) -> list[str]:
    """Load a common benchmark stock independently of any reference route."""
    values = frozenset()
    for index, line in enumerate(Path(path).read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = _canonical(line.strip())
        except ValueError:
            raise ValueError(f"Invalid stock molecule at line {index}") from None
        values = values | {value}
    return sorted(values)
