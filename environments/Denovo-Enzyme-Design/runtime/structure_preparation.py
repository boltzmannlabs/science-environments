"""Target-independent protein structure preparation and matched geometry audit.

This development adapter prepares a *new assessment model*, not a replacement for a
canonical designed structure. It does not certify catalysis or molecular stability.
Inputs, conserved residue identities and supported cis links are supplied by the run.
"""
from __future__ import annotations
import argparse
from contextlib import contextmanager
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile

import numpy as np

BACKBONE = ('N', 'CA', 'C', 'O')


def _proper_rotation_overlay(target, source):
    """Align column-vector coordinates with a rotation, never a reflection."""
    target, source = np.asarray(target, dtype=float), np.asarray(source, dtype=float)
    if (target.ndim != 2 or target.shape != source.shape or target.shape[1:] != (3,)
            or len(target) < 3 or not np.isfinite(target).all() or not np.isfinite(source).all()):
        raise ValueError('Template alignment needs matched finite 3D anchors')
    target_center, source_center = target.mean(axis=0), source.mean(axis=0)
    x, y = source-source_center, target-target_center
    if np.linalg.matrix_rank(x) < 2 or np.linalg.matrix_rank(y) < 2:
        raise ValueError('Template alignment anchors are collinear')
    u, _, vh = np.linalg.svd(x.T @ y)
    correction = np.diag([1., 1., 1. if np.linalg.det(u @ vh) > 0 else -1.])
    return -source_center, (u @ correction @ vh).T, target_center


def _alignment_key(target, source):
    return np.asarray(target, dtype=float).tobytes(), np.asarray(source, dtype=float).tobytes()


@contextmanager
def _template_alignment_guard(fixer):
    """Versioned, process-local PDBFixer adapter; installed source stays untouched.

    Missing CB atoms are placed using the named N/CA/C frame. An all-backbone
    fit including O can place CB on the wrong side even with det(R)=+1.
    This adapter runs in its own process; concurrent PDBFixer calls in this
    process are unsupported. PDBFixer's private placement API is tested against
    the recorded installation and must be revalidated on dependency changes.
    """
    import pdbfixer.pdbfixer as implementation
    from openmm import unit
    original = implementation._overlayPoints
    anchor_lookup = {}
    for residue, missing in fixer.missingAtoms.items():
        if not any(atom.name == 'CB' for atom in missing):
            continue
        template = fixer._getTemplate(residue.name)
        existing = {atom.name: fixer.positions[atom.index].value_in_unit(unit.nanometer)
                    for atom in residue.atoms()}
        names, target, source = [], [], []
        for atom in template.topology.atoms():
            if atom.name in existing:
                names.append(atom.name)
                target.append(existing[atom.name])
                source.append(template.positions[atom.index].value_in_unit(unit.nanometer))
        if not all(name in names for name in ('N', 'CA', 'C')):
            raise ValueError('Missing named backbone anchors for sidechain reconstruction')
        anchor_lookup[_alignment_key(target, source)] = [names.index(name) for name in ('N', 'CA', 'C')]

    def align(target, source):
        indices = anchor_lookup.get(_alignment_key(target, source))
        if indices is not None:
            target, source = np.asarray(target)[indices], np.asarray(source)[indices]
        return _proper_rotation_overlay(target, source)

    implementation._overlayPoints = align
    try:
        yield
    finally:
        implementation._overlayPoints = original


