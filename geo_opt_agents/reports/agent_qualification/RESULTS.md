# Geo-Opt agent qualification matrix

Each of the 18 specialists was run with an explicit input fixture. Results
distinguish deterministic fixture checks from live GPU engine evidence.

| Agent | Input case | Execution | Status |
|---:|---|---|---|
| 01 | malformed structure | deterministic fixture | pass |
| 02 | connectivity/valence | deterministic fixture | pass |
| 03 | distorted starting geometry | deterministic fixture | pass |
| 04 | charge/multiplicity | deterministic fixture | pass |
| 05 | method selection | deterministic fixture | pass |
| 06 | optimizer selection | deterministic fixture | pass |
| 07 | coordinate strategy | deterministic fixture | pass |
| 08 | constraint validation | deterministic fixture | pass |
| 09 | SCF failure recovery | deterministic fixture | pass |
| 10 | live water convergence | GPU4PySCF engine | pass |
| 11 | stagnation trace | deterministic fixture | pass |
| 12 | live gradient validation | GPU4PySCF engine | pass |
| 13 | minimum verification | contract fixture | review |
| 14 | multi-conformer handling | deterministic fixture | pass |
| 15 | protein-ligand geometry | contract fixture | review |
| 16 | resource recovery | deterministic fixture | pass |
| 17 | live final-geometry quality | GPU4PySCF engine | pass |
| 18 | orchestration/audit | deterministic fixture | pass |

Summary: `16 pass`, `2 review`, `0 fail`. Agents 10, 12, and 17 include
measured GPU energy/gradient evidence from the Tier-1 water optimization. The
other pass statuses are deterministic contract/input checks, not claims of a
completed production engine calculation. Agent 13 remains review because no
Hessian/frequency backend is installed; Agent 15 remains review because no
frozen protein-ligand topology/reference artifact is supplied.
