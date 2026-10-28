"""Structural checks. Toolkit validity does not establish reaction feasibility."""

from collections import Counter
from rdkit import Chem


def canonical_smiles(value: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 10000:
        raise ValueError("A nonempty SMILES of at most 10000 characters is required")
    mol = Chem.MolFromSmiles(value)
    if mol is None or mol.GetNumAtoms() == 0:
        raise ValueError("Invalid molecular structure")
    clean = Chem.Mol(mol)
    for atom in clean.GetAtoms():
        atom.SetAtomMapNum(0)
    return Chem.MolToSmiles(clean, canonical=True, isomericSmiles=True)


def validate_smarts(value: str) -> str:
    if not value or len(value) > 2000 or Chem.MolFromSmarts(value) is None:
        raise ValueError("Invalid exclusion SMARTS")
    return value


def elements(smiles: str) -> frozenset[int]:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError("Invalid molecular structure")
    return frozenset(atom.GetAtomicNum() for atom in mol.GetAtoms() if atom.GetAtomicNum() > 1)


def element_counts(smiles: str) -> Counter:
    return Counter(atom.GetAtomicNum() for atom in Chem.MolFromSmiles(smiles).GetAtoms() if atom.GetAtomicNum() > 1)


def matches_pattern(smiles: str, smarts: str) -> bool:
    return Chem.MolFromSmiles(smiles).HasSubstructMatch(Chem.MolFromSmarts(smarts))


def reaction_identity(reactants, product) -> tuple:
    counts = Counter(canonical_smiles(value) for value in reactants)
    return tuple(sorted(counts.items())), canonical_smiles(product)
