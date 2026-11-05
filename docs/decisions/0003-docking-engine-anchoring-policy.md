# Decision 0003: Docking-score engine anchoring policy

**Date:** 2026-11-04

## Context

Source papers used different scoring engines: AutoDock Vina 1.1.2, Glide SP/XP, AutoDock 4.2.6, LibDock/CDOCKER. kcal/mol scores from different engines are not interchangeable — a −9.89 Glide SP cut-off does not mean −9.89 in Vina. Graded runs dock exclusively through Boltzmann platform tools (`Vina_basic_docking`, `Diffdock` as second engine), never local installations of the papers' engines.

## Options considered

1. Require literal reproduction of every paper's kcal/mol cut-off in the platform engine.
2. Skip quantitative score bars entirely; grade workflow completion only.
3. Three-mode anchoring matched to each paper's engine, with the mode stated explicitly in every task document.

## Decision

Option 3:

- **Same-engine bar** — the paper used AutoDock Vina: the paper's kcal/mol cut-off applies directly (FGFR2 ≤ −11.7; GSK-3β < −6.80).
- **Engine-relative bar** — the paper used Glide/AutoDock 4/LibDock-CDOCKER: the paper number is kept as the anchor with an explicit caveat that the platform engine's scale differs and the agent must clear the bar relative to its own engine's reference scores (CAII, ROCK2, KHK-C, MMP-9, PI3Kα, EGFR, TrkB).
- **Self-calibrating bar** — the agent must out-dock a named reference ligand (co-crystal ligand or known inhibitor) redocked in the same engine, removing cross-engine comparison altogether (FoxM1/Hsp70 vs FDI-6 and VER-155008; PI5P4Kγ vs DVF redock; EGFR vs R85).

## Reasoning

Mode 1 would manufacture false failures on engine scale shifts; mode 2 throws away the quantitative rigor that makes the benchmark meaningful. Mode 3 keeps every paper's number visible as the anchor while making the comparison well-posed for the platform engine. The self-calibrating mode is preferred wherever the paper itself is organized around a reference ligand.

## Consequences

- Every task's Pass bar names its anchor mode; `ENVIRONMENT_SPEC.md` carries the per-task anchoring table.
- MM-GBSA/MM-PBSA bars are treated as engine-relative corroboration, never as the sole pass condition.
- kcal/mol vs kJ/mol unit conflicts in papers (VEGFR-2/c-Met reports kJ/mol) are annotated verbatim.

## References

- `environments/*/ENVIRONMENT_SPEC.md` (anchoring table)
- `research/small-molecule-virtual-screening/research-notes.md` §2 (engine-anchoring policy)
