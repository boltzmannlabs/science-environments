# Task 05 — run log

[Task](../../tasks/task-05-microwave-catalytic-amidation/README.md) · [Results](README.md)

All entries are derived from the originating session's recorded tool trace. No job or experiment was run while packaging these folders.

| Order | Stage | Tool / method | Input | Result | Status |
|---:|---|---|---|---|---|
| 1 | Input audit | Local file review | `SC02_agent_workflow (1).md` | Illustrative hindered pair `DEMO_01`; no exact benchmark matrix | completed |
| 2 | Condition recommendation | `boltzmann_submit`, job `condition_recommendation` | reactants + product SMILES | Accepted, doc_id `6b05bcdf8b9d410520f9a7b3` | accepted |
| 3 | Poll | `boltzmann_status`, same job/doc | — | `completed`; ten conditions returned inline; no artifact URLs | completed |
| 4 | Constraint audit | Local review | ten conditions | All `catalyst_name: []`; no heating mode/time | completed — FAIL vs task |
| 5 | Literature search | PubMed E-utilities (terminal) | targeted amidation queries | 8 records fetched; abstracts screened | completed |
| 6 | Literature verification | Crossref + PubMed + PMC | L1, L3 metadata; L2 full text | Five contextual sources verified | completed; Europe PMC timeout, Crossref intermittent |
| 7 | Grounding | `grounded-citations` ledger | retrieved abstracts/full text | Citations and verbatim evidence verified | completed — `citations OK` |
| 8 | Design campaign | `reaction-optimize` (BayBE v1) | 192-candidate catalytic condition space | Six diverse initial designs | completed — design only |
| 9 | Persistent campaign | `campaign_cli create/next/summary` | same campaign JSON | Campaign created; four experiments reserved; zero measurements | completed |
| 10 | Prior seeding | Local mapping + `reaction-optimize --observations` | ten prior predicted yields, `excluded` + QC flags | Eight untested conditions selected; 20 QC messages; no fit | completed |
| 11 | Diagnostic (not adopted) | Same run with priors marked `reviewed` | identical numeric priors | Would fit GP to predictions as measurements; rejected | rejected |
| 12 | Packaging | Local file writes | sanitized artifacts | This folder set created; no new model/lab execution | completed |

## Provenance and safety notes

- One internal job was submitted once and polled to terminal state; no duplicate submission after connection or encoding issues.
- Model scores are not experimental yields; heuristic design scores are not calibrated probabilities.
- Earlier predicted yields were never converted to measurements; the `reviewed` variant exists only as a rejected diagnostic.
- Raw service exports, credentials, signed URLs and personal paths are excluded from all artifacts.
