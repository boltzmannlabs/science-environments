"""Private subprocess entrypoint. One JSON request in, one JSON result out.

Heavy dependencies stay in the configured model environment. This module has
no platform imports, cloud job creation, or fallback to an LLM.
"""

from __future__ import annotations

import contextlib
import hashlib
import importlib.metadata
import json
import os
import sys
from pathlib import Path


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def localretro(request: dict) -> dict:
    import torch

    source = Path(request["source_dir"])
    root = Path(request["repo_root"])
    sys.path.insert(0, str(source))
    from LocalRetro import Retrosynthesis

    checkpoint = root / "req_data/LocalRetro_boltz_USPTO_MIT.pth"
    device = torch.device("cpu")
    torch.set_num_threads(1)
    args = {
        "data_dir": str(root / "req_data/USPTO_MIT"),
        "model_path": str(checkpoint),
        "config_path": str(source / "LocalRetro/default_config.json"),
        "device": device,
    }
    model, graph, atoms, bonds, template_info = Retrosynthesis.init_LocalRetro(args)
    result = Retrosynthesis.retrosnythesis(
        request["target_smiles"], model, graph, device, atoms, bonds,
        template_info, top_k=request["top_k"],
    )
    predictions = [{"reactants": row["SMILES"].split("."),
                    "product": request["target_smiles"], "score": float(row["Score"])}
                   for row in result.iloc[1:].to_dict(orient="records")]
    model_sha256 = _sha256(checkpoint)
    return {"status": "ok", "predictions": predictions, "diagnostic": "",
            "version": "sha256:" + model_sha256, "checkpoint_sha256": model_sha256,
            "device": "cpu", "usage": {"model_calls": 1, "candidate_cap": request["top_k"]}}


def aizynthfinder(request: dict) -> dict:
    from aizynthfinder.aizynthfinder import AiZynthExpander, AiZynthFinder

    cls = AiZynthExpander if request["operation"] == "expand" else AiZynthFinder
    finder = cls(configfile=request["config_path"])
    finder.expansion_policy.select(request["expansion_policy"])
    if request.get("filter_policy"):
        finder.filter_policy.select(request["filter_policy"])
    version = importlib.metadata.version("aizynthfinder")
    if request["operation"] == "expand":
        groups = finder.do_expansion(request["target_smiles"], return_n=request["top_k"])
        predictions = []
        for group in groups:
            reaction = group[0]
            score = reaction.metadata.get("policy_probability")
            predictions.append({"reactants": [mol.smiles for mol in reaction.reactants[0]],
                                "product": request["target_smiles"],
                                "score": float(score) if score is not None else None})
        return {"status": "ok", "predictions": predictions, "version": version, "diagnostic": ""}
    if request["stock_names"]:
        finder.stock.select(request["stock_names"])
    else:
        finder.stock.select_all()
    finder.config.search.iteration_limit = request["max_iterations"]
    finder.config.search.max_transforms = request["max_transforms"]
    finder.target_smiles = request["target_smiles"]
    finder.prepare_tree()
    finder.tree_search()
    finder.build_routes()
    stats = getattr(finder, "search_stats", {})
    profiling = getattr(getattr(finder, "tree", None), "profiling", {})
    return {"status": "ok", "predictions": [], "routes": finder.routes.dicts[:request["top_k"]],
            "version": version,
            "usage": {"iterations": stats.get("iterations"), "search_seconds": stats.get("time"),
                      "expansion_calls": profiling.get("expansion_calls"),
                      "reactant_generations": profiling.get("reactants_generations")},
            "diagnostic": "Routes are predictions; stock closure is not chemical feasibility."}


def main() -> None:
    try:
        request = json.loads(sys.stdin.read(200000))
        backend = request.get("backend")
        if backend not in {"localretro", "aizynthfinder"}:
            raise ValueError("Unknown backend.")
        with open(os.devnull, "w") as log_sink:
            with contextlib.redirect_stdout(log_sink), contextlib.redirect_stderr(log_sink):
                result = localretro(request) if backend == "localretro" else aizynthfinder(request)
    except (ModuleNotFoundError, ImportError):
        result = {"status": "unavailable", "predictions": [],
                  "diagnostic": "Required model package is unavailable in the configured Python environment."}
    except FileNotFoundError:
        result = {"status": "unavailable", "predictions": [],
                  "diagnostic": "Required model or configuration artifact is unavailable."}
    except Exception as error:
        result = {"status": "error", "predictions": [],
                  "diagnostic": "Inference failed (" + type(error).__name__ + ")."}
    sys.stdout.write(json.dumps(result, allow_nan=False))


if __name__ == "__main__":
    main()
