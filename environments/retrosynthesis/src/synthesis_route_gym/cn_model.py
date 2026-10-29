"""Safe, source-scoped C–N screen-hit inference; no synthesis feasibility claim."""
from collections.abc import Mapping, Sequence
from functools import lru_cache
import json
import math
from pathlib import Path

import numpy as np
from rdkit import Chem, rdBase
from rdkit.Chem import rdChemReactions, rdFingerprintGenerator
from .chemistry import canonical_smiles

CN_ROLES = ('aryl', 'amine', 'catalyst', 'base', 'solvent', 'product')
FEATURE_VERSION = 'cn-morgan-radius2-chiral-128-per-role-v1'
MODEL_SCHEMA = 'srg-cn-condition-hit-model-v1'
N_FEATURES = 128 * len(CN_ROLES)
MAX_MODEL_BYTES = 100_000_000
DOMAIN = 'JnJ25 aryl-halide C-N HTE screen; not general synthesis feasibility'
ENDPOINT = 'source_reported_CAD_response_gte_10_not_isolated_yield_or_general_feasibility'


def _json_copy(value, *, limit=None):
    try:
        serialized = json.dumps(value, allow_nan=False)
        if limit is not None and len(serialized.encode()) > limit:
            raise ValueError('Model exceeds serialized size limit')
        return json.loads(serialized)
    except (TypeError, ValueError, RecursionError) as exc:
        raise ValueError('Model must contain bounded finite JSON values; check serialized size') from exc


@lru_cache(maxsize=20000)
def _canonical(value):
    with rdBase.BlockLogs():
        return canonical_smiles(value)


def _normalized(row):
    if not isinstance(row, Mapping):
        raise ValueError('A condition record must be a mapping')
    try:
        return {role:_canonical(row[role]) for role in CN_ROLES}
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError('Six valid molecular condition roles are required') from exc


@lru_cache(maxsize=20000)
def _fingerprint(smiles):
    mol = Chem.MolFromSmiles(smiles)
    generator = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=128, includeChirality=True)
    return tuple(int(v) for v in generator.GetFingerprintAsNumPy(mol))


def cn_features(rows):
    """Fingerprint only six declared structures, regardless of outcome fields."""
    normalized = [_normalized(row) for row in rows]
    return np.asarray([tuple(v for role in CN_ROLES for v in _fingerprint(row[role]))
                       for row in normalized], dtype=np.float32).reshape(len(rows), N_FEATURES)


@lru_cache(maxsize=20000)
def _cn_products(aryl, amine):
    products = []
    with rdBase.BlockLogs():
        remaining = 32
        for hydrogens in (2,1):
            if not remaining:
                break
            template = f'[c:1]-[Cl,Br,I].[N;H{hydrogens}:2]>>[c:1]-[N;H{hydrogens-1}:2]'
            transformation = rdChemReactions.ReactionFromSmarts(template)
            results = transformation.RunReactants((Chem.MolFromSmiles(aryl), Chem.MolFromSmiles(amine)), maxProducts=remaining)
            remaining -= len(results)
            for group in results:
                for mol in group:
                    try:
                        Chem.SanitizeMol(mol)
                        products.append(_canonical(Chem.MolToSmiles(mol, isomericSmiles=True)))
                    except (ValueError, RuntimeError):
                        continue
    return frozenset(products)


def cn_domain_matches(row):
    """Check the encoded aryl C–N edit; this is not chemical certification."""
    try:
        values = _normalized(row)
        return values['product'] in _cn_products(values['aryl'], values['amine'])
    except (TypeError, ValueError, RuntimeError):
        return False


def _finite_number(value, minimum=None, maximum=None):
    if type(value) not in {int, float} or not math.isfinite(value):
        return False
    return (minimum is None or value >= minimum) and (maximum is None or value <= maximum)


def _tree(tree):
    fields = {'left', 'right', 'feature', 'threshold', 'value'}
    if not isinstance(tree, dict) or set(tree) != fields or any(not isinstance(tree[k],list) for k in fields):
        raise ValueError('Invalid forest tree fields')
    size = len(tree['left'])
    if not 1 <= size <= 100000 or any(len(tree[k]) != size for k in fields):
        raise ValueError('Invalid forest tree size')
    parents = [0]*size
    for index in range(size):
        left, right, feature = (tree[k][index] for k in ('left','right','feature'))
        if any(type(v) is not int for v in (left,right,feature)):
            raise ValueError('Tree indices must be integers')
        if not _finite_number(tree['threshold'][index]) or not _finite_number(tree['value'][index],0,1):
            raise ValueError('Invalid probability tree value')
        if left == right == -1:
            continue
        if not (index < left < size and index < right < size and left != right and 0 <= feature < N_FEATURES):
            raise ValueError('Invalid or cyclic tree children')
        parents[left] += 1
        parents[right] += 1
    if any(value != 1 for value in parents[1:]):
        raise ValueError('Tree must be connected with one parent per node')


