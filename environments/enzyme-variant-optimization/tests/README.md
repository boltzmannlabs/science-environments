# Environment Tests

From the repository root:

```bash
python -B -m unittest discover -s environments/enzyme-variant-optimization/tests -v
```

The tests exercise the real offline comparison helper and command with synthetic data. They check metric direction, parent identity, matching units/protocols, duplicate sequences, missing measurements, eligibility, finite values, sealed selections and local documentation/configuration links. Task checks also require the antibody-style sections, a full eight-stage capability table, explicit output artifacts and execution limits matching the shared configuration in every case file. These are document-completeness checks, not proof that a scientific workflow has run. They do not call scientific services or claim biological validation.

For each real case, a separate evaluator must review these scientific acceptance requirements:

| Requirement | Evidence to inspect |
| --- | --- |
| Tool-generated initial and revised variants | Actual native generation outputs, settings, candidate sequences and source-to-candidate trace. A planned call or hand-written edits are insufficient. |
| Correct design constraints | Parent construct, allowed edits, protected catalytic/assembly features and mutation count. Use the existing tools for molecular validation. |
| Real parent and candidate observations | Native artifacts with identity, units, method/state settings and explicit failures. |
| Candidate-specific structures and chemistry | Actual sequences in structures, ligand state/atom mapping, relevant components and quality/catalytic reports. |
| Results-driven revision | Observed weakness, executed revised design, affected re-evaluations and comparable parent results. |
| Fair comparison | Frozen inputs/evaluation/budgets, separate runs, actual delegation receipts in assisted runs and no delegation in base runs. |
| Honest conclusion | Complete with no improvement differs from missing evidence. Computational endpoints differ from experiments. |

Passing the software tests does not establish any of the scientific requirements above.
