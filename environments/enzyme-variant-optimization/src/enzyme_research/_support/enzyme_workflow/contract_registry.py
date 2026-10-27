"""Workflow metadata references the existing catalogue; it never copies inputs."""

import json
import re
from pathlib import Path, PurePosixPath

from .common import WorkflowError, digest, identifier, validate_data

REGISTRY_PATH = Path(__file__).parent / "contracts" / "tool_registry.json"


def catalogue_root():
    import plugins
    return Path(plugins.__file__).parent / "boltzmann" / "skills" / "boltzmann-tools" / "references"


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise WorkflowError("Authoritative JSON contains duplicate object keys")
        result[key] = value
    return result


def _json_contract(text):
    try:
        return json.loads(text, object_pairs_hook=_unique_object)
    except (json.JSONDecodeError, TypeError) as exc:
        raise WorkflowError("Authoritative JSON contract is malformed") from exc


def _read_contract(reference, root=None):
    if reference is None:
        return None, None
    if not isinstance(reference, dict) or set(reference) - {"path", "section", "entry"}:
        raise WorkflowError("contract_ref accepts only catalogue path and one optional section or entry")
    if "section" in reference and "entry" in reference:
        raise WorkflowError("contract_ref cannot combine a Markdown section and JSON entry")
    relative = reference.get("path")
    validate_storage_path(relative, "contract_ref.path")
    base = (root or catalogue_root()).resolve()
    path = (base / relative).resolve()
    if not path.is_relative_to(base) or not path.is_file():
        raise WorkflowError("Authoritative catalogue reference is missing or outside its root")
    text = path.read_text(encoding="utf-8")
    if "entry" in reference:
        entry_id = identifier(reference["entry"], "catalogue entry")
        document = _json_contract(text)
        if (not isinstance(document, dict) or document.get("schema") != "boltzmann-tool-contracts.v1"
                or document.get("schema_version") != 2 or document.get("status") != "canonical"):
            raise WorkflowError("Tool entry requires the current canonical catalogue, not an audit scaffold")
        tools = document.get("tools")
        entry = tools.get(entry_id) if isinstance(tools, dict) else None
        if not isinstance(entry, dict) or entry.get("job_name") != entry_id:
            raise WorkflowError("Authoritative catalogue entry is missing or has conflicting identity")
        # Hash only the selected authoritative entry. Updates to unrelated tools
        # must not invalidate an otherwise unchanged saved workflow contract.
        text = json.dumps(entry, sort_keys=True, separators=(",", ":"), allow_nan=False)
        return {"path": str(path), "section": None, "entry": entry_id, "sha256": digest(text)}, text
    section = reference.get("section")
    if "section" in reference and (not isinstance(section, str) or not section.strip()):
        raise WorkflowError("Catalogue section must be a nonempty heading")
    if section:
        lines = text.splitlines(keepends=True)
        matches = [i for i, line in enumerate(lines) if line.strip() == section]
        if len(matches) != 1:
            raise WorkflowError("Authoritative catalogue section is missing or ambiguous")
        start = matches[0]
        end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
        text = "".join(lines[start:end])
    return {"path": str(path), "section": section, "sha256": digest(text)}, text


def contract_document(reference, root=None):
    return _read_contract(reference, root)[0]


