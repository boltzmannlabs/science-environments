"""Strict episode inputs shared by local, installed and isolated executions."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import re

from enzyme_benchmark.cached_esm import CachedESMPredictor
from enzyme_benchmark.contracts import TaskContract, validate_candidates
from enzyme_benchmark.core import finite_score, mutation_details, public_candidates, read_csv
from enzyme_benchmark.predictor import FrozenPredictor
from enzyme_environment.policy import strict_json
from enzyme_environment.runtime import NativeRuntime, regular_file
from enzyme_environment.transport import Budget


def local_path(value, base):
    if not isinstance(value,str) or not value.strip() or "\0" in value: raise ValueError("Artifact path must be nonempty text")
    path=Path(value)
    return Path(os.path.abspath(path if path.is_absolute() else base/path))


def checksum(value):
    if not isinstance(value,str) or not re.fullmatch(r"[0-9a-f]{64}",value): raise ValueError("A pinned SHA-256 is required")
    return value


@dataclass
class Episode:
    runtime: NativeRuntime
    task: TaskContract
    candidates: list
    predictor: object
    practice: dict
    output: Path
    backend: str
    condition: str
    observation_format: str
    budget: Budget
    source_hashes: dict
    role_rounds: int = 2

    @classmethod
    def from_file(cls,path):
        path=Path(path).absolute()
        raw=regular_file(path,limit=65536)
        cfg=strict_json(raw)
        required={"schema_version","runtime","task","candidates","predictor","output","backend","condition"}
        optional={"practice","observation_format","budget","role_rounds"}
        if not isinstance(cfg,dict) or not required<=set(cfg) or set(cfg)-required-optional:
            raise ValueError("Unexpected or missing episode configuration fields")
        if cfg["schema_version"]!="enzyme-environment-episode/1": raise ValueError("Unsupported episode schema")
        if cfg["backend"] not in ("offline","live") or cfg["condition"] not in ("base","specialist"):
            raise ValueError("Unknown backend or condition")
        mode=cfg.get("observation_format","compact")
        if mode not in ("compact","full"): raise ValueError("Observation format must be compact or full")
        role_rounds=cfg.get("role_rounds",2)
        if type(role_rounds) is not int or not 1<=role_rounds<=3: raise ValueError("Role rounds must be an integer from one to three")
        base=path.parent
        hashes={str(path):hashlib.sha256(raw).hexdigest()}
        def artifact(name,limit=8388608):
            resolved=local_path(name,base)
            blob=regular_file(resolved,limit=limit)
            hashes[str(resolved)]=hashlib.sha256(blob).hexdigest()
            return resolved,blob
        runtime_path,_=artifact(cfg["runtime"],65536)
        runtime=NativeRuntime.from_file(runtime_path)
        if cfg["backend"]=="live" and runtime.profile is None: raise ValueError("Live execution requires an explicitly supplied authorized profile")
        _,task_raw=artifact(cfg["task"],65536)
        task=TaskContract.from_dict(strict_json(task_raw))
        if task.select_k!=10 or not 10<=task.candidate_count<=200 or task.max_unique_scores>200:
            raise ValueError("The selection environment supports ten selections from ten to two hundred candidates")
        candidate_path,_=artifact(cfg["candidates"])
        candidates=read_csv(candidate_path)
        known=validate_candidates(candidates,task.reference_sequence)
        if len(known)!=task.candidate_count: raise ValueError("Candidate count differs from the task")
        spec=cfg["predictor"]
        if not isinstance(spec,dict) or not {"kind","path","sha256"}<=set(spec) or set(spec)-{"kind","path","sha256","model_kind","pool_fingerprint"}:
            raise ValueError("Unexpected predictor settings")
        _,model_raw=artifact(spec["path"],2097152)
        expected=checksum(spec["sha256"])
        if spec["kind"]=="linear":
            if "pool_fingerprint" in spec: raise ValueError("Pool fingerprint is specific to the cached ESM predictor")
            predictor=FrozenPredictor.from_bytes(model_raw,expected,spec.get("model_kind","substitution_pair_one_hot"),candidates)
            if predictor.reference!=task.reference_sequence: raise ValueError("Model reference differs from task reference")
        elif spec["kind"]=="esm_cache":
            if "model_kind" in spec or "pool_fingerprint" not in spec: raise ValueError("ESM cache requires its pinned pool fingerprint")
            predictor=CachedESMPredictor.from_bytes(model_raw,expected,candidates,task.reference_sequence,
                expected_pool_fingerprint=checksum(spec["pool_fingerprint"]))
        else: raise ValueError("Unknown frozen predictor kind")
        practice={"train":[],"development":[]}
        practice_spec=cfg.get("practice",{})
        if not isinstance(practice_spec,dict) or set(practice_spec)-set(practice): raise ValueError("Only declared train/development practice pages are permitted")
        pool_positions={mutation_details(r["mutation"],task.reference_sequence,r["sequences"])[0] for r in candidates}
        practice_ids=set()
        for name,value in practice_spec.items():
            file,_=artifact(value)
            rows=read_csv(file)
            fields=set(rows[0])
            if not {"candidate_id","mutation","sequences","experimental_score"}<=fields or fields-{"candidate_id","mutation","sequences","experimental_score","position"}:
                raise ValueError("Unexpected practice fields")
            checked=validate_candidates(public_candidates(rows),task.reference_sequence)
            if set(checked)&(set(known)|practice_ids): raise ValueError("Practice IDs overlap candidate or other practice records")
            for row in rows:
                position=mutation_details(row["mutation"],task.reference_sequence,row["sequences"])[0]
                if position in pool_positions: raise ValueError("Practice mutation position overlaps the candidate pool")
                if "position" in row and str(position)!=row["position"]: raise ValueError("Practice position disagrees with its mutation")
                finite_score(row["experimental_score"])
            practice[name]=rows
            practice_ids.update(checked)
        budget_cfg=cfg.get("budget",{})
        if not isinstance(budget_cfg,dict) or set(budget_cfg)-set(Budget.__dataclass_fields__): raise ValueError("Unexpected shared budget settings")
        budget=Budget(**budget_cfg)
        output=local_path(cfg["output"],base)
        if output.exists() or output.parent.resolve()!=output.parent: raise ValueError("Output must be a new directory without symlink aliases")
        if output==runtime.agent_source or output.is_relative_to(runtime.agent_source): raise ValueError("Outputs must stay outside original Agent-Scientist source")
        if runtime.profile is not None and (output==runtime.profile or output.is_relative_to(runtime.profile)):
            raise ValueError("Outputs must stay outside the authorized account profile")
        return cls(runtime,task,candidates,predictor,practice,output,cfg["backend"],cfg["condition"],mode,budget,hashes,role_rounds)

    def sources_unchanged(self):
        try: return all(hashlib.sha256(regular_file(Path(path),limit=8388608)).hexdigest()==sha for path,sha in self.source_hashes.items())
        except (ValueError,OSError): return False
