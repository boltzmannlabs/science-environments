# Local SynthChem model-backed smoke check

Status: completed locally on 2026-10-29. This is an engineering check, not a
held-out benchmark or experimental validation.

Input: `examples/aspirin_task.json` (aspirin target; declared salicylic acid,
acetic anhydride, acetic acid and other inventory items). Search policy:
`synthchem_portfolio`. Proposal backend: the existing LocalRetro checkpoint
in the managed Agent Scientist profile, executed with its compatible `mol_gpu`
Python runtime. Neither checkpoint nor runtime is bundled in this repository.

The direct adapter check returned four aspirin precursor predictions. The full
portfolio search ran 12 backend expansions in 106.59 episode seconds and
submitted two routes. Both passed graph, inventory and task-constraint checks.
The full machine-readable run is in `synthchem_model_aspirin.json`.

| Route | Predicted starting materials | Structural gate | Chemical review |
|---|---|---|---|
| `route-0d436e400b178c3b` | Salicylic acid + acetic anhydride | Pass | Plausible acetylation proposal; conditions, yield and exact-source evidence were not supplied or checked in this run. |
| `route-f5045905b51d1ca7` | Salicylic acid + acetic acid | Pass | Feasibility unresolved: an activating method or suitable conditions would need review. Do not present this as a validated preparation. |

No route step has an evidence ID. Both assessments retain `solved=false`.
One LocalRetro expansion failed for phosphorus pentachloride and the failure was
recorded; the search continued. These findings demonstrate real model-backed
route retrieval and honest failure accounting. They do not demonstrate
reaction feasibility, literature support or superiority over another method.

Reproduce with the compatible LocalRetro source and runtime, substituting their
local paths:

```sh
python -m synthesis_route_gym plan \
  --task examples/aspirin_task.json \
  --search-policy synthchem_portfolio \
  --expansion-backend localretro \
  --repo-root /path/to/managed/localretro \
  --chemistry-python /path/to/mol_gpu/bin/python \
  --output /tmp/synthchem-model-aspirin.json
```
