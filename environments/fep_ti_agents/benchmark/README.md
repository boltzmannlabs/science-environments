# FEP benchmark catalogue

The benchmark catalogue measures literature-to-environment reconstruction,
not only whether a numerical free-energy value is produced.

## FEP-PAPER-001

- Paper-derived system: CDK2 transformation `17 -> 1h1q`.
- Reference source: pinned Alchaware CDK2 inputs and protocol metadata.
- Inputs: protein, endpoint ligand structures, mapping, parameter files and
  complex/solvent endpoint artifacts.
- Evaluations: parameter extraction, mapping, endpoint readiness, provenance,
  configuration matrix and independent qualification gate.
- Current result: setup reconstruction `PASS` for evaluated fields;
  scientific FEP qualification `REVIEW`.

The detailed task is in `../tasks/fep_paper_001/`. Its results are summarized in
`../results/FEP_PAPER_BENCHMARK_REPORT.md` and the machine-readable audit files.

Future benchmark systems must pin a paper DOI, revision, molecular edge,
structures, parameters, protocol, reference metrics and acceptance criteria.
