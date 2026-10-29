---
name: enzyme-research
description: Optimize an existing enzyme through scientific tool selection, hypothesis testing and feedback-driven revision, using the external enzyme_research environment. Not a substitute for independent experimental evaluation.
---

# Tool-using enzyme research

Use the existing authorized Boltzmann connector and authoritative tool catalogue.
The research environment records the investigation; enzyme_workflow executes
immutable segments and verifies artifact/job associations. Do not maintain a
second list of required API inputs.

## Begin with the task

Inspect the sequence, prepared structure, substrate, catalytic mapping, objective,
allowed tools and limits. Start with `enzyme_research_start`. The task defines
whether evidence is synthetic, computational or a protected measured-library
benchmark. Never expose final assay answers to the tested agent.

An example live pilot is parent evaluation, three distinct sequence proposals,
activity/stability/solubility screening, structural checks, then a revised batch
of three. A proposed revision should address a result, not repeat a fixed script.
Sequence changes require new structure-dependent checks. Parent-relative scores
need a comparable parent run; do not manufacture a reference value.

## Adaptive investigation

`enzyme_research_status` supplies candidate identities, actual observations and
previous decisions. In the specialist arm, use `enzyme_research_next` with
action `investigate` and empty `values`. The host calls a dedicated proposer
and critic through the same budgeted model route. They develop one or two
falsifiable hypotheses with a comparator, competing explanation, actual
observation references and one permitted scientific action. The pinned upstream
DiscoveryRSI selection and replay code records the selected investigation.
The coordinator does not supply its own critique scores. Manual `propose`
is available only to synthetic fixture code, not native scientific sessions.
A critic score concerns investigation quality, not predicted or measured enzyme
activity. Later investigations cite actual preceding observations.

Native status/context is a bounded index, not the complete scientific records.
Each view reports its full count, snapshot hash and whether the first 20 records
cover it. To read details, use `enzyme_research_next`, action `inspect`, with
`values` containing `view`, optional `record_id`, `pointer`, `offset`, `limit`
(1-20) and `snapshot_sha256`. Views include candidates, observations, structures,
structure_assessments, ligand_verifications, decisions, calls, prepared_inputs, confirmed_uploads,
tool_contracts and task. Record IDs and hashes are in the index. For example,
view observations, a known observation record_id and pointer `/metrics/<id>`
retrieves that candidate's result. Full records larger than one page require
selecting a smaller field; list fields can be paged. Carry the snapshot hash
across pages; changed snapshots are not combined. Omitted data never imply a
pass. Native specialist roles have the same read-only views inside their shared
model budget and cannot submit jobs through those lookups.

Use a new `plan_segment` for the selected action. Read its tool's exact input
contract. Give explicit candidate IDs and experiment labels. An optimization
round can contain several tool investigations: additional segments carry a
`followup` reason and actual `observation_ids` rather than rewriting the original
hypothesis. Submitted segments are never rewritten. The fixed and base arms do
not receive the specialist loop.

## Execute and observe

`prepare_input` takes the job name and explicit candidate IDs. For file inputs,
`upload_input` takes the returned `input_id` and any non-file experiment settings;
it returns the actual storage path in `experiment_data`. It validates the saved
bytes, uses the original connector and reuses confirmed upload receipts after a
restart. It does not submit a scientific job. An uncertain upload is reconciled,
not repeated. Best-effort warnings require recorded operator approval; the agent
cannot approve them by supplying a flag.

Single-structure preparation accepts EnzyControl (`enzycontrol`, file field
`pdb_path`), DeepAllo (`deepallo`, `input_path`), and RFD3 (`Enzyme_RFD3`,
`input_path`). Use one selected candidate per job. The first two require PDB;
RFD3 accepts PDB or CIF. Coordinate bytes and catalytic residue mappings are
preserved; unsupported formats are not silently renamed. Supply the remaining
scientific parameters from the current catalogue, including EnzyControl's
required seed. Scaffold counts must fit the campaign's remaining allocation.
All listed tools resolve their current wire names from the canonical catalogue;
newly deployed tools do not need another manual activation step.

Advance the segment with `submit`, `poll`, `download`, then `ingest`. Pass the
recorded campaign/workflow/step/submission IDs. Downloads refresh their signed
link inside the host; no signed URL belongs in a plan or report. Ingestion uses
the existing workflow parsers and verified download receipts. Row order is not
a candidate mapping. Empty, partial or mismatched results cannot finish a step.

