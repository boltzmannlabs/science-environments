"""Five local workflow operations; scientific execution stays remote."""


def schema(name, description, properties, required):
    return {"name": name, "description": description, "input_schema": {
        "type": "object", "properties": properties, "required": required, "additionalProperties": False}}


WORKFLOW = {"workflow_id": {"type": "string"}}
SCHEMAS = [
    schema("enzyme_workflow_catalog", "Inspect workflow adapters, capabilities and references to the existing Boltzmann catalogue. No remote job is submitted.", {}, []),
    schema("enzyme_workflow_start", "Persist an approved enzyme workflow plan. Load enzyme_workflow:enzyme-workflow first. No remote job is submitted.",
           {"specification": {"type": "object", "description": "Explicit approved DAG, objective, distinct confirmed experiment labels, tool inputs, dependencies and retry budgets."}}, ["specification"]),
    schema("enzyme_workflow_next", "Prepare one approved step, record an upload, ingest a completed artifact or recover the original submission. Returns existing Boltzmann tool calls; never submits directly.",
           {**WORKFLOW, "action": {"type": "string", "enum": ["inspect", "prepare", "record_upload", "ingest", "retry", "recover_submission"]},
            "step_id": {"type": "string"}, "field": {"type": "string"}, "result": {"type": "object"},
            "local_path": {"type": "string"}, "member": {"type": "string"}, "bindings": {"type": "object"}}, ["workflow_id"]),
    schema("enzyme_workflow_status", "Read persisted steps, candidates, artifacts and event history in the active profile. Does not poll remote services.", WORKFLOW, ["workflow_id"]),
    schema("enzyme_workflow_report", "Export the computational workflow report and candidate table with provenance and acceptance evidence.", WORKFLOW, ["workflow_id"]),
]
