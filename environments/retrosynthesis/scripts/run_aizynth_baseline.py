"""Run official AiZynthFinder/USPTO and LocalRetro on a shared aspirin task.

Usage (optional isolated environment, no Agent Scientist environment changes):
  python -m venv .venv-aizynth
  .venv-aizynth/bin/pip install aizynthfinder==4.4.1 pyarrow==20.0.0
  PYTHONPATH=src .venv/bin/python scripts/run_aizynth_baseline.py --download

Only the public USPTO ONNX model and templates are downloaded (about 95 MB).
The inventory is locally generated; no commercial-stock download is required.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from urllib.request import urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rdkit import Chem
import yaml

from synthesis_route_gym.adapters import AiZynthFinderAdapter, LocalRetroAdapter
from synthesis_route_gym.adapters.aizynthfinder import normalise_aizynth_route
from synthesis_route_gym.schemas import Budget, Constraints, InventoryItem, RouteCandidate, Task
from synthesis_route_gym.validation import assess_route


PUBLIC_ASSETS = (
    ("uspto_model.onnx", "https://zenodo.org/records/7797465/files/uspto_model.onnx",
     91518243, "b466a436b6a8eceaba8c14ef5e2a88c8"),
    ("uspto_templates.csv.gz", "https://zenodo.org/records/7341155/files/uspto_unique_templates.csv.gz",
     3313598, "e8fb29d4dcd54073658000e212b7845a"),
)


def file_hash(path: Path, algorithm: str = "sha256") -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def provision_assets(folder: Path, download: bool) -> list[dict]:
    folder.mkdir(parents=True, exist_ok=True)
    records = []
    for filename, url, size, md5 in PUBLIC_ASSETS:
        path = folder / filename
        valid = path.exists() and path.stat().st_size == size and file_hash(path, "md5") == md5
        if not valid:
            if not download:
                raise FileNotFoundError(f"Missing verified {filename}; rerun with --download")
            temporary = path.with_suffix(path.suffix + ".part")
            try:
                with urlopen(url, timeout=60) as incoming, temporary.open("wb") as handle:
                    total = 0
                    while chunk := incoming.read(1024 * 1024):
                        total += len(chunk)
                        if total > size:
                            raise ValueError("Download exceeded the published artifact size")
                        handle.write(chunk)
                if temporary.stat().st_size != size or file_hash(temporary, "md5") != md5:
                    raise ValueError("Published asset checksum mismatch")
                temporary.replace(path)
            finally:
                temporary.unlink(missing_ok=True)
        records.append({"name": filename, "url": url, "size_bytes": size,
                        "published_md5": md5, "sha256": file_hash(path)})
    return records


def make_task() -> Task:
    return Task(task_id="aspirin-inventory-baseline-v1", target="CC(=O)Oc1ccccc1C(=O)O",
                inventory=tuple(InventoryItem(smiles=smiles, source="frozen_demo_inventory") for smiles in (
                    "O=C(O)c1ccccc1O", "CC(=O)OC(C)=O", "CC(=O)Cl", "CC(=O)O")),
                constraints=Constraints(max_steps=1),
                budget=Budget(max_actions=10, max_expansions=1, max_wall_seconds=60, top_k=5))


def make_config(folder: Path, task: Task) -> Path:
    inchikeys = [Chem.MolToInchiKey(Chem.MolFromSmiles(item.smiles)) for item in task.inventory]
    stock = folder / "inventory.txt"
    stock.write_text("\n".join(inchikeys) + "\n")
    config = {
        "expansion": {"uspto": {"type": "template-based",
            "model": str(folder / "uspto_model.onnx"),
            "template": str(folder / "uspto_templates.csv.gz"), "cutoff_number": task.budget.top_k}},
        "stock": {"benchmark_inventory": str(stock)},
        "search": {"max_transforms": 1, "iteration_limit": 1, "time_limit": 60},
        "post_processing": {"max_routes": task.budget.top_k},
    }
    path = folder / "config.yml"
    path.write_text(yaml.safe_dump(config))
    return path


def localretro_routes(result: dict, task: Task) -> list[dict]:
    return [RouteCandidate.model_validate({"route_id": f"localretro-{i}", "target": task.target,
        "steps": [{"step_id": f"localretro-step-{i}", "product": prediction["product"],
                   "reactants": [{"smiles": s} for s in prediction["reactants"]],
                   "proposal_score": prediction["score"],
                   "source_tool": prediction["source"]["tool"],
                   "source_version": prediction["source"]["version"]}]}).model_dump(mode="json")
        for i, prediction in enumerate(result.get("predictions", []))]


def assessed(routes: list[dict], task: Task) -> list[dict]:
    return [{"route": route,
             "assessment": assess_route(task, RouteCandidate.model_validate(route)).model_dump(mode="json")}
            for route in routes]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--aizynth-python", default=".venv-aizynth/bin/python")
    parser.add_argument("--localretro-python", default=
        "/home/boltzmann6/server3_data/boltzmann3/anaconda3/envs/mol_gpu/bin/python")
    parser.add_argument("--output", default="artifacts/adapters/aizynth_baseline")
    args = parser.parse_args()
    folder = Path(args.output).resolve()
    assets = provision_assets(folder, args.download)
    task = make_task()
    (folder / "task.json").write_text(task.model_dump_json(indent=2) + "\n")
    config = make_config(folder, task)
    started = time.monotonic()
    # Preserve venv interpreter symlinks: resolving them bypasses that venv.
    aizynth = AiZynthFinderAdapter(config_path=config, python_executable=Path(args.aizynth_python).absolute(),
        stock_names=("benchmark_inventory",), timeout_seconds=task.budget.max_wall_seconds)
    az_result = aizynth.search(task.target, top_k=task.budget.top_k, max_iterations=1, max_transforms=1)
    az_routes = [normalise_aizynth_route(tree, f"aizynth-{i}", az_result.get("version", "unknown"))
                 for i, tree in enumerate(az_result.get("routes", []))]
    lr_result = LocalRetroAdapter(python_executable=Path(args.localretro_python).absolute(),
        timeout_seconds=task.budget.max_wall_seconds).expand(task.target, top_k=task.budget.top_k)
    report = {"benchmark_kind": "actual_one_target_one_step_smoke_baseline",
        "comparison_scope": "same target, inventory, one root expansion, top-5 proposal cap and 60-second per-method wall cap",
        "limitations": ["One target cannot establish comparative performance.",
                       "Candidate generators differ: official AiZynthFinder USPTO policy versus LocalRetro.",
                       "Inventory closure does not establish reaction feasibility or complete reagent accounting.",
                       "Quantities, yields, conditions and independent chemical review remain unknown."],
        "task": task.model_dump(mode="json"), "model_assets": assets,
        "config_sha256": file_hash(config), "stock_sha256": file_hash(folder / "inventory.txt"),
        "aizynthfinder": {"result": az_result, "routes": assessed(az_routes, task)},
        "localretro": {"result": lr_result, "routes": assessed(localretro_routes(lr_result, task), task)},
        "total_elapsed_seconds": time.monotonic() - started}
    output = folder / "report.json"
    output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    summary = {method: {"status": report[method]["result"]["status"],
                       "routes_returned": len(report[method]["routes"]),
                       "nonzero_route_candidates": sum(bool(x["route"]["steps"])
                                                        for x in report[method]["routes"]),
                       "inventory_complete": sum(x["assessment"]["inventory_complete"]
                                                 for x in report[method]["routes"]),
                       "routes_reviewed": 0, "reviewed_feasible": None}
               for method in ("aizynthfinder", "localretro")}
    print(json.dumps({"report": str(output), **summary}, indent=2))
    return 0 if all(report[m]["result"]["status"] == "ok" for m in summary) else 1


if __name__ == "__main__":
    raise SystemExit(main())