Sequence-design ingestion transfers verified child sequences to the research
registry with explicit parents. Catalytic changes, invalid substitutions and
duplicates are recorded as rejected; sequence changes require new structures.
After an interrupted transfer, `sync_sequences` resumes from the same completed
workflow/step/submission receipt. Its observation is sequence validation, not
activity or structural quality. No geometry-ready capability is inferred from a
sequence output.
`add_candidates` also permits explicit agent-proposed substitutions, but its
proposed status does not claim a remote generation job occurred.

Validated folding/preparation/docking outputs are attached to their exact input
sequence using `sync_structures` (also run during structure ingestion). These are
coordinate versions of an existing sequence, not extra designed variants. The
original protein sequence must match exactly; changed residue numbers are mapped
by verified single-chain sequence identity. Quality is not inferred from a fold.
For multiple coordinate versions, select one with `structure_ids`, a mapping from
candidate ID to the returned structure_id, in `prepare_input` or `plan_segment`.
The same setting may select a specific version for a structural follow-up.
The frozen supplied parent is selectable as `supplied-` plus the first 20
characters of its frozen structure SHA256.

Detected non-water HETATMs do not prove substrate identity. Such versions retain
`ligand_present_unverified`, not the `ligand` gate required for docking/geometry.
When a returned archive includes a single-molecule 3D SDF for that pose, use
`verify_ligand` with `candidate_id`, `structure_id`, explicit `sdf_member` and
`ligand_selector` (chain_id, integer residue_number, component_id; optional
insertion_code). The host verifies the SDF graph against the exact task SMILES,
including charge/stereochemistry, and maps its heavy atoms to the selected
ligand's actual coordinates. The SDF must belong to the same originally
receipted artifact; an uploaded template or guessed atom ordering is not evidence.
Verification receipts are available through the ligand_verifications context
view. Original structure records remain immutable; selection rechecks the receipt.
Missing SDF/bonds, pose mismatch, ambiguity or missing chemistry dependency keeps
the gate closed. Do not fabricate or copy a molecule file to bypass it. This
operation establishes requested graph/coordinate identity only, not assay-state
correctness, hydrogen coordinates, chemical preparation, quality or catalysis.
Backbone-only output never acquires all-atom capability. CIF files stay CIF; a
PDB-only downstream tool requires a reviewed conversion, not a renamed file.
Automatic coordinate mapping currently supports one exact-sequence protein
chain with unambiguous single-letter chain labels. Other assemblies require
reviewed preparation instead of a guessed mapping.

Quality and geometry results remain attached to the exact tested coordinate
version. A pass on one pose does not validate another pose of the same sequence.
`sync_metrics` resumes metric transfer from a completed workflow receipt without
duplicating observations; it is also performed during metric ingestion.
Rejected sequence outputs remain in the audit record but are not forwarded to
later workflow stages.

ThermoMPNN uses external workflow tool `thermompnn`, referencing the canonical
`Thermal_MPNN` contract. Prepare and upload its ZIP before planning the segment;
chain selection must match the verified structure. Ingestion requires a complete
20-amino-acid saturation table and maps zero-based gap-filled model indices to
the actual author numbering. The resulting stability observation retains a
separate matrix per input coordinate version. Establish deployed output compatibility
using that wrapper's actual outputs; unknown formats fail rather than guess.
To score a registered single-substitution candidate, use `match_stability` with
`observation_id`, `basis_candidate_id`, `structure_id` and `target_candidate_ids`.
It retains the original source prediction and rejects combined mutations,
insertions/deletions and unchanged WT. Never sum single-mutation values or label
the matrix as absolute stability, melting temperature or measured activity.

After metric ingestion, `complete_decision` references the returned observation
IDs. Inspect these results before proposing the next investigation. A timeout
without a job ID remains unresolved; recover the original job rather than
resubmitting. A missing required tool or chemistry mapping remains an explicit
incomplete gate, not a silently skipped check.

## Report the right conclusion

`enzyme_research_report` gives a bounded joined-evidence index, not every raw
matrix or an automatic ranking. Use `inspect_report` for complete candidate
rows, execution_ledger, observation_checks, structure_checks or
ligand_verifications; its values accept
view, record_id, pointer, offset, limit and the report snapshot_sha256. Reads do
not close the native step. Changed artifacts no longer count as usable evidence,
and a changed report snapshot cannot be combined with earlier pages. Original
metrics remain accessible through the observation references in each row.
Report ranks are not applied automatically. A separate frozen fixed-reference
selection procedure can record its own ranks; it does not impose that ranking
rule on either agent arm. Evidence coverage is not a shortlist or completed goal.

Distinguish predicted kinetics, stability changes,
solubility, geometry, structure confidence and docking. Do not turn any of them
into demonstrated catalytic improvement. Independent evaluation uses separately
protected measurements and frozen rules, never the specialist's critique.
Keep negative findings, failures, candidate attrition and total resource use.
