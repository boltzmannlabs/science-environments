# Five Monoclonal Task Packages: Scope and Validation

Base: upstream `main`, `ba3232c0480ba3e6fd516712d36ed2d93adf9414`.

Contribution scope: source and results for existing tasks 001–005, shared helper/provenance records, source/results documentation, environment specification, README, status and bounded ignore rules. Task and benchmark directories, other environments, and upstream task 006/007 records are unchanged.

The packages preserve historical findings and failures. Six scientific result runs map to seven source records; one source record is an unsubmitted PD-1 plan. No metric or model was recomputed. Published benchmark definitions are upstream's versions, even where the old local checkout had additional edits.

The HER2 historical improvement claim is qualified by its retained independent audit. LCAT's custom local-distance metric is explicitly distinguished from structural lDDT and pLDDT, and its single-case scores do not establish aggregate superiority. Gal-3BP remains partial, including the recorded SASA failure. Exact scientific coverage is linked from [status](../../status.md).

Original imported bytes are verifiable through [the import manifest](import_manifest.csv). Inputs/logs relocated to source are listed in [the relocation table](artifact_relocations.csv). Large downloads, caches and unrelated upstream examples are inventoried without deleting the originals. The finalized package inventory and validation reports document the current arrangement.

Validation: `python environments/antibody_design/src/shared/validate_packages.py` from the repository root. See [packaging report](validation/packaging_validation.md). Scientific jobs and portable reruns are outside this preparation.

Tracking issue: [#161 — Add source code and results for antibody design tasks](https://github.com/boltzmannlabs/science-environments/issues/161). The contribution requires pull-request review before merge.
