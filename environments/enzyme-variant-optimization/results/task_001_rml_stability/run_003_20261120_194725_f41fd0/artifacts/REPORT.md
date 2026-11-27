# RML stability workflow report

The requested fresh assisted workflow is unfinished. No stability or solubility prediction, candidate generation, sequence revision, candidate complex, final selection or independent final evaluation has been completed. No candidate improvement can be claimed.

The frozen user parent has 269 residues and its complete sequence exactly matches the 3TGL deposited entity sequence. The 3TGL coordinate file is missing mature residues 1–4. The comparison against UniProt P19515 mature sequence found two residue differences; their origin was not established. See evidence/parent_preparation.md for sources, disulfide and active-site checks, and the unresolved calcium annotation.

The required initial proposer and critic did not run. The saved enzyme-method specialist reported it cannot delegate, and catalog searches returned no saved proposer or critic. The saved enzyme-recovery specialist recommended holding submissions rather than replacing their required review. A preliminary enzyme-evaluator invocation could not read its supplied file paths because its tools denied access; it did not perform a final evaluation. The endpoint, complete edit mask, substrate-water state and final protocol remain to be frozen.

One local input-validation attempt was rejected because a FASTA file was passed to the Enzymes CSV input; the tool confirmed that no upload or submission occurred. A corrected, identity-verified CSV is prepared but not submitted. No remote scientific jobs were submitted and no variants generated. Model-token and cost totals remain unknown; see usage.json for available specialist usage.

Artifacts: RUN_PLAN.json is explicitly provisional, not a frozen design protocol; decisions.md and jobs.json record the role and validation failures; parent and substrate source artifacts are in evidence/. No selection.csv or selection_seal.json is created: absence means no selection occurred, not that a complete search produced no qualifying variants.
