"""Bind independent folding models to sequences without accepting a bad scaffold.

These are provenance and representation checks. Scientific quality comes from
the recorded calculations and independent review, never from parsing a PDB.
"""
from __future__ import annotations

import math
from pathlib import Path

from contracts import _fasta_sequence, _indexed, load_json, verify_artifact, verify_nested

RESIDUES = dict(zip(
    'ALA CYS ASP GLU PHE GLY HIS ILE LYS LEU MET ASN PRO GLN ARG SER THR VAL TRP TYR'.split(),
    'ACDEFGHIKLMNPQRSTVWY'))
INTEGRITY_CHECKS = {'atom_completeness', 'peptide_geometry', 'ca_stereochemistry',
                    'clashes', 'catalytic_mapping', 'assembly_geometry'}


def pdb_chain_sequences(path: Path) -> dict[str, str]:
    """Inspect one normalized PDB model; reject ambiguous or incomplete residues."""
    chains: dict = {}
    models = 0
    for line in path.read_text().splitlines():
        if line.startswith('MODEL '):
            models += 1
            if models > 1:
                raise ValueError('Select one prediction model before assessment')
        if line[:6] != 'ATOM  ':
            continue
        if len(line) < 54 or line[16] != ' ':
            raise ValueError('Normalize alternate locations before assessment')
        residue = line[17:20].strip()
        chain = line[21].strip()
        if residue not in RESIDUES or not chain:
            raise ValueError('Assessment needs mapped canonical protein chains')
        number = (int(line[22:26]), line[26])
        point = [float(line[start:start + 8]) for start in (30, 38, 46)]
        if not all(math.isfinite(v) for v in point):
            raise ValueError('Non-finite assessment coordinates')
        residues = chains.setdefault(chain, {})
        aa, atoms = residues.setdefault(number, (residue, set()))
        atom = line[12:16].strip()
        if aa != residue or atom in atoms:
            raise ValueError('Ambiguous assessment residue or duplicate atom')
        atoms.add(atom)
    for residues in chains.values():
        for aa, atoms in residues.values():
            required = {'N', 'CA', 'C', 'O'} | ({'CB'} if aa != 'GLY' else set())
            if not required.issubset(atoms):
                raise ValueError('Incomplete backbone/CB assessment coordinates')
    if not chains:
        raise ValueError('Assessment model contains no mapped protein atoms')
    return {chain: ''.join(RESIDUES[aa] for aa, _ in residues.values())
            for chain, residues in chains.items()}


def check_assessment_models(models: list, candidates: list, assembly: dict,
                            evaluation_plan_sha256: str, base: Path) -> dict:
    """Validate new model identity and evidence, leaving scientific review separate."""
    by_id = _indexed(models, 'candidate_id')
    known = _indexed(candidates, 'candidate_id')
    if set(by_id) != set(known):
        raise ValueError('Assessment models must cover exactly the current candidates')
    expected_chains = set(assembly['sequence_groups'][0]['chain_ids'])
    for identity, model in by_id.items():
        candidate = known[identity]
        if (model.get('revision') != candidate['revision']
                or model.get('sequence_sha256') != candidate['sequence']['sha256']
                or model.get('generated_structure_sha256') != candidate['structure']['sha256']
                or model.get('basis') != 'independent_sequence_prediction'):
            raise ValueError('Assessment model is not bound to this candidate revision')
        verify_nested(model, base)
        structure = verify_artifact(model['structure'], base)
        if model['structure']['sha256'] == candidate['structure']['sha256']:
            raise ValueError('Generated coordinates cannot be relabeled as an independent prediction')
        if structure.suffix.lower() != '.pdb':
            raise ValueError('Materialize a mapped PDB assessment model; preserve the original output')
        sequence = _fasta_sequence(verify_artifact(candidate['sequence'], base))
        observed = pdb_chain_sequences(structure)
        if set(observed) != expected_chains or any(s != sequence for s in observed.values()):
            raise ValueError('Predicted chain sequences or assembly do not match the candidate')
        provenance = load_json(verify_artifact(model['prediction_record'], base))
        if (provenance.get('sequence_sha256') != candidate['sequence']['sha256']
                or provenance.get('structure_sha256') != model['structure']['sha256']
                or provenance.get('input_basis') != 'sequence'
                or provenance.get('coordinate_input_sha256') != []
                or any(not provenance.get(k) for k in ('method', 'version', 'settings', 'raw_output'))):
            raise ValueError('Independent prediction needs actual sequence-input provenance')
        verify_nested(provenance, base)
        if not verify_artifact(provenance['raw_output'], base).stat().st_size:
            raise ValueError('Independent prediction raw output is empty')
        report = load_json(verify_artifact(model['integrity_report'], base))
        if (report.get('candidate_id') != identity or report.get('revision') != candidate['revision']
                or report.get('sequence_sha256') != candidate['sequence']['sha256']
                or report.get('structure_sha256') != model['structure']['sha256']
                or report.get('evaluation_plan_sha256') != evaluation_plan_sha256
                or report.get('status') != 'PASS'):
            raise ValueError('Assessment geometry report is failed, stale or bound to another model')
        verify_nested(report, base)
        checks = _indexed(report.get('checks', []), 'check_id')
        if not INTEGRITY_CHECKS.issubset(checks):
            raise ValueError('Assessment geometry checks are incomplete')
        for check_id in INTEGRITY_CHECKS:
            check = checks[check_id]
            if check.get('status') != 'PASS' or not check.get('evidence'):
                raise ValueError('Assessment geometry needs passing evidence: ' + check_id)
            for ref in check['evidence']:
                if not verify_artifact(ref, base).stat().st_size:
                    raise ValueError('Empty assessment geometry evidence')
        if not report.get('reference_controls'):
            raise ValueError('Assessment requires matched reference/control evidence')
        for ref in report['reference_controls']:
            if not verify_artifact(ref, base).stat().st_size:
                raise ValueError('Empty assessment reference/control evidence')
    return by_id
