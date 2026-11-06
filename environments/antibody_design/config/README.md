# Antibody task configuration

The `config/` directory contains shared definitions and **nine contract profiles**. Four profiles are retained for retired monoclonal prompts; five correspond to active bispecific tasks. The five active paper-based monoclonal prompts are cataloged separately and have no dedicated contract profiles. A profile selects the correct request/result schemas. It does not install tools, run a design algorithm, or supply scientifically qualified thresholds.

```text
config/
├── environment.yaml                # Task catalog and reference-bundle settings
├── requirements.txt                # Python validation dependencies
├── shared/                         # Common fields, protocol, assay and metric definitions
├── monoclonal_reference/            # Retained paired-reference contracts and DENV variants
├── monoclonal_target_only/          # Retained target-only contract
├── bispecific_design/               # Named chains, two specificities, combined evidence
└── bispecific_assessment/           # Cellular and CNS dataset/decision contracts
```

Only Markdown task instructions live in `../tasks/`. JSON request examples live beside their profiles and schemas in the family folders above. Validation code and tests remain in `../tests/`. Reports belong in `../results/`.

## Contract Profile Mapping

Paths below are relative to `config/`. Active profiles name their task file, request schema, result schema and validation level. The four older monoclonal profiles have `prompt_status: retired` and a `fixture_file` for regression checks; they do not register active task prompts.

| Task ID used with `--task` | Profile | Validation available |
| --- | --- | --- |
| `mab_reference_guided_design` | [monoclonal_reference/profile.yaml](monoclonal_reference/profile.yaml) | Retained contract; retired prompt fixture; reference preflight and bundle validation. |
| `denv_antibody_001` | [monoclonal_reference/denv.general.yaml](monoclonal_reference/denv.general.yaml) | Retained contract checks; retired prompt fixture. |
| `denv_antibody_001_tools` | [monoclonal_reference/denv.tool_specific.yaml](monoclonal_reference/denv.tool_specific.yaml) | Retained contract checks; retired prompt fixture. |
| `mab_target_only_design` | [monoclonal_target_only/profile.yaml](monoclonal_target_only/profile.yaml) | Retained contract; retired prompt fixture; schema and declared-identifier checks. |
| `bispecific_antibody_design` | [bispecific_design/profile.yaml](bispecific_design/profile.yaml) | Schema and declared-identifier checks. |
| `bispecific_cellular_mechanism_assessment` | [bispecific_assessment/cellular_mechanism.yaml](bispecific_assessment/cellular_mechanism.yaml) | Dataset declarations and response contract. |
| `bispecific_cns_delivery_assessment` | [bispecific_assessment/cns_delivery.yaml](bispecific_assessment/cns_delivery.yaml) | Dataset declarations and response contract. |
| `bispecific_cns_readout_comparison` | [bispecific_assessment/cns_readout.yaml](bispecific_assessment/cns_readout.yaml) | Dataset declarations and exact task answer fields. |
| `bispecific_cns_shuttle_integrated_gate` | [bispecific_assessment/cns_integrated.yaml](bispecific_assessment/cns_integrated.yaml) | Dataset declarations and exact task answer fields. |

Both DENV documents retain `task_id: denv_antibody_001` inside their requests; `variant` distinguishes `general` from `tool_specific`. The CLI profile selector includes `_tools` for the latter. Both historical prompts are test fixtures, not active agent tasks. The existing tool-specific validator still checks its registered method bindings in the supplied protocol; changing prompt wording does not qualify or install those methods.

The retained generic monoclonal profiles and request examples specify human EGFR (ERBB1): cetuximab for reference-guided design and no binding reference for target-only discovery. The bispecific profile specifies human HER2 (ERBB2), with zanidatamab as the reference for biparatopic domain II/domain IV design. These names identify the task context; verified sequences, structures, reference evidence, and evaluation protocols must still be supplied. Family schemas remain reusable across targets, and the generic contract checker does not enforce the target-specific task instructions or authenticate reference identity.

## What each family declares

- **Monoclonal with reference:** paired reference identity, target, permitted changes, objective, protocol, candidate lineage, and reference/candidate outputs. The six reference-required objectives share one schema pair; DENV retains its existing specialized pair.
- **Monoclonal target only:** `design_mode: de_novo`, `antibody.reference: null`, target context, framework policy, candidate origin, comparison policy, and evaluation requirements. Results contain candidate-origin records instead of a binding-reference baseline. `parent_id` remains null in this first contract; multi-generation lineage is not represented.
- **Bispecific design:** one or two targets, exactly two distinct target/epitope specificities, named molecular chains, arm assignments, valency, assembly policy, and mechanism. Chain count is not fixed at four. Declaring simultaneous engagement as required also requires its evidence domain. Results separate arm evidence from whole-molecule evidence.
- **Bispecific assessment:** supplied datasets, candidate identifiers, decision protocol, and a task-specific answer. The result envelope records status, request hash, answer, evidence, report, and limitations. For tasks using `<EVAL_ANSWER>`, the enclosed JSON corresponds to the envelope's `answer` field; the CLI validates the envelope JSON, not XML-like tags.

