"""Same numerical predictions and cache ledger across both wire formats."""
import hashlib
import json
import pytest

from enzyme_benchmark.cached_esm import CachedESMPredictor,pool_fingerprint
from enzyme_environment.policy import Audit,Policy


@pytest.mark.parametrize("cache_hit",[False,True])
def test_wire_matrix_and_full_records_are_exactly_equivalent(tmp_path,cache_hit):
    rows=[{"candidate_id":f"X{i}","mutation":f"A{i}C","sequences":"A"*(i-1)+"C"+"A"*(10-i)} for i in range(1,11)]
    raw=("candidate_id,predicted_score,ensemble_score_std,model_count\n"+"".join(f"X{i},{i/7:.17g},0.1,5\n" for i in range(1,11))).encode()
    model=CachedESMPredictor.from_bytes(raw,hashlib.sha256(raw).hexdigest(),rows,"A"*10,
        expected_pool_fingerprint=pool_fingerprint(rows,"A"*10))
    ids=[r["candidate_id"] for r in rows]
    results=[]
    for compact in (False,True):
        audit=Audit(tmp_path/(str(compact)+".jsonl"))
        try:
            policy=Policy({"candidates":rows},tmp_path/str(compact),audit,predictor=model,compact_candidates=compact)
            result=policy.tool("benchmark_score",{"candidate_ids":ids})
            if cache_hit:result=policy.tool("benchmark_score",{"candidate_ids":ids})
            results.append(result)
        finally:audit.close()
    full,matrix=results
    assert [dict(zip(matrix["row_columns"],row)) for row in matrix["rows"]]==full["rows"]
    assert {k:v for k,v in matrix.items() if k not in ("rows","row_columns")}=={k:v for k,v in full.items() if k!="rows"}
    assert len(json.dumps(matrix,separators=(",",":")))<len(json.dumps(full,separators=(",",":")))
