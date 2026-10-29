"""Input-only deterministic screening groups; never imports evaluator records."""
import hashlib
import statistics
from rdkit import Chem, rdBase
from .chemistry import canonical_smiles

PUBLIC_KEYS = frozenset({'task_id','target','partition','track','inventory_exclusions','constraints','budget'})


def _digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def select_route_groups(rows, count=4, *, salt='srg12-development-v1'):
    """Stratify by target size/stereochemistry, retaining all stock siblings.

    Target groups are input identities. They do not assert patent-family or
    scaffold independence; those require a separate curator attestation.
    """
    if type(count) is not int or count < 1 or not isinstance(salt,str) or not salt:
        raise ValueError('Invalid group selection parameters')
    groups, identities = {}, set()
    for row in rows:
        if (not isinstance(row,dict) or set(row)-PUBLIC_KEYS or row.get('partition') != 'development'
                or row.get('track') != 'reference_route'):
            raise ValueError('Expected input-only public development route tasks')
        identity = row.get('task_id')
        if not isinstance(identity,str) or not identity or identity in identities:
            raise ValueError('Expected unique task identities')
        identities.add(identity)
        with rdBase.BlockLogs():
            target = canonical_smiles(row.get('target'))
        groups = {**groups,target:sorted([*groups.get(target,[]),identity])}
    if len(groups) < count:
        raise ValueError('Not enough distinct public target groups')
    sizes = {target:Chem.MolFromSmiles(target).GetNumHeavyAtoms() for target in groups}
    median = statistics.median(sizes.values())
    candidates = [{'group_id':_digest(target),'target':target,'task_ids':groups[target],
        'heavy_atoms':sizes[target],'size_stratum':'large' if sizes[target] > median else 'small',
        'has_stereochemistry':any(char in target for char in ('@','/','\\')),
        'selection_key':_digest(salt+':'+target)} for target in groups]
    ordered = sorted(candidates,key=lambda row:row['selection_key'])
    selected, cells = [], set()
    for row in ordered:
        cell = (row['size_stratum'],row['has_stereochemistry'])
        if cell not in cells and len(selected) < count:
            selected.append(row)
            cells.add(cell)
    for row in ordered:
        if row not in selected and len(selected) < count:
            selected.append(row)
    return sorted(selected,key=lambda row:row['selection_key'])