@contextmanager
def _bounded_missing_atom_optimization(max_iterations, max_dynamics_steps):
    """Bound only PDBFixer's hidden minimizers/dynamics, restore OpenMM APIs.

    An exceeded dynamics budget raises an error rather than silently accepting
    poorly packed atoms. The template checkpoint is already saved by the caller.
    """
    import openmm as mm
    if max_iterations < 1 or max_dynamics_steps < 0:
        raise ValueError('Missing-atom optimization caps must be explicit and nonnegative')
    cls_min, cls_step = mm.LocalEnergyMinimizer, mm.LangevinIntegrator
    original_min = cls_min.__dict__['minimize']
    original_step = cls_step.__dict__.get('step')
    minimize = cls_min.minimize
    step = cls_step.step
    counts = {'minimizations': 0, 'dynamics_steps': 0}

    def bounded_minimize(context, tolerance=10, maxIterations=0):
        counts['minimizations'] += 1
        limit = min(max_iterations, maxIterations) if maxIterations else max_iterations
        return minimize(context, tolerance, limit)

    def bounded_step(integrator, steps):
        if counts['dynamics_steps'] + steps > max_dynamics_steps:
            raise RuntimeError('PDBFixer missing-atom dynamics budget exceeded; template checkpoint retained')
        counts['dynamics_steps'] += steps
        return step(integrator, steps)

    cls_min.minimize = staticmethod(bounded_minimize)
    cls_step.step = bounded_step
    try:
        yield counts
    finally:
        cls_min.minimize = original_min
        if original_step is None:
            del cls_step.step
        else:
            cls_step.step = original_step


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def parse_backbone(path):
    """Read observed PDB positions only; reject duplicate/alternate ambiguous atoms."""
    atoms, names, chains = {}, {}, {}
    models = 0
    for row in Path(path).read_text().splitlines():
        if row.startswith('MODEL '):
            models += 1
            if models > 1:
                raise ValueError('Select a single model before structure preparation')
        if not row.startswith('ATOM  '):
            continue
        if len(row) < 54 or not row[21].strip():
            raise ValueError('Incomplete PDB atom record or blank chain identifier')
        if row[26] != ' ' or row[16] != ' ':
            raise ValueError('Normalize insertion codes and alternate locations with a reversible mapping first')
        chain, position, name = row[21], int(row[22:26]), row[12:16].strip()
        residue = row[17:20].strip()
        if (chain, position) in names and names[chain, position] != residue:
            raise ValueError('Conflicting residue identities at one mapped position')
        names[chain, position] = residue
        chains.setdefault(chain, set()).add(position)
        if name not in BACKBONE:
            continue
        key = (chain, position, name)
        if key in atoms:
            raise ValueError('Duplicate backbone atom: ' + str(key))
        atoms[key] = np.array([float(row[j:j+8]) for j in (30, 38, 46)])
        names[chain, position] = row[17:20].strip()
        chains.setdefault(chain, set()).add(position)
    if not atoms or any(not np.all(np.isfinite(p)) for p in atoms.values()):
        raise ValueError('Missing or nonfinite backbone coordinates')
    if any(any((chain, pos, atom) not in atoms for atom in BACKBONE)
           for chain, positions in chains.items() for pos in positions):
        raise ValueError('Incomplete observed backbone')
    return atoms, names, {key: sorted(val) for key, val in chains.items()}


def angle(a, b, c):
    x, y = np.asarray(a,dtype=float)-b, np.asarray(c,dtype=float)-b
    if not np.isfinite([x,y]).all() or min(np.linalg.norm(x),np.linalg.norm(y)) <= 1e-12:
        raise ValueError('Undefined bond angle: degenerate atomic geometry')
    return float(np.degrees(np.arccos(np.clip(np.dot(x, y)/(np.linalg.norm(x)*np.linalg.norm(y)), -1, 1))))


def dihedral(a, b, c, d):
    x, y, z = np.asarray(a,dtype=float)-b, np.asarray(c,dtype=float)-b, np.asarray(d,dtype=float)-c
    if not np.isfinite([x,y,z]).all() or np.linalg.norm(y) <= 1e-12:
        raise ValueError('Undefined dihedral: degenerate atomic geometry')
    y = y/np.linalg.norm(y)
    x -= np.dot(x, y)*y
    z -= np.dot(z, y)*y
    if min(np.linalg.norm(x),np.linalg.norm(z)) <= 1e-12:
        raise ValueError('Undefined dihedral: collinear atomic geometry')
    return float(np.degrees(np.arctan2(np.dot(np.cross(y, x), z), np.dot(x, z))))


