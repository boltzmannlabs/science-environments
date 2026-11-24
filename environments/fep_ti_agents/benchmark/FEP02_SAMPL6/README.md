# FEP02 SAMPL6 benchmark

This wrapper turns the pinned SAMPL6 manifest into the second paper-driven FEP
benchmark. Its canonical detailed task is
`tasks/fep_paper_003/`, which contains frozen PDB inputs, checksums, four
controlled configurations, an independent validator and regression tests. It
is currently `REFERENCE_READY`; engine execution and scientific qualification
remain pending.

Use `scripts/validate_sampl6_manifest.py` for the independent manifest check.
