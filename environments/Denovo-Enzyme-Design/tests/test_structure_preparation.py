"""Independent software checks for target-independent structural input validation."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
import importlib.util
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'runtime'))
from structure_preparation import audit, verify_mapping, _ca_chirality, _proper_rotation_overlay, _bounded_missing_atom_optimization, parse_backbone, angle, dihedral


def minimal_pair(path):
    positions={
        (1,'N'):(-1.5,1.0,0.0),(1,'CA'):(0.,1.,0.),(1,'C'):(0.,0.,0.),(1,'O'):(0.,-1.,0.),
        (2,'N'):(1.33,0.,0.),(2,'CA'):(1.33,1.,0.),(2,'C'):(2.8,1.,0.),(2,'O'):(2.8,2.,0.),
    }
    rows=[];idx=0
    for ch,shift in (('A',0.),('B',12.)):
        for (pos,atom),(x,y,z) in positions.items():
            idx+=1; residue='ALA' if pos==1 else 'PRO'
            rows.append(f'ATOM  {idx:5d} {atom:<4s} {residue:3s} {ch}{pos:4d}    {x+shift:8.3f}{y:8.3f}{z:8.3f}  1.00  0.00           C\n')
    path.write_text(''.join(rows)+'END\n')


class StructurePreparationInputTests(unittest.TestCase):
    def test_ambiguous_pdb_records_are_not_silently_remapped(self):
        with tempfile.TemporaryDirectory() as root:
            p = Path(root) / 'ambiguous.pdb'
            minimal_pair(p)
            original = p.read_text()
            row = original.splitlines()[0]
            cases = [original.replace(row, row[:26] + 'A' + row[27:], 1),
                     original.replace(row, row[:16] + 'A' + row[17:], 1),
                     'MODEL        1\n' + original + 'ENDMDL\nMODEL        2\n' + original,
                     original.replace('ALA A   1', 'GLY A   1', 1)]
            for content in cases:
                p.write_text(content)
                with self.subTest(content=content[:90]), self.assertRaises(ValueError):
                    parse_backbone(p)

    def test_undefined_geometry_cannot_be_reported_as_a_cis_peptide(self):
        with self.assertRaisesRegex(ValueError, 'Undefined dihedral'):
            dihedral([0,0,0], [1,0,0], [2,0,0], [3,0,0])
        with self.assertRaisesRegex(ValueError, 'Undefined bond angle'):
            angle([0,0,0], [0,0,0], [1,0,0])
        self.assertAlmostEqual(abs(dihedral([0,1,0], [0,0,0], [1,0,0], [1,1,0])), 0)

    @unittest.skipUnless(importlib.util.find_spec('openmm'), 'OpenMM isolated runtime not in this interpreter')
    def test_bounded_internal_context_restores_openmm_api_after_over_budget(self):
        import openmm as mm
        before_min=mm.LocalEnergyMinimizer.__dict__['minimize']
        before_step=mm.LangevinIntegrator.__dict__.get('step')
        integrator=mm.LangevinIntegrator(300,1,0.002)
        with _bounded_missing_atom_optimization(5,0) as counts:
            with self.assertRaisesRegex(RuntimeError,'dynamics budget exceeded'):
                integrator.step(200)
            self.assertEqual(counts['dynamics_steps'],0)
        self.assertIs(mm.LocalEnergyMinimizer.__dict__['minimize'],before_min)
        self.assertIs(mm.LangevinIntegrator.__dict__.get('step'),before_step)

    def test_proper_alignment_recovers_rotation_but_cannot_fit_a_reflection(self):
        points=np.array([[0.,0.,0.],[1.,0.,0.],[0.,2.,0.],[0.,0.,3.]])
        rotation=np.array([[0.,-1.,0.],[1.,0.,0.],[0.,0.,1.]])
        target=points@rotation.T+np.array([5.,2.,-4.])
        before=points.copy()
        shift,fit,center=_proper_rotation_overlay(target,points)
        np.testing.assert_allclose((points+shift)@fit.T+center,target,atol=1e-12)
        self.assertAlmostEqual(np.linalg.det(fit),1.)
        np.testing.assert_array_equal(points,before)
        reflected=points*np.array([-1.,1.,1.])
        shift,fit,center=_proper_rotation_overlay(reflected,points)
        self.assertAlmostEqual(np.linalg.det(fit),1.)
        self.assertGreater(np.linalg.norm((points+shift)@fit.T+center-reflected),0.1)

    def test_planar_backbone_frame_preserves_sidechain_handedness(self):
        anchors=np.array([[1.,0.,0.],[0.,0.,0.],[0.,1.,0.]])
        cb=np.array([0.,0.,1.])
        target=anchors@np.diag([-1.,1.,1.])
        shift,rotation,center=_proper_rotation_overlay(target,anchors)
        placed=(cb+shift)@rotation.T+center
        source_volume=np.linalg.det(np.stack([anchors[0]-anchors[1],anchors[2]-anchors[1],cb-anchors[1]]))
        target_volume=np.linalg.det(np.stack([target[0]-target[1],target[2]-target[1],placed-target[1]]))
        self.assertGreater(source_volume*target_volume,0)
        with self.assertRaisesRegex(ValueError,'collinear'):
            _proper_rotation_overlay(np.zeros((3,3)),np.zeros((3,3)))

    def test_cis_link_and_tied_identity_are_run_inputs_not_hardcoded_positions(self):
        with tempfile.TemporaryDirectory() as root:
            root=Path(root);source=root/'candidate.pdb';reference=root/'reference.pdb';fasta=root/'sequence.fasta'
            minimal_pair(source);minimal_pair(reference);fasta.write_text('>software_test\nAP\n')
            mapping={'chain_ids':['A','B'],'cis_links':[{'left':1,'right':2}],
                     'fixed_identities':{'2':'P'}}
            sequence, candidate, control=verify_mapping(source,reference,fasta,mapping)
            self.assertEqual(sequence,'AP')
            self.assertEqual(sorted(candidate),['A','B'])
            self.assertEqual(candidate['A']['cis_like_links'],[1])
            self.assertEqual(control['B']['cis_like_links'],[1])
            fasta.write_text('>software_test\nAA\n')
            with self.assertRaisesRegex(ValueError,'FASTA/PDB residue mismatch'):
                verify_mapping(source,reference,fasta,mapping)
            mapping['cis_links']=[{'left':2,'right':3}]
            fasta.write_text('>software_test\nAP\n')
            with self.assertRaisesRegex(ValueError,'Unsupported cis-link mapping'):
                verify_mapping(source,reference,fasta,mapping)

    def test_handedness_sign_detects_inverted_non_gly_ca(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/'backbone_plus_cb.pdb'; minimal_pair(p)
            lines=p.read_text().splitlines();extras=[]
            for ch,shift in (('A',0.),('B',12.)):
                extras.append(f'ATOM  {100+int(shift):5d} {"CB":<4s} ALA {ch}{1:4d}    {1.+shift:8.3f}{1.:8.3f}{1.:8.3f}  1.00  0.00           C')
                extras.append(f'ATOM  {101+int(shift):5d} {"CB":<4s} PRO {ch}{2:4d}    {2.+shift:8.3f}{1.:8.3f}{1.:8.3f}  1.00  0.00           C')
            p.write_text('\n'.join(lines[:-1]+extras)+'\nEND\n')
            original=_ca_chirality(p)
            candidate=p.read_text().replace('   1.000   1.000   1.000','   1.000   1.000  -1.000',1)
            p.write_text(candidate)
            changed=_ca_chirality(p)
            self.assertLess(original['A',1]*changed['A',1],0)
            self.assertGreater(original['B',1]*changed['B',1],0)

    def test_existing_reference_gaps_reported_not_invented(self):
        with tempfile.TemporaryDirectory() as root:
            root=Path(root);p=root/'partial.pdb';minimal_pair(p)
            text=p.read_text().replace(' A   2',' A   3').replace(' B   2',' B   3')
            p.write_text(text)
            evidence,_=audit(p,{'chain_ids':['A','B'],'cis_links':[]})
            self.assertEqual(evidence['A']['unmodeled_or_disconnected_pairs'],[[1,3]])
            self.assertEqual(evidence['B']['unmodeled_or_disconnected_pairs'],[[1,3]])

if __name__=='__main__':unittest.main()
