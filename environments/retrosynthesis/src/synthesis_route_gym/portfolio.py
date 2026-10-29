"""Executable scientific portfolio tasks with explicit evidence boundaries."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Callable

from rdkit import Chem, DataStructs
from rdkit.Chem import rdFingerprintGenerator

from .portfolio_conditions import run_condition_task


def _identity(smiles: str) -> str:
    if not isinstance(smiles, str) or not smiles.strip():
        raise ValueError('SMILES must be a nonempty string')
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f'Invalid SMILES: {smiles!r}')
    for atom in mol.GetAtoms():
        atom.SetAtomMapNum(0)
    return Chem.MolToSmiles(mol, canonical=True, isomericSmiles=True)


def _identities(values: list) -> list[str]:
    if not isinstance(values, list):
        raise ValueError('SMILES collections must be lists')
    return sorted({_identity(value) for value in values})


def assess_impurities(task: dict) -> dict:
    """Legacy identity comparison; incomplete labels never create false positives."""
    from .evidence_contracts import SourceRecord
    from .portfolio_impurities import ImpurityQuantity
    predictions = _identities(task.get('predicted_smiles', []))
    proxies = _identities(task.get('proxy_impurities', []))
    measured_input = task.get('measured_impurities')
    if measured_input is None:
        return {'application': 'impurity_analysis', 'evidence_kind': 'predicted_impurity_hypotheses',
                'predicted_impurities': predictions, 'proxy_impurities': proxies,
                'measured_impurities': None, 'metrics': None,
                'evaluation_status': 'no_measured_labels',
                'limitations': ['Product fragments and proxy labels do not establish measured impurities.']}
    source = task.get('measurement_source')
    if not isinstance(source, dict) or any(not isinstance(source.get(key), str)
            or not source[key].strip() or len(source[key]) > 2000 for key in ('url', 'locator')):
        raise ValueError('measurement_source requires a source url and locator')
    source = {'url': SourceRecord.http_source(source['url']), 'locator': source['locator']}
    coverage = task.get('annotation_coverage', 'unknown')
    if not isinstance(coverage, str) or coverage not in {'unknown', 'partial', 'complete_within_assay_scope'}:
        raise ValueError('Unsupported annotation_coverage')
    complete = coverage == 'complete_within_assay_scope'
    method, scope = task.get('assay_method'), task.get('assay_scope')
    if any(value is not None and (not isinstance(value, str) or not value.strip()
                                  or len(value) > 2000) for value in (method, scope)):
        raise ValueError('Assay metadata must be bounded nonblank text')
    limit = task.get('reporting_limit')
    if limit is not None:
        limit = ImpurityQuantity.model_validate(limit).model_dump(mode='json')
    if complete and (limit is None or method is None or scope is None):
        raise ValueError('Complete assay metrics require assay_method, assay_scope and reporting_limit')
    measured = _identities(measured_input)
    true_positives = len(set(predictions) & set(measured))
    known_recall = true_positives / len(measured) if measured else None
    precision = true_positives / len(predictions) if complete and predictions else None
    recall = known_recall if complete else None
    f1 = (2 * precision * recall / (precision + recall) if precision + recall else 0.0
          ) if precision is not None and recall is not None else None
    return {
        'application': 'impurity_analysis', 'evidence_kind': 'measured_impurity_annotations',
        'evidence_status': 'supplied_measurement_claim', 'verification_status': 'not_independently_verified',
        'claims_experimental_validation': False, 'recipe_binding_status': 'not_bound_legacy_helper',
        'predicted_impurities': predictions, 'proxy_impurities': proxies,
        'measured_impurities': measured, 'measurement_source': source,
        'annotation_coverage': coverage, 'assay_method': method, 'assay_scope': scope, 'reporting_limit': limit,
        'evaluation_status': 'evaluated_against_supplied_measured_annotations',
        'metrics': {'precision': precision, 'recall': recall, 'f1': f1,
                    'known_annotation_recall': known_recall, 'true_positives': true_positives,
                    'false_positives': len(predictions) - true_positives if complete else None,
                    'false_negatives': len(measured) - true_positives if complete else None,
                    'unlabeled_predictions': None if complete else len(predictions) - true_positives,
                    'scope': 'supplied_finite_assay_identity_set' if complete else 'known_positive_annotations_only'},
        'limitations': ['Annotation provenance is supplied by the task and requires independent review.',
                       'Partial or unknown coverage does not establish negative labels for unlisted identities.',
                       'Legacy helper has no reaction/recipe binding; use build_impurity_report for route-bound evaluation.',
                       'Finite-assay identity metrics do not establish concentrations or universal impurity absence.'],
    }


def _route_record(route: dict) -> dict:
    route_id = route.get('route_id')
    steps = route.get('steps')
    if not isinstance(route_id, str) or not route_id:
        raise ValueError('route_id must be a nonempty string')
    if isinstance(steps, bool) or not isinstance(steps, int) or steps < 0:
        raise ValueError('steps must be a nonnegative integer')
    cost = route.get('material_cost')
    if cost is not None and (isinstance(cost, bool) or not isinstance(cost, (int, float))
                             or not math.isfinite(cost) or cost < 0):
        raise ValueError('material_cost must be nonnegative, finite, or null')
    if cost is not None and not route.get('cost_currency'):
        raise ValueError('Known material_cost requires a cost_currency')
    return {**route, 'material_cost': cost, 'cost_status': 'unknown' if cost is None else 'supplied_estimate'}


def select_process_routes(task: dict) -> dict:
    """Pareto comparison of supplied material costs and preparative step counts."""
    routes = [_route_record(route) for route in task.get('routes', [])]
    if not routes:
        raise ValueError('At least one route is required')
    if len({route['route_id'] for route in routes}) != len(routes):
        raise ValueError('route_id values must be unique')
    known = [route for route in routes if route['material_cost'] is not None]
    if len({route['cost_currency'] for route in known}) > 1:
        raise ValueError('Normalize cost currency before route comparison')
    def dominates(first: dict, second: dict) -> bool:
        a = first['material_cost'], first['steps']
        b = second['material_cost'], second['steps']
        return all(x <= y for x, y in zip(a, b)) and any(x < y for x, y in zip(a, b))
    nondominated = [route['route_id'] for route in known
                    if not any(dominates(other, route) for other in known)]
    return {
        'application': 'process_route_selection', 'evidence_kind': 'supplied_route_estimates',
        'objectives': ['minimize_material_cost', 'minimize_preparative_steps'],
        'pareto_route_ids': nondominated,
        'dominated_route_ids': [route['route_id'] for route in known if route['route_id'] not in nondominated],
        'unranked_route_ids': [route['route_id'] for route in routes if route['material_cost'] is None],
        'routes': routes,
        'limitations': ['Missing costs are not zero and are excluded from cost dominance comparisons.',
                       'Costs must use the same scale, currency, and inventory snapshot.',
                       'Pareto membership does not establish reaction feasibility or manufacturing readiness.'],
    }


def _bio_record(record: dict) -> dict:
    for field in ('record_id', 'enzyme_name', 'source_url', 'source_locator'):
        if not isinstance(record.get(field), str) or not record[field].strip():
            raise ValueError(f'Biocatalytic record requires {field}')
    if record.get('evidence_kind') not in {'curated_database', 'literature_report'}:
        raise ValueError('Biocatalytic evidence_kind must be curated_database or literature_report')
    reactants = _identities(record.get('reactants', []))
    products = _identities(record.get('products', []))
    if not reactants or not products:
        raise ValueError('Biocatalytic records require reactants and products')
    return {**record, 'reactants': reactants, 'products': products}


def retrieve_biocatalytic_routes(task: dict) -> dict:
    """Legacy product lookup; no query substrates are bound by this interface."""
    target = _identity(task['target_smiles'])
    inventory = set(_identities(task.get('inventory_smiles', [])))
    raw_records = task.get('records')
    if raw_records is None and task.get('records_path'):
        raw_records = json.loads(Path(task['records_path']).read_text())
    if not isinstance(raw_records, list):
        raise ValueError('records or records_path must provide a list of curated transformations')
    threshold = task.get('analogue_threshold', 0.5)
    if isinstance(threshold, bool) or not isinstance(threshold, (int, float)) or not 0 <= threshold <= 1:
        raise ValueError('analogue_threshold must be between 0 and 1')
    records = [_bio_record(record) for record in raw_records]
    if len({r['record_id'] for r in records}) != len(records):
        raise ValueError('record_id values must be unique')
    generator = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048, includeChirality=True)
    target_fp = generator.GetFingerprint(Chem.MolFromSmiles(target))
    candidates = []
    for record in records:
        exact = target in record['products']
        similarity = max(DataStructs.TanimotoSimilarity(target_fp, generator.GetFingerprint(Chem.MolFromSmiles(p)))
                         for p in record['products'])
        if not exact and similarity < threshold:
            continue
        missing = sorted(set(record['reactants']) - inventory)
        candidates.append({
            **record, 'match_kind': 'exact_product' if exact else 'product_similarity_analogue',
            'product_similarity': similarity, 'missing_reactants': missing,
            'inventory_complete': not missing, 'supports_query_transformation': False,
            'supports_recorded_product_identity': exact,
            'query_reaction_binding': 'not_supplied_product_only_query',
            'experimental_yield': None,
            'review_status': 'requires_independent_review',
        })
    candidates.sort(key=lambda row: (row['match_kind'] != 'exact_product',
                                     not row['inventory_complete'], -row['product_similarity'], row['record_id']))
    return {
        'application': 'biocatalytic_synthesis', 'target_smiles': target,
        'evidence_kind': 'curated_transformation_retrieval', 'candidates': candidates,
        'claims_experimental_validation': False,
        'limitations': ['Exact product matching retrieves the recorded reaction, not a validated process.',
                       'No query reactants are supplied; inventory membership cannot bind a query transformation.',
                       'Analogue matches do not establish enzyme activity on the query substrate.',
                       'Inventory membership does not establish enzyme availability, quantities, or conditions.'],
    }


def dispatch_portfolio(task: dict, inventory_validator: Callable[[dict], dict] | None = None) -> dict:
    application = task.get('application')
    handlers = {'condition_optimization': run_condition_task, 'impurity_analysis': assess_impurities,
                'process_route_selection': select_process_routes, 'biocatalytic_synthesis': retrieve_biocatalytic_routes}
    if application == 'inventory_planning':
        if inventory_validator is None:
            raise ValueError('inventory_planning requires an inventory_validator callback')
        return inventory_validator(task)
    if application not in handlers:
        raise ValueError(f'Unknown portfolio application: {application!r}')
    return handlers[application](task)
