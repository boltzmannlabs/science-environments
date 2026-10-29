"""Reproducible mixture-aware nearest-neighbour baseline; no default training data."""
from dataclasses import dataclass
from math import sqrt, isfinite


@dataclass
class MixturePredictor:
    material_ids: tuple[str, ...]
    target_unit: str
    version: str = 'nearest-mixture-v1'
    samples: list | None = None

    def fit(self, rows: list[dict]):
        """Train only on source-linked measured labels; features are mass fractions."""
        if not self.material_ids or not self.target_unit or not rows:
            raise ValueError('explicit feature roster, target unit and measured data required')
        checked = []
        for row in rows:
            if row.get('label') != 'measured' or not row.get('source_id') or row.get('unit') != self.target_unit:
                raise ValueError('training target must be source-linked measured value with matching unit')
            if not isinstance(row.get('target'), (int,float)) or not isfinite(row['target']):
                raise ValueError('invalid target')
            x = self._features(row['composition'])
            checked.append((x, row['target'], row['source_id']))
        self.samples = checked
        return self

    def _features(self, composition: dict) -> tuple[float, ...]:
        if set(composition) != set(self.material_ids) or any(not isinstance(v,(int,float)) or isinstance(v,bool) or not isfinite(v) or v < 0 for v in composition.values()) or abs(sum(composition.values())-1) > 1e-6:
            raise ValueError('composition must contain exactly known materials and sum to fraction 1')
        return tuple(composition[i] for i in self.material_ids)

    def predict(self, composition: dict) -> dict:
        if not self.samples:
            return {'status':'insufficient_data','missing_data':['measured training rows']}
        x = self._features(composition)
        distance, y, source = min((sqrt(sum((a-b)**2 for a,b in zip(x, train))), target, sid) for train,target,sid in self.samples)
        return {'status':'success','label':'predicted','value':y,'unit':self.target_unit,'model_version':self.version,'nearest_distance':distance,'applicability':'unestablished; nearest composition is not proof of generalization','uncertainty':{'calibration':'not_established'},'source_ids':[source]}
