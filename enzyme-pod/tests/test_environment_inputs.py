"""Episode input protection and lossless compact observations; synthetic only."""
import json
from pathlib import Path

import pytest

from enzyme_environment.inputs import Episode
from enzyme_environment.policy import Audit,Policy


def fixture(tmp_path):
    # Reuse the benchmark's canonical synthetic fixture instead of a second
    # task/model schema or a real experimental dataset.
    from enzyme_benchmark.cli import main
    folder=tmp_path/"synthetic"
    assert main(["demo","--output",str(folder)])==0
    for name in ("agent","python/bin","deps"):(tmp_path/name).mkdir(parents=True)
    (tmp_path/"agent/run_agent.py").write_text("# fixture\n")
    (tmp_path/"python/bin/python3").write_text("fixture")
    runtime={"schema_version":"enzyme-native-runtime/1","agent_source":str(tmp_path/"agent"),"agent_revision":"a"*40,
        "python_root":str(tmp_path/"python"),"site_packages":str(tmp_path/"deps"),"bubblewrap":"/usr/bin/true","limit_python":"/usr/bin/python3"}
    (folder/"runtime.json").write_text(json.dumps(runtime))
    sha=json.loads((folder/"report.json").read_text())["synthetic_model_sha256"]
    cfg={"schema_version":"enzyme-environment-episode/1","runtime":"runtime.json","task":"task.json","candidates":"candidates.csv",
        "predictor":{"kind":"linear","path":"frozen_models.synthetic.json","sha256":sha},"output":"result","backend":"offline","condition":"base"}
    path=folder/"episode.json"
    path.write_text(json.dumps(cfg))
    return path,cfg


def test_valid_episode_reuses_canonical_benchmark_contract(tmp_path):
    path,_=fixture(tmp_path)
    episode=Episode.from_file(path)
    assert len(episode.candidates)==20 and episode.sources_unchanged()
    (path.parent/"candidates.csv").write_text("tampered")
    assert not episode.sources_unchanged()


@pytest.mark.parametrize("key,value",[("unknown",1),("backend","other"),("condition","other"),("role_rounds",True),
    ("observation_format","unknown"),("budget",{"unbounded":True}),("practice",{"answers":"labels.synthetic.csv"}),
    ("output","."),("backend","live")])
def test_invalid_episode_fails_before_output_creation(tmp_path,key,value):
    path,cfg=fixture(tmp_path)
    cfg[key]=value
    path.write_text(json.dumps(cfg))
    with pytest.raises((ValueError,TypeError)):Episode.from_file(path)
    assert not (path.parent/"result").exists()


def test_compact_view_is_lossless_and_keeps_full_internal_sequences(tmp_path):
    path,_=fixture(tmp_path)
    episode=Episode.from_file(path)
    audit=Audit(tmp_path/"audit.jsonl")
    try:
        policy=Policy({"task":[episode.task.to_dict()],"candidates":episode.candidates},tmp_path/"selection",audit,
            predictor=episode.predictor,compact_candidates=True)
        view=policy.tool("benchmark_read",{"dataset":"candidates"})
        assert view["omitted_redundant_fields"]==["sequences"]
        by_id={r["candidate_id"]:r for r in episode.candidates}
        for row in view["rows"]:
            assert set(row)=={"candidate_id","mutation"}
            assert by_id[row["candidate_id"]]["mutation"]==row["mutation"]
            assert "sequences" in by_id[row["candidate_id"]]
    finally:audit.close()
