"""Evaluator regression fixtures; these are not outputs from a new agent run."""
import copy
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import evaluate as case


def design(mutation='N220Y', cid='C1', rank='1'):
    parent = case.parent_sequence()
    position = int(mutation[1:-1])
    sequence = parent[:position-1] + mutation[-1] + parent[position:]
    return dict(candidate_id=cid, rank=rank, mutation=mutation, sequence=sequence)


class ScientificOutputChecks(unittest.TestCase):
    def setUp(self):
        self.parent = case.parent_sequence()
        self.reference = case.published_reference()

    def invalid(self, rows):
        with self.assertRaises(ValueError):case.validate_selection(rows, self.parent)

    def test_parent_and_all_source_mutations_have_verified_numbering(self):
        self.assertEqual(len(self.parent), 445)
        self.assertEqual(hashlib.sha256(self.parent.encode()).hexdigest(), case.PARENT_SHA256)
        self.assertEqual(len(self.reference), 129)
        self.assertEqual(len(self.reference)-1, 128)
        self.assertEqual([self.parent[i-1] for i in (164,295,353)], ['E','Y','E'])

    def test_valid_shortlist_uses_declared_ranks_not_predicted_or_measured_order(self):
        rows = [design('Q313R','C2','2'), design()]
        result = case.validate_selection(rows, self.parent)
        self.assertEqual([r['candidate_id'] for r in result], ['C1','C2'])

    def test_empty_is_retained_without_claiming_a_successful_design(self):
        self.assertEqual(case.validate_selection([], self.parent), [])
        result=case.summarize([], self.reference)
        self.assertTrue(result['empty_shortlist'])
        self.assertEqual(result['joint_point_rule_counts']['met'], 0)
        self.assertIsNone(result['mean_efficiency_ratio'])

    def test_protected_sites_cannot_be_optimized_for_apparent_stability(self):
        for mutation in ('E164A','Y295A','E353A'):
            with self.subTest(mutation=mutation):self.invalid([design(mutation)])

    def test_reference_sequence_cannot_be_a_designed_candidate(self):
        row=design();row['sequence']=self.parent
        self.invalid([row])

    def test_combined_mutations_are_not_single_mutants(self):
        row=design();row['sequence']='C'+row['sequence'][1:]
        self.invalid([row])

    def test_mutation_label_must_agree_with_actual_sequence(self):
        for label in ('N223Y','N220A','A220Y','n220y'):
            row=design();row['mutation']=label
            with self.subTest(label=label):self.invalid([row])

    def test_invalid_length_and_alphabet(self):
        for sequence in (self.parent[:-1], self.parent+'A', 'X'+self.parent[1:], self.parent.lower()):
            row=design();row['sequence']=sequence
            with self.subTest(sequence=sequence[:12]):self.invalid([row])

    def test_duplicate_ids_and_sequences(self):
        self.invalid([design(), design('Q313R','C1','2')])
        self.invalid([design(), design('N220Y','C2','2')])

    def test_ranks_and_empty_identity(self):
        for rank in ('0','-1','1.0','2','01'):
            with self.subTest(rank=rank):self.invalid([design(rank=rank)])
        self.invalid([design(cid='')])

    def test_shortlist_count_and_columns(self):
        self.invalid([design(cid=str(i),rank=str(i+1)) for i in range(6)])
        row=design();row['predicted_activity']='42'
        self.invalid([row])

    def test_published_reference_not_prediction_is_attached(self):
        result=case.summarize([design()], self.reference)
        measured=result['candidates'][0]['source_measurements']
        self.assertEqual(measured['kcat_over_km_M_inverse_min_inverse'],1570000)
        self.assertEqual(measured['functional_tm_c'],41.74)
        self.assertEqual(result['joint_point_rule_counts']['met'],1)
        self.assertFalse(result['new_experimental_validation'])

    def test_stable_but_less_active_variant_does_not_meet_joint_objective(self):
        result=case.summarize([design('W120F')], self.reference)
        measured=result['candidates'][0]['source_measurements']
        self.assertGreater(measured['functional_tm_delta_c'],0)
        self.assertLess(measured['efficiency_ratio_to_parent'],1)
        self.assertEqual(result['candidates'][0]['joint_point_rule'],'not_met')

    def test_unmeasured_design_remains_unknown_and_denominators_are_visible(self):
        self.assertNotIn('M10C', self.reference)
        result=case.summarize([design('M10C')], self.reference)
        self.assertEqual(result['joint_point_rule_counts']['unknown'],1)
        self.assertEqual(result['not_in_published_table_count'],1)
        self.assertIsNone(result['candidates'][0]['source_measurements'])
        self.assertEqual(result['mean_efficiency_ratio_denominator'],0)

    def test_missing_measurement_is_not_zero(self):
        reference=copy.deepcopy(self.reference)
        reference['N220Y']['tm']='NA'
        result=case.summarize([design()],reference)
        self.assertIsNone(result['candidates'][0]['source_measurements']['functional_tm_c'])
        self.assertEqual(result['joint_point_rule_counts']['unknown'],1)

    def test_censored_low_activity_is_not_an_exact_zero(self):
        reference=copy.deepcopy(self.reference)
        reference['N220Y']['kcatkm']='0'
        result=case.summarize([design()],reference)
        measured=result['candidates'][0]['source_measurements']
        self.assertTrue(measured['at_or_below_detection_limit'])
        self.assertIsNone(measured['kcat_over_km_M_inverse_min_inverse'])
        self.assertEqual(result['mean_efficiency_ratio_denominator'],0)
        self.assertEqual(result['joint_point_rule_counts']['not_met'],1)

    def test_real_published_less_than_detection_limit_is_retained(self):
        result=case.summarize([design('Q19A')],self.reference)
        measured=result['candidates'][0]['source_measurements']
        self.assertEqual(measured['reported_efficiency_text'],'<10')
        self.assertTrue(measured['at_or_below_detection_limit'])
        self.assertIsNone(measured['kcat_over_km_M_inverse_min_inverse'])
        self.assertEqual(result['joint_point_rule_counts']['not_met'],1)

    def test_every_allowed_published_variant_can_be_evaluated(self):
        for mutation in set(self.reference)-{'BglB'}:
            if int(mutation[1:-1]) in case.PROTECTED:continue
            with self.subTest(mutation=mutation):
                rows=case.validate_selection([design(mutation)],self.parent)
                result=case.summarize(rows,self.reference)
                self.assertEqual(result['published_match_count'],1)

    def test_units_are_converted_once_without_equating_unlike_endpoints(self):
        result=case.summarize([design()],self.reference)
        measured=result['candidates'][0]['source_measurements']
        self.assertAlmostEqual(measured['kcat_per_s'],628/60)
        self.assertAlmostEqual(measured['km_M'],0.4*0.001)
        self.assertAlmostEqual(measured['kcat_over_km_M_inverse_s_inverse'],1570000/60)

    def test_invalid_source_numbers_are_not_accepted(self):
        for value in ('NaN','Infinity','-1'):
            reference=copy.deepcopy(self.reference);reference['N220Y']['kcatkm']=value
            with self.subTest(value=value),self.assertRaises(ValueError):
                case.summarize([design()],reference)

    def test_real_csv_entry_point_and_changed_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            selection=Path(directory)/'candidates.csv'
            with selection.open('w',newline='') as handle:
                writer=csv.DictWriter(handle,fieldnames=case.FIELDS)
                writer.writeheader();writer.writerow(design())
            result=case.evaluate(selection)
            self.assertTrue(result['design_constraints_valid'])
            self.assertEqual(result['selection_sha256'],hashlib.sha256(selection.read_bytes()).hexdigest())
            changed=Path(directory)/'changed.csv';changed.write_bytes(case.REFERENCE.read_bytes()+b'\n')
            with self.assertRaises(ValueError):case.evaluate(selection,changed)

    def test_bad_csv_header_does_not_silently_reinterpret_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            selection=Path(directory)/'wrong.csv';selection.write_text('id,sequence\n')
            with self.assertRaises(ValueError):case.evaluate(selection)

    def test_selection_hash_describes_the_bytes_actually_parsed(self):
        with tempfile.TemporaryDirectory() as directory:
            selection=Path(directory)/'fixture.csv'
            with selection.open('w',newline='') as handle:
                writer=csv.DictWriter(handle,fieldnames=case.FIELDS)
                writer.writeheader();writer.writerow(design())
            initial=selection.read_bytes()
            original=case.published_reference
            def change_selection_then_read_reference(path):
                selection.write_text('changed after the selection snapshot was read\n')
                return original(path)
            with patch.object(case,'published_reference',side_effect=change_selection_then_read_reference):
                result=case.evaluate(selection)
            self.assertEqual(result['selection_sha256'],hashlib.sha256(initial).hexdigest())
            self.assertEqual(result['candidates'][0]['mutation'],'N220Y')
            self.assertNotEqual(selection.read_bytes(),initial)

    def test_reference_is_parsed_from_its_verified_snapshot_not_reopened(self):
        source=case.REFERENCE.read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            reference=Path(directory)/'fixture.csv'
            reference.write_text('different file contents after the source snapshot\n')
            with patch.object(Path,'read_bytes',return_value=source) as read:
                indexed=case.published_reference(reference)
                self.assertEqual(read.call_count,1)
            self.assertEqual(len(indexed),129)
            self.assertEqual(indexed['BglB']['kcatkm'],'174000')

    def test_cli_evaluates_a_fixture_without_overwriting_an_earlier_result(self):
        with tempfile.TemporaryDirectory() as directory:
            selection=Path(directory)/'fixture.csv';output=Path(directory)/'evaluation.json'
            with selection.open('w',newline='') as handle:
                writer=csv.DictWriter(handle,fieldnames=case.FIELDS)
                writer.writeheader();writer.writerow(design())
            command=[sys.executable,case.__file__,'--selection',str(selection),'--output',str(output)]
            first=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(first.returncode,0,first.stderr)
            before=output.read_bytes()
            self.assertFalse(json.loads(before)['new_experimental_validation'])
            second=subprocess.run(command,capture_output=True,text=True)
            self.assertNotEqual(second.returncode,0)
            self.assertEqual(output.read_bytes(),before)

    def test_native_specialist_is_data_not_a_second_execution_framework(self):
        definition=json.loads((case.ENV/'specialist/enzyme-variant-specialist.json').read_bytes())
        self.assertFalse(definition['enabled'])
        self.assertTrue(definition['needs_review'])
        self.assertFalse(definition['automatic'])
        self.assertEqual(set(definition['tools']),{'read_file','web_search','web_extract'})
        self.assertEqual(definition['children'],[])
        self.assertNotIn('boltzmann_submit',definition['tools'])


if __name__=='__main__':unittest.main()