def audit(path, cis_map):
    atoms, names, chains = parse_backbone(path)
    expected = cis_map['chain_ids']
    if sorted(chains) != sorted(expected):
        raise ValueError('Chain mismatch with run-specific mapping')
    stats = {}
    for chain in expected:
        rows, gaps = [], []
        positions = chains[chain]
        for i, j in zip(positions, positions[1:]):
            if j != i + 1:
                gaps.append([i, j]); continue
            p = lambda n, a: atoms[chain, n, a]
            rows.append({'left':i, 'right':j,
                         'CN_A':float(np.linalg.norm(p(i,'C')-p(j,'N'))),
                         'CA_CA_A':float(np.linalg.norm(p(i,'CA')-p(j,'CA'))),
                         'omega_deg':dihedral(p(i,'CA').copy(), p(i,'C').copy(), p(j,'N').copy(), p(j,'CA').copy()),
                         'CA_C_N_deg':angle(p(i,'CA'),p(i,'C'),p(j,'N')),
                         'C_N_CA_deg':angle(p(i,'C'),p(j,'N'),p(j,'CA'))})
        stat={'observed_residues':len(positions),'first_residue':min(positions), 'last_residue':max(positions),
              'backbone_links':len(rows), 'unmodeled_or_disconnected_pairs':gaps, 'links':rows}
        stat['CN_range_A']=[min(x['CN_A'] for x in rows),max(x['CN_A'] for x in rows)] if rows else None
        stat['cis_like_links']=[x['left'] for x in rows if abs(x['omega_deg'])<35]
        stats[chain]=stat
    return stats, names


def verify_mapping(input_path, reference_path, sequence_path, mapping):
    seq=''.join(x.strip() for x in Path(sequence_path).read_text().splitlines() if not x.startswith('>'))
    if not seq or any(c not in 'ACDEFGHIKLMNPQRSTVWY' for c in seq):
        raise ValueError('Invalid target FASTA')
    input_stats,names=audit(input_path,mapping)
    ref_stats,ref_names=audit(reference_path,mapping)
    codes={'A':'ALA','C':'CYS','D':'ASP','E':'GLU','F':'PHE','G':'GLY','H':'HIS','I':'ILE','K':'LYS',
           'L':'LEU','M':'MET','N':'ASN','P':'PRO','Q':'GLN','R':'ARG','S':'SER','T':'THR','V':'VAL','W':'TRP','Y':'TYR'}
    for chain in mapping['chain_ids']:
        target_positions={p for (c,p) in names if c==chain}
        if target_positions != set(range(1,len(seq)+1)):
            raise ValueError('Full contiguous sequence is required for candidate')
        if any(names[chain,p]!=codes[seq[p-1]] for p in target_positions):
            raise ValueError('FASTA/PDB residue mismatch')
        for residue, code in mapping.get('fixed_identities',{}).items():
            if seq[int(residue)-1]!=code:
                raise ValueError('Required identity not retained')
        for link in mapping['cis_links']:
            left,right=link['left'],link['right']
            if right!=left+1 or (chain,right) not in ref_names or (chain,right) not in names:
                raise ValueError('Unsupported cis-link mapping')
            ref_row=next((r for r in ref_stats[chain]['links'] if r['left']==left),None)
            candidate_row=next((r for r in input_stats[chain]['links'] if r['left']==left),None)
            if not ref_row or abs(ref_row['omega_deg'])>=35 or not candidate_row:
                raise ValueError('Cis link not supported by observed reference')
            if names[chain,right]!='PRO' or ref_names[chain,right]!='PRO':
                raise ValueError('This preparation adapter supports cis-before-Pro only; a validated non-Pro cis link needs another preparation route')
    return seq, input_stats, ref_stats


def _positions_nm(topology, positions):
    atom_map={}
    for atom in topology.atoms():
        if atom.name in BACKBONE:
            key=(atom.residue.chain.id,int(atom.residue.id),atom.name)
            if key in atom_map: raise ValueError('Duplicate modeled backbone atom')
            atom_map[key]=(atom.index,positions[atom.index])
    return atom_map


def _ca_chirality(path):
    """Signed N-C-CB tetrahedron at non-Gly CA, with no enzyme-specific labels."""
    parse_backbone(path)
    residues={}
    for row in Path(path).read_text().splitlines():
        if not row.startswith('ATOM  '):
            continue
        key=row[21],int(row[22:26])
        atom=row[12:16].strip()
        item=residues.setdefault(key, {'resname':row[17:20].strip()})
        if atom in ('N','CA','C','CB'):
            if atom in item:
                raise ValueError('Duplicate stereocentre atom at '+str(key))
            item[atom]=np.array([float(row[j:j+8]) for j in (30,38,46)])
    result={}
    for key, atoms in residues.items():
        if atoms['resname']=='GLY':
            continue
        if not all(atom in atoms for atom in ('N','CA','C','CB')):
            raise ValueError('Missing non-Gly stereocentre atoms at '+str(key))
        volume=float(np.linalg.det(np.stack([atoms[atom]-atoms['CA'] for atom in ('N','C','CB')])))
        if not math.isfinite(volume) or abs(volume) <= 1e-8:
            raise ValueError('Undefined C-alpha handedness: degenerate stereocentre at '+str(key))
        result[key]=volume
    return result