def _metadata(raw):
    if not isinstance(raw,dict):
        raise ValueError('Model metadata is required')
    required = {'model_version','training_component_smiles','substrate_similarity_threshold','endpoint'}
    optional = {'source','provenance','training_row_count','training_data_sha256','split_sha256',
                'selected_config','evaluation_scope','calibration_scope'}
    if not required <= set(raw) or set(raw)-required-optional:
        raise ValueError('Invalid model metadata fields')
    if not isinstance(raw['model_version'],str) or not 1 <= len(raw['model_version'].strip()) <= 200:
        raise ValueError('Invalid model version')
    if raw['endpoint'] != ENDPOINT:
        raise ValueError('Model endpoint must match the source-specific CAD screen hit')
    if not _finite_number(raw['substrate_similarity_threshold'],0,1):
        raise ValueError('Invalid substrate similarity threshold')
    known = raw['training_component_smiles']
    if not isinstance(known,dict) or set(known) != set(CN_ROLES):
        raise ValueError('Training component identities must cover all six roles')
    normalized = {}
    for role, values in known.items():
        if not isinstance(values,list) or not 1 <= len(values) <= 20000:
            raise ValueError('Invalid training component identities')
        try:
            canonical = [_canonical(value) for value in values]
        except (TypeError,ValueError) as exc:
            raise ValueError('Invalid training molecular structure') from exc
        normalized[role] = sorted(set(canonical))
    return {**raw, 'training_component_smiles':normalized}


def _calibration(raw):
    if raw is None:
        return
    if not isinstance(raw,dict) or set(raw) != {'kind','x','y'} or raw['kind'] != 'isotonic':
        raise ValueError('Invalid calibration specification')
    x,y = raw['x'],raw['y']
    if (not isinstance(x,list) or not isinstance(y,list) or not 2 <= len(x) <= 100000
            or len(x) != len(y) or any(not _finite_number(v,0,1) for v in x+y)
            or any(a>=b for a,b in zip(x,x[1:])) or any(a>b for a,b in zip(y,y[1:]))):
        raise ValueError('Invalid monotone calibration arrays')


def export_classifier(estimator, metadata, calibration=None):
    """Export RF/ExtraTrees class-one leaf probabilities as numeric JSON."""
    if (getattr(estimator,'n_features_in_',None) != N_FEATURES
            or list(getattr(estimator,'classes_',[])) != [0,1]
            or not hasattr(estimator,'estimators_')):
        raise ValueError('Expected a fitted binary forest with the declared features')
    trees = []
    for fitted in estimator.estimators_:
        tree = fitted.tree_
        values = tree.value[:,0,:]
        total = values.sum(axis=1)
        if values.shape[1] != 2 or np.any(total <= 0):
            raise ValueError('Invalid classifier leaf class counts')
        trees.append({'left':tree.children_left.tolist(),'right':tree.children_right.tolist(),
            'feature':tree.feature.tolist(),'threshold':tree.threshold.tolist(),
            'value':(values[:,1]/total).tolist()})
    artifact = {'schema_version':MODEL_SCHEMA,'feature_version':FEATURE_VERSION,
        'n_features':N_FEATURES,'trees':trees,'metadata':metadata,'calibration':calibration}
    return CNConditionModel(artifact).artifact


def _unique_object(pairs):
    result = {}
    for key,value in pairs:
        if key in result:
            raise ValueError('Duplicate model JSON key')
        result[key] = value
    return result


