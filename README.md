# BolChem

Small-molecule task specifications for Agent Scientist.

**Status: Specification.** Owner: Ankith116. Related issue: #46.

| Module | Task |
| --- | --- |
| [Small-molecule de novo design](environments/bolchem/small-molecule-de-novo-design/README.md) | Design candidates for p38α and assess them using the supplied 1A9U structure. |
| [Small-molecule optimization](environments/bolchem/small-molecule-optimization/README.md) | Improve supplied DRD2 starting molecules under frozen property/similarity conditions. |

Common [specification](environments/bolchem/ENVIRONMENT_SPEC.md),
[status](environments/bolchem/STATUS.md),
[tool inventory](environments/bolchem/MODELS_AND_TOOLS.md) and
[validation notes](environments/bolchem/results/specification-validation.md)
are maintained alongside the task modules. Owner/evaluator source material is in
[research/bolchem](research/bolchem/research-notes.md).

Give the execution agent only the selected task and its prepared input/scorer
bundle and limits. The task files contain no literature references or prescribed
reference algorithms. Scientific execution and runtime validation remain pending.

## Branch workflow

This working branch intentionally displays only the BolChem contribution and the
repository license. Its history is preserved with ordinary commits. The removal
of inherited files is confined to this working branch, not main.

For review, create a fresh contribution branch from main and transfer only
`environments/bolchem/` and `research/bolchem/`, with appropriate navigation updates.
Do not open a direct merge request from this working snapshot into main, since
that would also propose deleting inherited files. No PR or merge is performed here.
