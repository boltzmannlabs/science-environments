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

## FEP-PAPER-002

- Paper-derived system: PTP1B structure `2QBS`, edge `23477 -> 23482`.
- Reference source: Ross et al. 2023 public binding free-energy benchmark,
  pinned revision `a65d86b782a678c75388566ce00446e45283ee63`.
- Published edge reference: `-1.16 kcal/mol`.
- Current result: source identity and edge validation PASS; production FEP
  qualification REVIEW because edge-specific trajectories and complete open
  protocol evidence are unavailable.

The detailed task is in `../tasks/fep_paper_002/`.
