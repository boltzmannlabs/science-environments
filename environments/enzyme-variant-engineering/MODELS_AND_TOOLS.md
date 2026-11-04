# Models and Tools

This environment uses an existing Agent-Scientist installation. It adds no model
weights, dependency bundle or second execution service.

| Component | Role | Requirement |
| --- | --- | --- |
| Agent-Scientist | Research, planning, tool execution, sessions and native delegation. | An installed version supporting the capabilities used by the task. |
| Configured language model | General reasoning; assisted runs also use native delegated roles. | Existing user authentication and native model configuration. |
| Boltzmann | Candidate scientific operations through the maintained catalogue. | Required only for operations chosen from that provider; native authorization applies. |
| ToolUniverse | Discovery and execution of suitable operations when connected. | Required only for chosen operations; service-specific dependencies may apply. |
| RCSB PDB | Public starting structures and associated sequence/entry metadata. | Est30 starts from entry 1TQH. |
| Scientific predictors and simulators | Sequence design, properties, structures, complexes and reaction analysis. | Selected per task; record the actual executable method and its requirements. |
| Domain subagents | Proposal and critique for the assisted comparison. | Supplied and reviewed separately through Agent-Scientist; no definitions are bundled here. |

## Selection and reproducibility

The workflow is not tied to one predictor or software vendor. For every selected
operation, record its method/version, parameters, input and output identifiers,
units, chemical/structural state and actual execution evidence. If a service does
not expose a version, record that limitation rather than invent one.

A tool listing, package description or published prediction does not establish
that a required calculation can run. Use native discovery and current schemas.
CSV headers and field types come from the chosen operation's contract.

## Compute and dependencies

The specification and task files need no GPU or model weights. Actual structure
prediction or simulation may need a GPU, model files, licensed software or a
remote service. Those requirements depend on the chosen method; this contribution
does not install them or prescribe a shared NFS location.

Scientific runs use the existing service permissions. Keep account credentials
and private connection configuration in SCI's normal user state, never here.
Use bounded concurrency and preserve other workloads on a shared server.

## Version and evidence boundaries

Definitions of saved subagents, their code and their review lifecycle are owned
by [Agent-Scientist](https://github.com/boltzmannlabs/Agent-Scientist).
Its [saved-specialist documentation](https://github.com/boltzmannlabs/Agent-Scientist/blob/main/website/docs/user-guide/features/saved-specialists.md)
describes native setup. This environment does not assert that another installation
already has the required named roles.

Scientific accuracy, runtime and cost are measured during the actual task.
No completed model comparison or improved enzyme is claimed by this tool inventory.
