# References and inspected sources

**Inspected on 28 October 2026.** Sources inform a specification-stage draft; they do not establish reproduced results or a working local scientific environment. No third-party source code, task archive, model weights, or experimental dataset was copied into this contribution.

## SMDD-Bench

- **S1.** Han et al., *SMDD-Bench: Can LLMs Solve Real-World Small Molecule Drug Design Tasks?* [arXiv:2605.21740v2](https://arxiv.org/abs/2605.21740v2), revised 24 May 2026. The abstract and repository documentation were inspected; a full-paper scientific audit was not performed.
- **S2.** [Official repository README](https://github.com/t7rs/SMDD-Bench) — task types, separate task archive, agent/evaluator layout, computational affinity semantics, and runtime requirements.
- **S3.** [Lead-optimization metrics](https://github.com/t7rs/SMDD-Bench/blob/main/metrics/lead_optimization.py) and [evaluator entry point](https://github.com/t7rs/SMDD-Bench/blob/main/evaluator/eval_entrypoint.py) — inspected source for objectives, baseline comparisons, held-property tolerances, chemistry constraints, and evaluation statuses. These files are design references; their defaults and runtime are not adopted.

The repository files were read through web access on the inspection date. An exact code commit was not independently resolved: Git remote lookup failed to resolve the host and the web API endpoint was inaccessible. The `main` links are therefore moving references, not reproducibility pins. Pin and review an exact revision before reusing code or executing the benchmark. The separately hosted task archive was not downloaded or checked.

## Practical Molecular Optimization (PMO)

- **P1.** Gao, Fu, Sun, and Coley, *Sample Efficiency Matters: A Benchmark for Practical Molecular Optimization.* [arXiv:2206.12411v2](https://arxiv.org/abs/2206.12411v2), revised 9 October 2022. The inspected abstract motivates explicit oracle accounting and limited-budget comparisons; it is not evidence that our proposed environment has been evaluated.
- **P2.** [Official `mol_opt` repository](https://github.com/wenhao-gao/mol_opt) — inspected README for computational benchmark organization, independent-seed production runs, and tuning separation. Repository code and dependencies were not installed or exercised. Its changing method inventory is not treated as a frozen paper result.

The repository README was read through web access; no exact code commit was verified for the same remote-lookup limitation noted above. These are methodological references, not a requirement to install PMO or inherit its numerical budget.

## Agent-Scientist and local repository sources

- **I1.** [Agent-Scientist](https://github.com/boltzmannlabs/agent-scientist) — local source inspected at checkout HEAD `062351dd048c142840f78ea198f22417d983ccda`. The checkout had unrelated local edits, so this records the inspected source context and does not certify a clean release or runtime compatibility.
- **I2.** [Boltzmann integration contracts](https://github.com/boltzmannlabs/agent-scientist/blob/062351dd048c142840f78ea198f22417d983ccda/plugins/boltzmann/CONTRACTS.md) and [connector README](https://github.com/boltzmannlabs/agent-scientist/blob/062351dd048c142840f78ea198f22417d983ccda/plugins/boltzmann/README.md) — local files inspected for canonical contract ownership and existing execution/authorization boundaries.
- **I3.** [Canonical tool catalogue](https://github.com/boltzmannlabs/agent-scientist/blob/062351dd048c142840f78ea198f22417d983ccda/plugins/boltzmann/skills/boltzmann-tools/references/tool-contracts.v1.json), [Molecule Optimization module](https://github.com/boltzmannlabs/agent-scientist/blob/062351dd048c142840f78ea198f22417d983ccda/plugins/boltzmann/skills/boltzmann-tools/references/modules/small-molecule-optimization.md), and [other generated modules](https://github.com/boltzmannlabs/agent-scientist/tree/062351dd048c142840f78ea198f22417d983ccda/plugins/boltzmann/skills/boltzmann-tools/references/modules) — source of tool definitions; no duplicated tool schema or live availability assertion is supplied here.
- **I4.** [Science Environments contribution guide](../../CONTRIBUTING.md), [enzyme environment specification](../../environments/enzyme-variant-optimization/ENVIRONMENT_SPEC.md), and [matching research notes](../enzyme-variant-optimization/research-notes.md) — local organizational references. Similar state/evidence concepts do not establish that an enzyme implementation can be reused unchanged for small molecules.

Target-specific literature and dataset versions will be recorded in the relevant task contribution. COVID Moonshot remains a proposed future case, not an included dataset or completed benchmark.

### Advisory integration source inspection

Additional local source inspected at the Agent-Scientist revision above:

- [Plugin hook directives](https://github.com/boltzmannlabs/agent-scientist/blob/062351dd048c142840f78ea198f22417d983ccda/sci_cli/plugins.py) and [hook failure handling](https://github.com/boltzmannlabs/agent-scientist/blob/062351dd048c142840f78ea198f22417d983ccda/sci_cli/plugins_dispatch.py): guard semantics and failure behavior.
- [Tool dispatch](https://github.com/boltzmannlabs/agent-scientist/blob/062351dd048c142840f78ea198f22417d983ccda/model_tools.py) and [turn context](https://github.com/boltzmannlabs/agent-scientist/blob/062351dd048c142840f78ea198f22417d983ccda/agent/turn_context.py): observer/warning timing and context-hook limitations.
- [Code-execution RPC](https://github.com/boltzmannlabs/agent-scientist/blob/062351dd048c142840f78ea198f22417d983ccda/tools/code_execution_rpc.py) and [kernel ownership](https://github.com/boltzmannlabs/agent-scientist/blob/062351dd048c142840f78ea198f22417d983ccda/tools/code_kernel.py): task/session identity constraints.

These files establish integration options and limitations for discussion. No hook, middleware, warning-delivery path, or campaign attachment has been exercised by this contribution.
