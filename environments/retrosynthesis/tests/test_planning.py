from synthesis_route_gym.planning import run_fixed_workflow
from synthesis_route_gym.environment import SynthesisRouteEnv
from synthesis_route_gym.schemas import Task, InventoryItem, Budget


def expand(smiles, top_k):
    choices = {"CCOC(C)=O": [["CCO", "CC(=O)O"]], "CCO": [["C=C", "O"]]}
    return {"status": "ok", "predictions": [
        {"reactants": values, "product": smiles, "score": 0.8,
         "source": {"tool": "unit-fixture", "version": "1"}} for values in choices.get(smiles, [])]}


def test_fixed_workflow_resolves_every_branch_and_records_true_budget():
    task = Task(task_id="convergence", target="CCOC(C)=O", inventory=tuple(
        InventoryItem(smiles=s) for s in ("C=C", "O", "CC(=O)O")))
    env = SynthesisRouteEnv(task, expand=expand)
    result = run_fixed_workflow(env)
    assert result["method"] == "fixed_workflow"
    assert result["episode"]["usage"]["expansions"] == 2
    assessment = result["episode"]["assessments"][0]
    assert assessment["inventory_complete"] and assessment["graph_valid"]
    assert not assessment["solved"]


def test_fixed_workflow_reports_exhaustion_and_no_invented_solution():
    task = Task(task_id="missing", target="CCOC(C)=O", inventory=(), budget=Budget(max_actions=2))
    result = run_fixed_workflow(SynthesisRouteEnv(task, expand=expand))
    assert not result["episode"]["submitted_route_ids"]
    assert result["episode"]["truncated"]


def test_duplicate_predictions_do_not_duplicate_routes():
    def duplicate(smiles, top_k):
        result = expand(smiles, top_k)
        return {**result, "predictions": result["predictions"] * 2}
    task = Task(task_id="duplicate", target="CCOC(C)=O", inventory=tuple(
        InventoryItem(smiles=s) for s in ("CCO", "CC(=O)O")))
    result = run_fixed_workflow(SynthesisRouteEnv(task, expand=duplicate))
    assert len(result["episode"]["routes"]) == 1
