# Tests and validation boundaries

**Version 0.1 has executable software tests.** They use artificial observations and temporary campaign storage. A native integration test uses the actual Agent-Scientist loader and registry in an isolated host context. No test here establishes improved compounds or a successful model-driven research episode.

From the environment directory:

```bash
python3 -m unittest discover -s tests -v
```

The native test is explicitly skipped unless both host paths are supplied:

```bash
LEADOPT_AGENT_SOURCE=/absolute/path/to/agent-scientist \
LEADOPT_AGENT_PYTHON=/absolute/path/to/agent-scientist/.venv/bin/python \
python3 -m unittest discover -s tests -v
```

See [validation evidence](../results/validation.md) for the executed command, versions and results. [Installation checks](../scripts/README.md) additionally build/install a wheel offline into a fresh environment outside the source tree.

## Implemented coverage

| Test file | Behaviors exercised |
| --- | --- |
| [test_environment.py](test_environment.py) | Schema export consistency; task intake and rollback; compatible comparisons; objective directions; observation/action association; pending outcomes; usage categories; immutable identity; frozen evidence; evaluator identity/receipt checks and overruns. |
| [test_critic.py](test_critic.py) | Independent adversarial tests for unsupported objectives, incompatible/censored/ambiguous evidence, numeric overflow, concurrent/idempotent writes, restart, session association, unchecked violations and warning-only continuation. |
| [test_evaluation_critic.py](test_evaluation_critic.py) | Missing/unknown/pending resource evidence; exact allowance versus overrun; evidence-kind/scorer contradictions; invalid final ranges; immutable final scoring and identity binding. |
| [test_plugin.py](test_plugin.py) | Side-effect-free registration, schema discovery, explicit session attachment, association errors, installation collision protection and visible storage failures. |
| [test_plugin_native.py](test_plugin_native.py) | Isolated installed-directory discovery through the real host, skill lookup, tool registry dispatch, campaign/check/record operations and unloading. |

Data-integrity errors are distinct from advisory findings. The environment may reject malformed records or a conflicting candidate identity while still permitting a known task-rule violation to be recorded. Its checks never submit scientific jobs or enforce task budgets. Exact budget consumption warns but is not an overrun; unresolved usage cannot earn a final eligibility pass.

## Synthetic example

[The runnable fixture](../tasks/synthetic/README.md) exercises an entire scripted record/evaluation sequence. Its structures, counters and values are labelled artificial, and its reference labels are public. This checks software behavior, not agent intelligence, assay performance or hidden-label isolation.

## Qualification still required

The installed skill still needs model-driven qualification with the intended runtime and actual scientific tool results. Live checks need dated request/job/artifact evidence and validated result-to-candidate associations. This implementation uses explicit agent records and does not automatically intercept calls; tests cannot establish complete accounting for unrecorded activity.

Scientific comparison requires a separately approved task, matched starting information/tools/resource boundaries, a frozen protocol, repeated runs and appropriate baselines. Use the [comparison protocol](../benchmark/PROTOCOL.md). A different predictor does not automatically provide independent evidence; reuse of the search scorer cannot be labelled transfer to another predictor.

The offline evaluator binds a submission receipt to preregistered final rules and reference identities. It does not deploy an access sandbox or verify prior model exposure. Real protected answers must remain outside the tested agent's filesystem and tools. Public data exposure, censored measurements, molecular forms and assay compatibility require separate review.

[COVID Moonshot](../tasks/covid-moonshot/README.md) remains a preparation dossier. No real case, scientific service run, base-agent comparison or scientific performance result is supplied here.
