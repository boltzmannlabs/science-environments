"""Independently compare reported quality decisions with approved thresholds."""

from .common import WorkflowError


def verify_report_policy(tool, inputs, entries):
    if tool["adapter"] not in {"quality", "geometry"}:
        return
    mode = inputs.get("execution_mode", "measurement_only")
    for entry in entries:
        status = entry["status"]
        if status == "invalid":
            continue
        if mode == "measurement_only":
            if status != "measured":
                raise WorkflowError("Measurement-only output unexpectedly makes a pass/reject decision")
        elif mode == "validation" and status == "measured":
            raise WorkflowError("Validation output lacks a pass/reject decision")
        if tool["tool_id"] == "mol_probity" and mode == "validation":
            thresholds = inputs.get("quality_thresholds")
            if isinstance(thresholds, dict):
                failures = []
                for key, bound in thresholds.items():
                    if bound is None:
                        continue
                    metric = key.removeprefix("max_").removeprefix("min_")
                    if entry["metrics"].get(metric) in {None, ""}:
                        raise WorkflowError("An approved quality threshold has no reported metric")
                    value = float(entry["metrics"][metric])
                    if key.startswith("max_") and value > bound or key.startswith("min_") and value < bound:
                        failures.append(key)
                if (status == "passed") == bool(failures):
                    raise WorkflowError("Reported MolProbity decision disagrees with the submitted quality thresholds")