class CNConditionModel:
    """Read-only host model; outputs remain source-specific predicted hit scores."""
    def __init__(self, artifact):
        raw = _json_copy(artifact, limit=MAX_MODEL_BYTES)
        if (not isinstance(raw,dict) or set(raw) != {'schema_version','feature_version','n_features',
                'trees','metadata','calibration'} or raw['schema_version'] != MODEL_SCHEMA
                or raw['feature_version'] != FEATURE_VERSION or type(raw['n_features']) is not int
                or raw['n_features'] != N_FEATURES):
            raise ValueError('Unsupported C-N model or feature contract')
        if not isinstance(raw['trees'],list) or not 1 <= len(raw['trees']) <= 2048:
            raise ValueError('A bounded nonempty forest is required')
        if sum(len(t['left']) for t in raw['trees']
               if isinstance(t,dict) and isinstance(t.get('left'),list)) > 2_000_000:
            raise ValueError('Forest exceeds node limit')
        for tree in raw['trees']:
            _tree(tree)
        _calibration(raw['calibration'])
        self._artifact = {**raw,'metadata':_metadata(raw['metadata'])}
        self._known = {role:frozenset(values) for role,values in self.metadata['training_component_smiles'].items()}
        self._substrates = {role:np.asarray([_fingerprint(value) for value in values],dtype=bool)
                            for role,values in self._known.items() if role in {'aryl','amine'}}

    @classmethod
    def load(cls, path):
        path = Path(path)
        with path.open('rb') as stream:
            data = stream.read(MAX_MODEL_BYTES+1)
        if len(data) > MAX_MODEL_BYTES:
            raise ValueError('C-N model exceeds the 100 MB limit')
        try:
            raw = json.loads(data, object_pairs_hook=_unique_object,
                parse_constant=lambda value: (_ for _ in ()).throw(ValueError('Nonfinite model number')))
        except (TypeError,ValueError,UnicodeDecodeError,RecursionError) as exc:
            raise ValueError('Invalid finite JSON model') from exc
        return cls(raw)

    @property
    def artifact(self):
        return _json_copy(self._artifact)

    @property
    def metadata(self):
        return _json_copy(self._artifact['metadata'])

    def _raw_predict_array(self, features):
        total = np.zeros(len(features))
        for tree in self._artifact['trees']:
            left,right = np.asarray(tree['left']),np.asarray(tree['right'])
            indices,thresholds = np.asarray(tree['feature']),np.asarray(tree['threshold'])
            nodes = np.zeros(len(features),dtype=int)
            active = np.flatnonzero(left[nodes] != -1)
            while len(active):
                current = nodes[active]
                nodes[active] = np.where(features[active,indices[current]] <= thresholds[current],left[current],right[current])
                active = np.flatnonzero(left[nodes] != -1)
            total += np.asarray(tree['value'])[nodes]
        return total/len(self._artifact['trees'])

    def _calibrate(self, scores):
        calibration = self._artifact['calibration']
        return scores if calibration is None else np.interp(scores,calibration['x'],calibration['y'])

    def _reason(self, row):
        if not cn_domain_matches(row):
            return 'outside_structural_domain'
        if any(row[role] not in self._known[role] for role in ('catalyst','base','solvent')):
            return 'unseen_condition_component'
        threshold = self._artifact['metadata']['substrate_similarity_threshold']
        for role,known in self._substrates.items():
            fingerprint = np.asarray(_fingerprint(row[role]),dtype=bool)
            union = np.logical_or(known,fingerprint).sum(axis=1)
            similarity = np.logical_and(known,fingerprint).sum(axis=1)/np.maximum(union,1)
            if float(np.max(similarity)) < threshold:
                return 'substrate_similarity_below_threshold'
        return None

    def predict(self, rows):
        if not isinstance(rows,Sequence) or isinstance(rows,(str,bytes)) or len(rows)>1000:
            raise ValueError('Expected at most 1000 condition records')
        normalized = [_normalized(row) for row in rows]
        reasons = [self._reason(row) for row in normalized]
        eligible = [index for index,reason in enumerate(reasons) if reason is None]
        scores = self._raw_predict_array(cn_features([normalized[index] for index in eligible])) if eligible else []
        raw_predicted = dict(zip(eligible,scores))
        predicted = dict(zip(eligible,self._calibrate(scores)))
        metadata = self._artifact['metadata']
        kind = ('uncalibrated_forest_score' if self._artifact['calibration'] is None else
                'heldout_isotonic_not_transfer_guarantee')
        return [{**({'id':row['id']} if 'id' in row else {}),
            'status':'scored' if index in predicted else 'abstained',
            'hit_score':float(predicted[index]) if index in predicted else None,
            'raw_hit_score':float(raw_predicted[index]) if index in raw_predicted else None,
            'reason':reasons[index], 'model_version':metadata['model_version'],
            'domain':DOMAIN,'calibration_kind':kind,'evidence_status':'predicted'}
            for index,row in enumerate(rows)]