An assessment with missing inputs uses `NEEDS_INPUT`, `answer: null`, and a nonempty missing-input list. `ASSESSED` requires an answer, declared evidence, and a report. These are declarations: the checker does not recompute CNS measurements, select a scientifically correct answer, or establish mechanism validity.

## Shared definitions and scientific protocols

[definitions.schema.json](shared/definitions.schema.json) owns reusable artifact, target, provenance, budget, and paired-record fields. JSON Schema `$ref` links reuse these definitions; there is no YAML inheritance or implicit merging of profiles.

[protocol.schema.json](shared/protocol.schema.json), [metric-catalog.json](shared/metric-catalog.json), and [mab-assay-record.schema.json](shared/mab-assay-record.schema.json) retain the reference-monoclonal evaluation vocabulary. They are not universal scientific protocols for every architecture or assessment. New-family protocol fields currently declare hashed artifacts; their scientific contents need a separately reviewed evaluator.

No profile supplies affinity, interface, developability, or safety cutoffs. Actual methods, revisions, applicable thresholds, and ranking rules must come from a qualified protocol appropriate to the task. `scientific_execution_included: false` and `scientific_thresholds_supplied: false` make that boundary explicit.

## Validate a configuration

Run from `environments/antibody_design/`:

```bash
python3 -m pip install -r config/requirements.txt
python3 tests/validate_spec.py

python3 tests/task_contracts.py config/monoclonal_target_only/request.example.json --task mab_target_only_design
python3 tests/task_contracts.py config/bispecific_design/request.example.json --task bispecific_antibody_design
python3 tests/task_contracts.py config/bispecific_assessment/cns_readout.request.example.json --task bispecific_cns_readout_comparison

# Reference-only preflight also checks input completeness.
python3 tests/monoclonal_antibody_with_reference/validation.py preflight config/monoclonal_reference/request.example.json
```

For a real result, select its task and bind it to the exact request file:

```bash
python3 tests/task_contracts.py /path/to/result.json \
  --task bispecific_cns_readout_comparison --kind result \
  --request /path/to/request.json --input-root /path/to/result-artifacts
```

`CONTRACT_VALID` means the selected schema and declared identifiers agree. It is **not a readiness status**: the supplied examples deliberately contain null fields or placeholder artifact hashes. Without `--input-root`, artifact contents are not checked. With it, referenced files in the checked document must exist beneath that root and match their hashes. Validate a request separately against its own input root; checking a result does not recheck the request's artifact files.

Only the reference family has the existing `preflight` and `bundle` checks. The new families do not yet have equivalent end-to-end bundle validation or scientific grading.

## Paths and maintenance

[environment.yaml](environment.yaml) registers all nine profiles. Its inherited `stages`, `qualification`, `output`, and reference scope settings apply to the reference-bundle validator, not automatically to other families. All configuration paths are relative to the environment directory.

Canonical schemas now live in family folders; the former flat schema paths were removed. Use the catalog or the validation CLI rather than hardcoded old paths. Schema IDs are stable identifiers resolved by `tests/schema_registry.py` from local files; they are not download URLs. Unknown references fail without network retrieval.

When adding a task, put its Markdown in `tasks/<family>/` and its matching reference document in `benchmark/<family>/`. Register document-only prompts separately from contract profiles. When a compatible contract is implemented, add its profile and request example under `config/<family>/`, register it in `environment.yaml` and add relevant checks under `tests/`. Run the package validator to verify schema references, task mappings, examples, documentation links, and existing monoclonal regressions.

Paper-based evaluation prompts are listed under `paper_benchmark_tasks` and stored in `tasks/monoclonal_antibody_design/`. Their published values and sources live in matching files under `benchmark/monoclonal_antibody_design/`, indexed by `paper_benchmark_references`. Each task and benchmark share the same family folder and filename and link to one another. These documents do not register executable profiles, request schemas or automatic graders.

The `bispecific_benchmark_references` mapping links the five existing bispecific task IDs to their benchmark documents. These are reference and evaluation specifications; the mapping does not provide a TxBench grader or certify trajectory outputs.
