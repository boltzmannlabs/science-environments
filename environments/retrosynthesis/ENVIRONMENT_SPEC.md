# Retrosynthesis — environment specification

**Status:** Implemented. Base software and local repository migration checks passed; post-publication checks and full scientific validation remain separate gates. See [validation status](results/README.md).

**Tracking:** [issue #14](https://github.com/boltzmannlabs/science-environments/issues/14). Owner: Synthetic Chemistry pod (Gopi Krishna). Maintainer and chemistry-SME reviewers remain unassigned. This broader base implementation references the issue without claiming its acceptance criteria or closure; no reviewer approval is implied here.

## Objective and execution model

Enable Agent Scientist to propose, import, compare and improve synthesis routes from available starting materials to a target molecule. Normal Agent Scientist keeps its existing tools, skills and workflow autonomy. This environment is an optional common workspace. A separate controlled runner supports matched scientific comparisons.

The default local route search is breadth-first search using LocalRetro proposals. Best-first and SynthChem A*, MCTS and portfolio policies are also implemented. External reaction models require explicitly configured assets; missing models fail visibly. Creating a session does not automatically run a search. Normal local searches produce drafts for inspection and explicit submission.

## Inputs and validation

The executable [Task schema](src/synthesis_route_gym/schemas.py) is authoritative:

- `schema_version: "1.0"`, unique task identifier and target SMILES.
- Inventory with canonical molecular identities, optional amounts in mmol, optional prices per mmol with currency, source and quote date. Duplicate identities are rejected. Unknown quantities/prices remain null.
- Constraints: maximum steps, forbidden molecules/SMARTS/operations, equipment availability and whether complete conditions are required.
- Explicit resource regime: finite action/expansion/wall-time/token limits for budgeted tasks; all aggregate limits null for unbudgeted tasks. `top_k` remains finite in either regime.
- Evidence records distinguishing predictions, proxies, exact/analogue literature, measurements and unresolved claims. Provenance does not establish that a claim has been independently verified.

Malformed structures, unsupported fields and nonfinite scientific numbers fail input validation. Route validation checks graph connectivity, cycles, target identity, inventory, quantities and declared constraints. Constraint checks do not constitute laboratory safety approval.

## Actions and output contract

Normal `srg_action` sessions support reset, local route generation, supported-format route import, route proposal, validation, ranking, revision and explicit submission; close releases the session. See the [integration action contract](integrations/agent_scientist/README.md) for exact action names and arguments.

Canonical route candidates contain stable IDs, target, reaction-step graph, reactants/reagents, optional amounts/conditions/yield predictions, tool identity and evidence references. Import supports `srg-route-candidates-v1` and `rebolt-scored-paths-v1`. Legacy stock/reference flags cannot grant experimental authority.

Assessments report graph validity, inventory completeness, quantity status, constraint compliance, known/unknown cost components, unresolved steps and evidence status. Structural assessment deliberately retains `solved: false` and pending review. Submission records selected route IDs and resource use; it does not establish a successful synthesis.

## Scientific applications and specialists

Executable interfaces cover inventory-constrained planning, reaction-condition optimisation, impurity analysis, process-route comparison and biocatalytic source matching. Their separate evidence limits are documented in [application workflows](docs/APPLICATION_WORKFLOWS.md). Bundled replays are software fixtures or declared source records, not new experimental measurements.

Retrosynthesis Strategist, Condition Optimisation Scientist and Route Critic are experimental advisor roles. Main-only is the default. All LLM roles use the Agent Scientist main/default profile; scientific predictors are separate tools. Existing ReactionT5v2-yield support is replaceable and predicts supplied recipes, not route success. New custom-model development is deferred at the owner's request.

## Evaluation and reproducibility

The planned scientific comparison is fixed non-agent workflow versus main Agent Scientist versus specialist-enabled Agent Scientist, using identical tasks, permitted tools and matched compute budgets. A separate unbudgeted comparison records actual resource consumption. Held-out reference answers stay outside solver input. Report solved targets only with an explicit evidence/review definition; additionally report top-k feasibility, stock/quantity compliance, ranking quality, comparable costs and search efficiency. Report negative results and uncertainty.

Base software checks do not satisfy the held-out improvement gate. Full benchmarking, independent source-based chemistry assessment and specialist promotion remain deferred. AI-assisted chemistry review is not independent experimental confirmation.

Install with the [README](README.md); record versions, checkpoint hashes, configuration, seed and resource regime for actual model runs. Python 3.10+ is declared; the base clean suite used Python 3.11. Linux is the verified live subprocess platform. Model assets, credentials, private evaluation answers and historical raw datasets are excluded.

## Limitations and research records

Normal sessions are memory-only. Ordinary external-tool/LLM activity is not fully measured by the environment ledger. Startup model attestation is not continuous file integrity enforcement. Linux cleanup covers the current direct worker. Full remote-platform submit/download/import execution is not claimed tested.

- [Research notes](../../research/retrosynthesis/research-notes.md)
- [Scientific and software references](../../research/retrosynthesis/references.md)
- [Historical preparation snapshot](STATUS.md), preserved at its original reporting cutoff
- [Base verification report](docs/BASE_RELEASE_VERIFICATION.md)
