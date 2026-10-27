# Use the skill with Agent Scientist

After deliberate installation into the active profile, restart SCI and preload the skill if the build supports it: `sci --skills sirna-harness`. Check the local CLI help; no external product website is the operating manual for a customized SCI installation.

## Design request template

Use sirna-harness in DESIGN mode. Organism: [explicit organism]. Primary transcript: [exact accession.version] or approved FASTA: [path]. Experiment: [name]. Coverage references/objective: [declared choices]. Requested research-review count: [count, default20]. Provider: [inspect matching authorized tools first, or explicit local choice]. Cell/assay/chemistry/delivery: [specified or unresolved]. Preserve source artifacts, use compatible existing tools, screen both strands, report executed/missing evidence and do not force biological qualification. Do not upload sequences or install models without required authorization.

Missing transcript/variant choices must be resolved before affected design steps. Merely copying this request does not configure a generator, reference index or scientific model.

## Audit request template

Use sirna-harness in AUDIT mode on [verified run directory]. First discover actual artifacts and verify input hashes/receipt. Write a new timestamped sibling audit. Do not regenerate, infer, fold or screen again. Resolve candidate evidence, reproduce saved diagnostic windows where available, preserve exact/near/seed and guide/passenger distinctions, and report failed versus missing gates separately. Verify original files are unchanged.

## Sensitivity request template

Use SENSITIVITY mode with preserved scores from [run]. Declare matched cohorts, K and tie behavior before calculating. Reuse verified baselines. Compare extrapolation and actual missing-output restrictions without imputation, new weights or silent renormalization. Label K>n not applicable and K=n non-discriminating. Do not designate a winner or interpret a changed rank as new biological evidence.

## Experimental benchmark request template

Use BENCHMARK mode to audit documented experimental datasets, original-study/target/assay/chemistry metadata and final-checkpoint exposure before prediction. Preserve source labels and units; do not pool doses/native-reporter endpoints. Only create a new grouped, duplicate-aware untouched test when independence and compatibility are auditable. Otherwise report BLOCKED_NO_AUDITABLE_INDEPENDENT_DATASET with null metrics, zero attempts and an explicit empty independent-prediction schema. Do not recycle historical random/cross-study performance as independent evidence.

## Helper commands

Run from the unpacked/installed skill directory using an explicitly chosen Python3.10+:

python3 scripts/sirna_portable.py preflight --config /absolute/project/environment.json
python3 scripts/sirna_portable.py validate-objective --objective /absolute/project/objective.json
python3 scripts/sirna_portable.py validate-candidates --candidates /absolute/run/candidates.csv --fasta /absolute/run/reference.fasta --reference-alphabet DNA
python3 scripts/sirna_portable.py check-gates --gates /absolute/run/gates.json
python3 scripts/sirna_portable.py audit-label-table --dataset /absolute/data/records.csv --sequence-column guide --label-column measured_inhibition --label-unit source_reported_percent_inhibition
python3 scripts/test_portable.py --scratch /absolute/approved/scratch

The column names in the last example are placeholders to replace after inspecting the actual file. Candidate CSV requires candidate_id, guide_sequence, passenger_sequence, target_start, target_end; optional transcript_id must match the reference token. Guides/passengers must already be documented uppercase19nt RNA. DNA reference conversion is explicit and comparison-only; originals remain untouched.

Templates are intentionally incomplete and should block until scientific parameters/paths are filled. The label-table helper cannot certify independence, and the gate helper cannot certify biology even if supplied gate claims are all PASSED. Deliberate blocked checks exit2; inspect JSON before interpreting exit status.
