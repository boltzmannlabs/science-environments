"""Resolve historical report inputs through explicit native run identities."""
import json
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=4)
def _artifact_aliases(env):
    aliases = {}
    for metadata in list((env / "results").glob("task_*/run_*/provenance.json")) + list(
        (env / "benchmark/evaluation").glob("*/comparisons/provenance.json")
    ):
        for item in json.loads(metadata.read_text()).get("artifacts", []):
            if item.get("original_relative_path"):
                aliases[(metadata.parent / item["original_relative_path"]).resolve()] = (
                    metadata.parent / item["path"]
                ).resolve()
    return aliases


def resolve_artifact(path):
    """Resolve a published legacy artifact name through its recorded provenance."""
    path = Path(path).resolve()
    if path.exists():
        return path
    for ancestor in path.parents:
        if (ancestor / "migration_map.json").is_file():
            return _artifact_aliases(ancestor).get(path, path)
    return path

def historical_result(env, task_id, approach="agent-alone"):
    registry = json.loads((env / "runs/registry.json").read_text())
    matches = [r for r in registry["runs"] if r["task_id"] == task_id
               and r["approach"] == approach and r["source_kind"] == "historical_publication"]
    if len(matches) != 1:
        raise ValueError("Expected one explicitly identified historical execution")
    return env / "results" / task_id / matches[0]["run_folder"]
