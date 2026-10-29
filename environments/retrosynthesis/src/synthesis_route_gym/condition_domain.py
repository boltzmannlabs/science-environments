"""Conservative structural applicability gate for the measured C–N model.

This verifies that the declared route really describes the model's aryl-halide
coupling with fixed p-toluidine partner and source-dataset Pd precatalyst. It
does not certify feasibility, conditions, or yields for a new combination.
"""
from collections.abc import Mapping, Sequence
from functools import lru_cache

from rdkit import Chem
from rdkit.Chem import rdChemReactions

from .chemistry import canonical_smiles

CONDITION_ROLES = ("aryl halide", "ligand", "additive", "base")
FIXED_PARTNER = canonical_smiles("Cc1ccc(N)cc1")
FIXED_PRECATALYST = canonical_smiles("O=S(=O)(O[Pd]1c2ccccc2-c2ccccc2N~1)C(F)(F)F")


def _declared_smiles(values) -> tuple[str, ...]:
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        raise ValueError("Declared reaction inputs must be a sequence")
    return tuple(canonical_smiles(value.get("smiles") if isinstance(value, Mapping) else value)
                 for value in values)


@lru_cache(maxsize=512)
def _coupling_products(aryl_halide: str) -> frozenset[str]:
    substrate = Chem.MolFromSmiles(aryl_halide)
    partner = Chem.MolFromSmiles(FIXED_PARTNER)
    transformation = rdChemReactions.ReactionFromSmarts(
        "[c:1]-[Cl,Br,I].[NH2:2]-[c:3]>>[c:1]-[NH:2]-[c:3]")
    products = []
    for result in transformation.RunReactants((substrate, partner), maxProducts=32):
        for molecule in result:
            try:
                Chem.SanitizeMol(molecule)
                products.append(canonical_smiles(Chem.MolToSmiles(molecule, isomericSmiles=True)))
            except (ValueError, RuntimeError):
                continue
    return frozenset(products)


def condition_roles_match_step(step: Mapping) -> bool:
    """Return False for missing, unrelated or structurally out-of-domain steps.

    The aryl halide and fixed amine must be declared reactants. The three
    remaining roles and the source Pd precatalyst must occur in the declared
    input mixture. Other added species conservatively put the step outside
    this narrowly trained domain. Product matching uses the actual C–N edit.
    """
    if not isinstance(step, Mapping):
        return False
    roles = step.get("condition_inputs")
    if roles is None:
        roles = step.get("conditions")
    if not isinstance(roles, Mapping) or any(role not in roles for role in CONDITION_ROLES):
        return False
    try:
        normalized = {role: canonical_smiles(roles[role]) for role in CONDITION_ROLES}
        reactants = set(_declared_smiles(step.get("reactants", ())))
        reagents = set(_declared_smiles(step.get("reagents", ())))
        product = canonical_smiles(step.get("product"))
    except (ValueError, TypeError):
        return False
    if normalized["aryl halide"] not in reactants or FIXED_PARTNER not in reactants:
        return False
    mixture = reactants | reagents
    expected = set(normalized.values()) | {FIXED_PARTNER, FIXED_PRECATALYST}
    if mixture != expected:
        return False
    return product in _coupling_products(normalized["aryl halide"])
