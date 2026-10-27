"""Audited candidate-to-input conversions; scientific schemas stay canonical."""
from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
import zipfile

from .contracts import ResearchError, digest, identifier, safe_data


def prepare_input(service, campaign, job_name, candidate_ids, *, structure_ids=None):
    state = service.store.status(campaign)
    if job_name not in state["task"]["allowed_jobs"]:
        raise ResearchError("Input preparation requested an unapproved job")
    candidates = {c["candidate_id"]: c for c in state["candidates"]}
    if (not isinstance(candidate_ids, list) or not candidate_ids or any(not isinstance(c, str) for c in candidate_ids)
            or len(candidate_ids) != len(set(candidate_ids)) or set(candidate_ids) - set(candidates)):
        raise ResearchError("Input preparation requires explicit unique known candidates")
    catalogue = json.loads((Path(service.settings["catalogue_root"]) / "tool-contracts.v1.json").read_bytes())
    entry = catalogue.get("tools", {}).get(job_name)
    if not entry or entry.get("execution_blocked") or entry.get("status") != "active":
        raise ResearchError("Input preparation needs an active authoritative tool contract")
    selected = [candidates[c] for c in candidate_ids]
    structural_jobs = {"Solublempnn", "Thermal_MPNN", "Ligand_MPNN", "Placer", "Mol_Probity", "mol_probity",
                       "Catalytic_Geometry", "catalytic_geometry"}
    structure_ids = {} if structure_ids is None else structure_ids
    if (not isinstance(structure_ids, dict) or set(structure_ids) - set(candidate_ids)
            or any(not isinstance(value, str) for value in structure_ids.values())
            or (structure_ids and job_name not in structural_jobs)):
        raise ResearchError("structure_ids selects verified versions only for a structure-based tool and its selected candidates")
    coordinates = {}
    if job_name in structural_jobs:
        from .structures import select_structure
        coordinates = {cid: select_structure(service, campaign, cid, structure_ids.get(cid)) for cid in candidate_ids}
        required = {"all_atom"} if job_name in {"Mol_Probity", "mol_probity", "Placer", "Catalytic_Geometry", "catalytic_geometry"} else {"structure"}
        if job_name in {"Placer", "Catalytic_Geometry", "catalytic_geometry"}:
            required.add("ligand")
        for record in coordinates.values():
            missing = required - set(record["capabilities"])
            if missing:
                raise ResearchError("Selected coordinates need " + ", ".join(sorted(missing)) + "; a detected ligand does not establish substrate identity")
    location = service.store.root / campaign / "inputs"
    location.mkdir(parents=True, exist_ok=True)
    csv_headers = service.settings.get("csv_headers")
    if csv_headers is not None and csv_headers != ["Seq_id", "Sequences", "SMILES"]:
        raise ResearchError("Explicit benchmark CSV headers must be Seq_id,Sequences,SMILES in that order")
    key = digest({"job_name": job_name, "candidate_ids": candidate_ids,
                  **({"explicit_csv_headers": csv_headers} if csv_headers is not None else {}),
                  "sequence_sha256": [c["sequence_sha256"] for c in selected], "substrate": state["task"]["substrate"],
                  "structure_ids": {cid: record["structure_id"] for cid, record in coordinates.items()},
                  **({"stability_layout": "thermompnn-integer-auth-gap-index/1"} if job_name == "Thermal_MPNN" else {}),
                  **({"csv_layout": "netsolp-canonical-headers/1"} if job_name == "Netsolp" else {}),
                  **({"csv_layout": "catpred-canonical-headers/1"} if job_name == "Cat_Pred" and csv_headers is None else {}),
                  **({"protein_projection": "protein-only-cif-pdb/1"} if job_name in {"Solublempnn", "Thermal_MPNN"}
                      and any(Path(record["artifact"]["member"]).suffix.lower() in {".cif", ".mmcif"} for record in coordinates.values()) else {}),
                  "contract_sha256": digest(entry)})
    projections, stability_layouts = {}, {}
    if job_name in {"Cat_Pred", "Netsolp", "Protein_Structure_Prediction"}:
        field = "input_csv" if job_name == "Protein_Structure_Prediction" else "input_path"
        suffix = ".csv"
        if csv_headers is not None:
            expected = io.StringIO(newline="")
            writer = csv.writer(expected)
            writer.writerow(csv_headers)
            writer.writerows([c["candidate_id"], c["sequence"], state["task"]["substrate"]["smiles"]] for c in selected)
            expected = expected.getvalue().encode()
            target = location / (key + suffix)
        elif job_name == "Cat_Pred":
            from enzyme_workflow.catpred import requested_pairs
            pairs = requested_pairs({"candidates": candidates}, candidate_ids,
                                    {"smiles": state["task"]["substrate"]["smiles"]})
            expected = io.StringIO(newline="")
            writer = csv.writer(expected)
            writer.writerow(["Seq_id", "Sequences", "SMILES"])
            writer.writerows([pair["candidate_id"], pair["sequence"], pair["smiles"]] for pair in pairs)
            expected = expected.getvalue().encode()
            target = location / (key + suffix)
        else:
            expected = io.StringIO(newline="")
            writer = csv.writer(expected)
            writer.writerow(["Sequence_ID", "Sequences"] if job_name == "Netsolp" else ["seq_id", "sequences"])
            writer.writerows([c["candidate_id"], c["sequence"]] for c in selected)
            expected = expected.getvalue().encode()
            target = location / (key + suffix)
    elif job_name in structural_jobs:
        from .structures import checked_structure_content
        field = "zip_path" if job_name == "Thermal_MPNN" else "input_file_path" if job_name == "Placer" else "input_path"
        suffix = ".zip" if job_name in {"Solublempnn", "Thermal_MPNN", "Mol_Probity", "mol_probity", "Catalytic_Geometry", "catalytic_geometry"} else None
        data = {cid: checked_structure_content(record) for cid, record in coordinates.items()}
        extensions = {cid: Path(record["artifact"]["member"]).suffix.lower() for cid, record in coordinates.items()}
        if job_name in {"Solublempnn", "Thermal_MPNN"}:
            from .protein_projection import project_protein_pdb
            for cid, extension in extensions.items():
                if extension in {".cif", ".mmcif"}:
                    data[cid], projections[cid] = project_protein_pdb(coordinates[cid]["artifact"]["member"], data[cid])
                    extensions[cid] = ".pdb"
        if job_name in {"Solublempnn", "Thermal_MPNN", "Ligand_MPNN"} and any(ext != ".pdb" for ext in extensions.values()):
            raise ResearchError("This tool needs PDB coordinates; ligand-preserving CIF conversion requires a separate reviewed chemistry preparation")
        if job_name == "Thermal_MPNN":
            from .stability import input_layout
            stability_layouts = {cid: input_layout(data[cid], candidates[cid]["sequence"]) for cid in candidate_ids}
        if suffix == ".zip":
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                for cid in candidate_ids:
                    member = zipfile.ZipInfo(cid + extensions[cid], date_time=(1980, 1, 1, 0, 0, 0))
                    archive.writestr(member, data[cid])
            expected = buffer.getvalue()
        else:
            if len(candidate_ids) != 1:
                raise ResearchError("This tool accepts one structure per job; a multi-candidate complex cannot be invented")
            cid = candidate_ids[0]
            suffix, expected = extensions[cid], data[cid]
        target = location / (key + suffix)
    elif job_name == "Boltz2":
        if len(selected) != 1:
            raise ResearchError("Boltz2 Protein_Sequences describes chains in ONE complex, not a batch of candidates")
        return {"job_name": job_name, "candidate_ids": candidate_ids, "input_kind": "inline",
                "experiment_data": {"Protein_Sequences": [selected[0]["sequence"]],
                                    "DNA_Sequences": [], "RNA_Sequences": [],
                                    "SMILES": [state["task"]["substrate"]["smiles"]]},
                "jobs_submitted": 0}
    else:
        raise ResearchError("This tool needs a reviewed input-conversion adapter; no improvised conversion was performed")
    if target.is_symlink():
        raise ResearchError("Prepared input cannot be a symbolic link")
    if target.exists():
        if target.stat().st_size != len(expected) or target.read_bytes() != expected:
            raise ResearchError("Prepared input changed or conflicts with its candidate identities")
    else:
        with target.open("xb") as handle: handle.write(expected)
    value = {"input_id": key, "job_name": job_name, "input_field": field,
             "candidate_ids": candidate_ids, "path": str(target), "sha256": hashlib.sha256(expected).hexdigest(),
             "contract_sha256": digest(entry), "uploaded": False, "jobs_submitted": 0}
    if coordinates:
        value["structure_ids"] = {cid: record["structure_id"] for cid, record in coordinates.items()}
        value["residue_mappings"] = {cid: record["mapping"] for cid, record in coordinates.items()}
        evidence = {cid: record["ligand_verification"] for cid, record in coordinates.items() if record.get("ligand_identity_verified")}
        if evidence: value["ligand_verifications"] = evidence
    if projections:
        value["protein_projections"] = projections
    if stability_layouts:
        value["stability_layouts"] = stability_layouts
    with service.store.transaction() as db:
        service.store.event(db, campaign, "input_prepared", value)
    return value


