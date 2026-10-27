# Per-run template contract

Build a JSON object with `reaction_state`, `sources`, `checks` and optional
description, save it as a UTF-8 JSON file, and upload it. The current live
`reaction_template` field takes its storage path. Upload a real binding JSON file
for `template_binding` as well; that path is required by the current live API.
The local worker's ability to accept objects or omit a binding does not imply
that the API accepts the same request. The hosted tool assigns `template_id`,
`version` and status; callers do not supply those fields.

Supply numeric bounds wherever the current template parser requires them,
including measurement-only runs. Bounds must be justified for the represented
state; do not add arbitrary intervals to make an otherwise incomplete template run.

Every check has `check_id`, `type`, `rationale`, `sources`, `evidence_level`.
Evidence levels: `direct_experimental`, `homolog_transfer`, `mechanistic_review`,
`user_defined`. A literature-based rationale is not itself experimental proof
that a newly generated candidate works.

Supported primitives:

- `distance`: two atoms, angstrom bounds.
- `angle` / `burgi_dunitz_angle`: three ordered atoms, middle atom the vertex,
  degrees. A reaction-specific attack angle is not a universal angle cutoff.
- `dihedral`: four ordered atoms, degrees.
- `metal_coordination`: center and explicitly selected coordinating atoms,
  distance intervals; chemistry/state assumptions remain explicit.
- `hydrogen_bond`: donor/acceptor distances, optionally an explicit hydrogen and
  donor–hydrogen–acceptor angle.
- `plane_orientation`: two groups, at least three atoms each; acute best-fit plane angle.
- `coordination_number`: center, possible coordinating atoms, cutoff and count range.
- `centroid_distance`: two atom groups and distance bounds.
- `ensemble_occupancy`: one nested non-occupancy predicate over a multi-model
  ensemble. Workflow candidate ingestion currently requires single-model
  structures; submit ensemble analysis as a separate explicitly prepared input.

Atom selectors use `entity_type`, `chain_id`, `residue_number`, `atom_name` and
optional `component_id`, `insertion_code`, `altloc` or semantic `mapping_key`.
`template_binding.mapping_keys` maps roles to upstream residue keys or explicit
residue locations. Do not substitute a missing mapping by nearest spatial atom.

Record the source DOI/PDB/stable URL, reaction state, units, applicability,
protonation/cofactor/metal/water assumptions for each check. No NFS template
registry: results retain template/binding JSON, evidence report and SHA-256.
