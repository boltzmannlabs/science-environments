# MD paper benchmark catalogue

This catalogue evaluates whether agents can reconstruct a published molecular
dynamics protocol, identify missing details, and distinguish setup validation
from scientific reproduction. Each paper packet contains a pinned source,
local input identity, protocol extraction fields, and an independent evaluation
gate. Short local runs never count as reproduction of a long-timescale paper.

| ID | Paper system | Primary question | Status |
|---|---|---|---|
| MD-PAPER-001 | Villin headpiece (1VII) | Folding protocol and native-state observables | CATALOGUED |
| MD-PAPER-002 | Barnase–barstar (1BRS) | Protein-interface stability and contacts | CATALOGUED |
| MD-PAPER-003 | DNA duplex (12-mer) | Base-pairing and helical observables | CATALOGUED |

The detailed packets are in the corresponding directories. Before execution,
the evaluator must pin the exact paper revision, input hashes, engine version,
force field, solvent, sampling design, observable definition, and reference
values.