def upload_input(service, campaign, input_id, experiment_data=None):
    """Upload only a prepared, hash-checked input through the native connector.

    The model supplies an input identifier, not a local path or an approval flag.
    The native handler still validates the file and owns its validation receipt.
    """
    identifier(input_id, "input_id")
    state = service.store.status(campaign)
    prepared = [event["payload"]["data"] for event in state["events"]
                if event["payload"]["event"] == "input_prepared"
                and event["payload"]["data"].get("input_id") == input_id]
    if not prepared or any(value != prepared[0] for value in prepared):
        raise ResearchError("Upload requires an unambiguous prepared input from this campaign")
    value = prepared[0]
    path = Path(value["path"])
    base = service.store.root / campaign / "inputs"
    if (path.parent != base or path.resolve() != path or path.is_symlink() or not path.is_file()
            or not 0 < path.stat().st_size <= 10 * 1024**2
            or hashlib.sha256(path.read_bytes()).hexdigest() != value["sha256"]):
        raise ResearchError("Prepared input is missing, changed or outside this campaign")
    catalogue = json.loads((Path(service.settings["catalogue_root"]) / "tool-contracts.v1.json").read_bytes())
    entry = catalogue.get("tools", {}).get(value["job_name"])
    if (not entry or entry.get("status") != "active" or entry.get("execution_blocked")
            or digest(entry) != value["contract_sha256"]):
        raise ResearchError("The authoritative tool contract changed; prepare and review a new input")
    context = {} if experiment_data is None else experiment_data
    if not isinstance(context, dict) or value["input_field"] in context:
        raise ResearchError("Upload context is a JSON object without the file field; its path comes from the actual upload")
    safe_data(context)
    if value["job_name"] == "Thermal_MPNN":
        from .stability import validate_context
        validate_context(value["stability_layouts"], context)
    key = "upload-" + digest({"input_id": input_id, "experiment_data": context,
                               "validation_approval": service.connector.validation_approval})
    tracked = service.connector.execute(campaign, "boltzmann_upload", {
        "local_path": str(path), "job_name": value["job_name"], "input_field": value["input_field"],
        "experiment_data": context}, operation_key=key)
    result = tracked["result"]
    if tracked["status"] != "completed" or result.get("error"):
        return {"input_id": input_id, "uploaded": False, "jobs_submitted": 0, **tracked}
    from enzyme_workflow.contract_registry import validate_storage_path
    storage = result.get("s3_path")
    validate_storage_path(storage, "uploaded storage path")
    if not storage.startswith(("users/", "users_test/")) or result.get("sha256") != value["sha256"]:
        raise ResearchError("Upload receipt did not verify this input's exact bytes and user storage reference; no job was submitted")
    receipt = {"input_id": input_id, "job_name": value["job_name"], "input_field": value["input_field"],
               "candidate_ids": value["candidate_ids"], "sha256": value["sha256"],
               "call_id": tracked["call_id"], "storage_path": storage, "experiment_data": context}
    with service.store.transaction() as db:
        prior = [json.loads(r[0])["data"] for r in db.execute("SELECT payload FROM events WHERE campaign=?", (campaign,))
                 if json.loads(r[0]).get("event") == "input_uploaded"]
        if receipt not in prior:
            service.store.event(db, campaign, "input_uploaded", receipt)
    return {**receipt, "uploaded": True, "jobs_submitted": 0, "reused": tracked.get("reused", False),
            "experiment_data": {**context, value["input_field"]: storage}}