def catalogue_binding(text):
    """Read routing only from the selected original catalogue section.

    A Mongo collection is diagnostic metadata, not a submit prerequisite.
    Never infer it from a Docker task, tool ID, or job name.
    """
    if text.lstrip().startswith("{"):
        entry = _json_contract(text)
        if not isinstance(entry, dict):
            raise WorkflowError("Catalogue tool entry must be a JSON object")
        job = identifier(entry.get("job_name"), "catalogue job_name")
        submission = entry.get("submission")
        if not isinstance(submission, dict) or submission.get("wire_job_name") != job:
            raise WorkflowError("Catalogue job_name conflicts with its documented wire job name")
        if not isinstance(entry.get("status"), str) or type(entry.get("execution_blocked")) is not bool:
            raise WorkflowError("Catalogue tool entry lacks explicit status and execution policy")
        diagnostics = entry.get("diagnostics", [])
        if not isinstance(diagnostics, list) or any(not isinstance(d, dict) for d in diagnostics):
            raise WorkflowError("Catalogue diagnostics must be a list of documented mappings")
        collections = set()
        for item in diagnostics:
            if item.get("job_name") == job and item.get("mapping_status") == "source_documented":
                value = item.get("collection_name")
                if value is not None:
                    collections.add(identifier(value, "catalogue collection_name"))
        if len(collections) > 1:
            raise WorkflowError("Ambiguous diagnostic collection in the authoritative catalogue entry")
        active = entry["status"] == "active" and not entry["execution_blocked"]
        return {"job_name": job, "collection_name": next(iter(collections), None),
                "backend_status": "active" if active else "pending", "binding_source": "catalogue"}
    rows = re.findall(r"^\|\s*\*\*([^*]+)\*\*\s*\|\s*`([^`]+)`[^\n]*\|\s*$", text, re.MULTILINE)
    jobs = [value for label, value in rows if label == "job_name"]
    if len(jobs) != 1:
        raise WorkflowError("Existing tool needs exactly one job_name in its authoritative catalogue section")
    job = identifier(jobs[0], "catalogue job_name")
    collections = [value for label, value in rows
                   if label in {"Mongo diagnostics collection", "backend task/collection", "collection_name"}]
    if len(collections) > 1:
        raise WorkflowError("Ambiguous diagnostic collection in the authoritative catalogue section")
    collection = identifier(collections[0], "catalogue collection_name") if collections else None
    return {"job_name": job, "collection_name": collection, "backend_status": "active",
            "binding_source": "catalogue"}


def load_registry(overrides=None, extensions=None, *, catalog_root=None):
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))["tools"]
    for name, metadata in (extensions or {}).items():
        identifier(name, "tool name")
        validate_data(metadata)
        if name in registry:
            raise WorkflowError("Extensions cannot replace bundled workflow metadata")
        required = {"stage", "adapter", "requires", "contract_ref"}
        allowed = required | {"adapter_source", "notes"}
        if not isinstance(metadata, dict) or not required <= metadata.keys() or set(metadata) - allowed:
            raise WorkflowError("Extension needs workflow metadata and contract_ref, not a duplicate input schema")
        if metadata["adapter"] not in {"structures", "sequences", "quality", "geometry", "report", "pockets"}:
            raise WorkflowError("Unsupported extension adapter")
        if not isinstance(metadata["requires"], list):
            raise WorkflowError("Extension requires a list of candidate capabilities")
        registry[name] = {**metadata, "backend_status": "pending", "job_name": None,
                          "collection_name": None, "live_verified": False}
    for name, binding in (overrides or {}).items():
        if name not in registry or not isinstance(binding, dict):
            raise WorkflowError(f"Unknown tool binding: {name}")
        if set(binding) - {"job_name", "collection_name", "backend_status", "live_verified", "contract_ref"}:
            raise WorkflowError(f"Unsupported backend binding fields for {name}")
        registry[name].update(binding)
    for name, tool in registry.items():
        tool["tool_id"] = name
        tool.setdefault("live_verified", False)
        document, text = _read_contract(tool["contract_ref"], catalog_root)
        tool["contract_document"] = document
        if tool["backend_status"] == "catalogue":
            if text is None or not any(tool["contract_ref"].get(k) for k in ("section", "entry")):
                raise WorkflowError(f"Existing tool {name} needs a specific authoritative catalogue section or entry")
            tool.update(catalogue_binding(text))
        if tool["backend_status"] not in {"pending", "active"}:
            raise WorkflowError(f"Invalid backend status for {name}")
        if tool["backend_status"] == "active":
            required = ("job_name",) if tool.get("binding_source") == "catalogue" else ("job_name", "collection_name")
            if not all(isinstance(tool.get(k), str) and tool[k].strip() for k in required):
                raise WorkflowError(f"Active tool {name} needs verified {' and '.join(required)}")
    return registry


def validate_storage_path(value, field):
    if not isinstance(value, str) or not value.strip():
        raise WorkflowError(f"{field} must be a nonempty relative storage path")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or "\\" in value or ":" in value:
        raise WorkflowError(f"{field} must be a relative storage path")


def validate_inputs(tool, inputs, *, partial=False):
    """Check durable-data safety, not scientific parameters or API schemas.

    The agent reads the authoritative module; the worker validates scientific
    inputs. Newly documented fields need no second registry update.
    """
    if not isinstance(inputs, dict) or not inputs:
        raise WorkflowError("Tool inputs must be a nonempty JSON object")
    validate_data(inputs)
    return inputs
