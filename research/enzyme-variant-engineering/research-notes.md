# Research notes — minimal enzyme variant environment

## Scope and architectural decision

The environment is a reusable scientific process with case studies, task-specific
evaluation and one native failure-focused specialist. Native SCI already supplies
research, tool contracts, enzyme preflight, execution, authorization, sessions and
saved child agents. None is reimplemented here. See the
[decision record](../../docs/decisions/native-enzyme-case-studies.md).

The old runner, duplicated workflow executor and synthetic-only task interface
were removed from this contribution. They remain in Git history and were preserved
locally before replacement. Their tests do not become evidence for this new case.

## Why BglB is the first case

The selected study reports separate activity and functional-stability endpoints,
with a small accessible supporting table. It supports a concrete failure-analysis
question: does a favorable stability result come at the expense of catalysis?
The assignment proposes single variants, rather than prescribing a particular
predictor or automatically replaying a fixed molecular pipeline.

## Source checks completed

- Downloaded the 2017 S1 CSV and checked the actual data/units/reference row.
  SHA-256: `3d94ee8b73d4b67cc7c1f6def54b00a40bdacc6f1eaf1b53bcd01294fe58b619`.
- Counted 128 mutant rows and one reference row, despite the article's description
  of 129 mutants. Preserve the discrepancy, not a fabricated extra record.
- The 2016 source archive's `bagel.pdb` has a 445-residue chain A core. Its sequence
  is exactly P22505 residues 4–448 in the RCSB UniProt record. Every source-table
  mutation's starting amino acid matches that study-numbered core.
- Normalized parent sequence SHA-256:
  `5595c3d42a0dfb9f365c84b05c993991e4cc7930f2d16160e09187e1329d6619`.
- Checked the 2O9P mmCIF tag and engineered substitutions. It is not an automatic
  exact-parent replacement. The model core is not a complete tagged assay construct.
- Reviewed the 2017 supplemental methods: these identify P22505 and a tagged
  expression construct. Assay equivalence for a new construct remains a separate
  scientific check, not something a matching mutation label proves by itself.
- Source RCSB UniProt JSON SHA-256:
  `db02025fc20f92bfe6fd0bf8bf166577effa294a5224dd49f70705afdc786687`.
- Source 2O9P mmCIF SHA-256:
  `99303ec0637acd9247aaf2edc7630bd4ad67de1da4fecf97dea22435241dac18`.

The structure archive is linked rather than copied as a scientific executor or a
bundled ligand-chemistry definition. Reacting-state chemistry still needs suitable
preparation before any structural activity interpretation.

## Interpretation limits

The functional Tm endpoint is activity after heat challenge, not a thermodynamic
unfolding measurement. Published kinetic units must be normalized explicitly.
The project uses a descriptive joint point rule and does not claim significance.
Source error estimates and near-equal values need scientific interpretation.

The case is public and permits literature research. It is not a blinded holdout;
model training overlap is unknown. A published mutation can be rediscovered, but
not advertised as a novel, experimentally improved enzyme. Novel variants remain
unmeasured until appropriate experiments are provided. No base/specialist design
run, trained molecular model or new experimental improvement is reported yet.

## Next work

Run the ordinary base task, inspect its real failure points, and use native
specialist advice for a declared matched run or recovery continuation. Record both
negative and positive results, with resource costs and missing evidence. Add
further case studies without adding another runtime or copying these catalytic
residue numbers to unrelated enzymes.