def prepare(path, reference, mapping, output, max_iterations):
    from importlib.metadata import version, PackageNotFoundError
    from pdbfixer import PDBFixer
    import openmm as mm
    from openmm import unit
    from openmm.app import ForceField, CutoffNonPeriodic, PDBFile
    print('prepare: read '+str(path),flush=True)
    platform=mm.Platform.getPlatformByName('CPU')
    platform.setPropertyDefaultValue('Threads','2')
    fixer=PDBFixer(filename=str(path),platform=platform)
    fixer.findMissingResidues()
    fixer.missingResidues={}  # Do not invent unobserved reference terminal residues.
    fixer.findNonstandardResidues()
    if fixer.nonstandardResidues:
        raise ValueError('Nonstandard residues need separate chemistry review')
    print('prepare: find/add missing heavy atoms',flush=True)
    fixer.findMissingAtoms()
    control_chirality = _ca_chirality(reference)
    if not control_chirality:
        raise ValueError('No observed reference stereocentres to verify sidechain placement')
    control_sign=1 if sum(v>0 for v in control_chirality.values())>sum(v<0 for v in control_chirality.values()) else -1
    intermediates={}
    def checkpoint(label, topology=None, positions=None):
        dest=output.with_name(output.stem+'_'+label+'.pdb')
        with dest.open('w') as f:PDBFile.writeFile(topology or fixer.topology, positions if positions is not None else fixer.positions, f, keepIds=True)
        inverted={ch:[p for (c,p),v in _ca_chirality(dest).items() if c==ch and np.sign(v)!=control_sign]
                  for ch in mapping['chain_ids']}
        intermediates[label]={'path':str(dest),'sha256':sha(dest),'inverted_ca':inverted}
        print('prepare: checkpoint '+str(dest)+' inversions='+str({ch:len(v) for ch,v in inverted.items()}),flush=True)
        if any(inverted.values()):
            raise ValueError('Chiral inversion at checkpoint '+label+'; no structural promotion')
    with _template_alignment_guard(fixer):
        template_topology, template_positions, _, _ = fixer._addAtomsToTopology(False,False)
        checkpoint('template_only',template_topology,template_positions)
        mode=mapping.get('missing_atom_preparation_mode','bounded_pdbfixer')
        if mode=='bounded_pdbfixer':
            with _bounded_missing_atom_optimization(mapping.get('internal_missing_atom_max_iterations',25),
                                                     mapping.get('internal_missing_atom_max_dynamics_steps',200)) as internal_counts:
                fixer.addMissingAtoms(seed=mapping.get('preparation_seed',42))
        elif mode=='template_only_then_bounded_outer_minimization':
            # Bypass the hidden, potentially expensive packing loop after its
            # bounded regression failed. Explicitly retain the unoptimized
            # stereochemically placed checkpoint for independent assessment.
            fixer.topology, fixer.positions=template_topology,template_positions
            internal_counts={'minimizations':0,'dynamics_steps':0}
        else:
            raise ValueError('Unrecognized missing-atom preparation mode')
    checkpoint('heavy_atoms')
    print('prepare: add hydrogens',flush=True)
    fixer.addMissingHydrogens(pH=mapping['preparation_pH'])
    checkpoint('hydrogenated')
    topology=fixer.topology
    chain_ids=[c.id for c in topology.chains()]
    if sorted(chain_ids)!=sorted(mapping['chain_ids']):
        raise ValueError('Preparation changed chains')
    atoms=list(topology.atoms())
    pos=fixer.positions
    bonds=ForceField('amber14-all.xml')
    print('prepare: create local bonded+short-range model (vacuum cutoff 1 nm)',flush=True)
    system=bonds.createSystem(topology,nonbondedMethod=CutoffNonPeriodic,
                              nonbondedCutoff=1.0*unit.nanometer,constraints=None)
    # Preserve the supplied observed structural context while allowing geometric
    # minimization. Restraints are disclosed as *preparation*, not independent fold.
    fixed=_positions_nm(topology,pos)
    cis_positions={p for link in mapping['cis_links'] for p in (link['left'],link['right'])}
    keep=mm.CustomExternalForce('0.5*k*((x-x0)^2+(y-y0)^2+(z-z0)^2)')
    for label in ('k','x0','y0','z0'):keep.addPerParticleParameter(label)
    for key,(idx,point) in fixed.items():
        k=mapping.get('backbone_restraint_k_kj_mol_nm2', 2500.0)
        if str(key[1]) in mapping.get('fixed_identities',{}):k*=2.0
        if key[1] in cis_positions:
            k=max(k,mapping.get('cis_backbone_restraint_k_kj_mol_nm2',k))
        xyz=point.value_in_unit(unit.nanometers)
        keep.addParticle(idx,[k,*xyz])
    system.addForce(keep)
    torsion=mm.CustomTorsionForce('k*(1-cos(theta-target))')
    torsion.addPerTorsionParameter('k');torsion.addPerTorsionParameter('target')
    for link in mapping['cis_links']:
        for chain in mapping['chain_ids']:
            i,j=link['left'],link['right']
            row=next(r for r in audit(reference,mapping)[0][chain]['links'] if r['left']==i)
            indices=[fixed[chain,p,a][0] for p,a in ((i,'CA'),(i,'C'),(j,'N'),(j,'CA'))]
            torsion.addTorsion(*indices,[mapping.get('cis_torsion_k_kj_mol',1000.0),math.radians(row['omega_deg'])])
    system.addForce(torsion)
    platform=mm.Platform.getPlatformByName('CPU')
    integrator=mm.VerletIntegrator(0.001*unit.picoseconds)
    context=mm.Context(system,integrator,platform,{'Threads':'2'})
    context.setPositions(pos)
    initial_energy=context.getState(getEnergy=True).getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)
    print('prepare: minimize '+str(path),flush=True)
    mm.LocalEnergyMinimizer.minimize(context, tolerance=20*unit.kilojoules_per_mole/unit.nanometer, maxIterations=max_iterations)
    state=context.getState(getPositions=True,getEnergy=True)
    energy=state.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)
    if not math.isfinite(energy):raise ValueError('Nonfinite energy after preparation')
    with output.open('w') as f:PDBFile.writeFile(topology,state.getPositions(),f,keepIds=True)
    print('prepare: wrote '+str(output),flush=True)
    del context, integrator
    def installed_version(name):
        try:
            return version(name)
        except PackageNotFoundError:
            return 'undisclosed: distribution metadata unavailable'
    return {'initial_total_potential_kj_mol':initial_energy,'final_total_potential_kj_mol':energy,
            'tool_versions':{'OpenMM':installed_version('OpenMM'),'PDBFixer':installed_version('pdbfixer')},
            'template_alignment':'named_N_CA_C_for_missing_CB_and_proper_rotations_only',
            'missing_atom_preparation_mode':mode,
            'internal_missing_atom_optimization':{'max_iterations_per_minimization':mapping.get('internal_missing_atom_max_iterations',25),
                                                  'max_dynamics_steps_total':mapping.get('internal_missing_atom_max_dynamics_steps',200),
                                                  'observed_calls_and_steps':internal_counts},
            'preparation_seed':mapping.get('preparation_seed',42),
            'intermediate_files':intermediates,
            'execution_platform':'CPU, 2 threads, including PDBFixer internal preparation',
            'total_potential_includes_restraints':True, 'minimizer_max_iterations':max_iterations,
            'heavy_atom_count':sum(a.element.symbol!='H' for a in atoms), 'atom_count':len(atoms),
            'model':'OpenMM Amber14 local vacuum cutoff 1 nm; *not* a solvent free energy or a folded-state energy; no ligand; pH-dependent protonation provisional',
            'backbone_restraint_k_kj_mol_nm2':mapping.get('backbone_restraint_k_kj_mol_nm2',2500.0),
            'cis_backbone_restraint_k_kj_mol_nm2':mapping.get('cis_backbone_restraint_k_kj_mol_nm2',2500.0),
            'cis_torsion_k_kj_mol':mapping.get('cis_torsion_k_kj_mol',1000.0)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('input','reference','fasta','mapping','outdir'):parser.add_argument('--'+name,required=True,type=Path)
    parser.add_argument('--max-iterations',type=int,default=500)
    args=parser.parse_args()
    mapping=json.loads(args.mapping.read_text())
    if args.max_iterations<1: raise ValueError('At least one iteration required')
    out=args.outdir;out.mkdir(parents=True,exist_ok=False)
    sequence,before,reference_before=verify_mapping(args.input,args.reference,args.fasta,mapping)
    before_files={'input':sha(args.input),'reference':sha(args.reference),'fasta':sha(args.fasta),'mapping':sha(args.mapping)}
    reference_prep=out/'reference_prepared.pdb';candidate_prep=out/'candidate_prepared.pdb'
    runs={}
    try:
        for key,path,dest in (('reference',args.reference,reference_prep),('candidate',args.input,candidate_prep)):
            runs[key]=prepare(path,args.reference,mapping,dest,args.max_iterations)
        candidate_after,_=audit(candidate_prep,mapping)
        reference_after,_=audit(reference_prep,mapping)
        ref_chirality=_ca_chirality(reference_prep)
        candidate_chirality=_ca_chirality(candidate_prep)
        reference_sign=1 if sum(v>0 for v in ref_chirality.values())>sum(v<0 for v in ref_chirality.values()) else -1
        chirality_deviations={label:{chain:[p for (c,p),v in values.items()
                                         if c==chain and np.sign(v)!=reference_sign]
                                     for chain in mapping['chain_ids']}
                             for label,values in (('reference',ref_chirality),('candidate',candidate_chirality))}
        cis_preserved=all(
            any(r['left']==link['left'] and abs(r['omega_deg'])<35 for r in rows[chain]['links'])
            for rows in (candidate_after,reference_after)
            for chain in mapping['chain_ids'] for link in mapping['cis_links'])
        result={'status':'STRUCTURAL_PREPARATION_EXECUTED_NOT_QUALIFIED','inputs_sha256':before_files,
                'output_sha256':{'candidate':sha(candidate_prep),'reference':sha(reference_prep)},
                'prepared_files':{'candidate':{'path':str(candidate_prep),'sha256':sha(candidate_prep)},
                                  'reference':{'path':str(reference_prep),'sha256':sha(reference_prep)}},
                'methods':runs,'candidate_before':before,'candidate_after':candidate_after,
                'reference_before':reference_before,'reference_after':reference_after,
                'cis_map':mapping['cis_links'],'fixed_identities':mapping.get('fixed_identities',{}),
                'supported_cis_links_preserved_after_preparation':cis_preserved,
                'ca_chirality_opposite_to_observed_reference':chirality_deviations,
                'interpretation':'Same algorithm and settings applied to candidate and observed reference. Reference has only observed residues; no terminal coordinates invented. Restraints force local geometry, not independent folding or catalytic activity. Compare all observed peptide links, dihedrals and site mapping before any physical-integrity claim.',
                'qualified':False}
        if not cis_preserved:
            result['status']='PREPARATION_FAILED_SUPPORTED_CIS_LOST'
        elif any(chirality_deviations[label][chain] for label in chirality_deviations
                 for chain in mapping['chain_ids']):
            result['status']='PREPARATION_FAILED_CA_STEREOCHEMISTRY'
    except Exception as exc:
        checkpoints=[{'path':str(p),'sha256':sha(p)} for p in sorted(out.glob('*_template_only.pdb'))
                     +sorted(out.glob('*_heavy_atoms.pdb'))+sorted(out.glob('*_hydrogenated.pdb'))
                     +sorted(out.glob('*_prepared.pdb')) if p.is_file()]
        result={'status':'PREPARATION_FAILED','error':str(exc),'inputs_sha256':before_files,'completed_methods':runs,
                'checkpoint_files':checkpoints,'qualified':False}
    (out/'geometry_evidence.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'status':result['status'],'error':result.get('error'), 'outputs':result.get('output_sha256')},indent=2))
    if result['status'].startswith('PREPARATION_FAILED'):return 2
    return 0

if __name__=='__main__':raise SystemExit(main())
