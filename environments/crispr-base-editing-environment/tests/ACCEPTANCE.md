# Acceptance Checks

Run these checks when implementing or integrating the environment. They define expected behavior; they do not claim that tool execution has already been tested.

- Reject missing project, experiment name, gene ID, editing mode, base editor or cell type before calling a prediction tool.
- Confirm the selected organism, reference assembly, transcript and Bowtie index are recorded and compatible.
- Verify returned guides are 20 nt, use supported PAMs and have target bases in the configured editor window.
- For variant-correction tasks, verify reference/alternate alleles and map the requested base to each candidate's strand and genomic coordinate.
- Validate every prediction FASTA record has exactly 50 nt in the 19 + 20 + 3 + 8 layout, contains only A/C/G/T and has a unique identifier.
- Preserve the mapping from each FASTA identifier to guide, allele, editor, transcript and genomic coordinates.
- Keep efficacy, bystander and off-target results separate; do not interpret editing-event fraction as intended-correction fraction.
- Check Bowtie results against the matching genome index, record mismatch positions/counts through the configured limit and exclude the intended site by coordinate.
- Preserve unique spacer counts separately from guide–editor combination counts.
- Return `NO_COMPATIBLE_GUIDES` only after a complete supported search returns zero eligible designs. Return `UNSUPPORTED_TARGET` for unsupported tool/model scope and `BLOCKED` for unavailable required files or services.
- Rank candidates using the declared ordering and retain each component metric and missing-data reason in `metrics.json`.
