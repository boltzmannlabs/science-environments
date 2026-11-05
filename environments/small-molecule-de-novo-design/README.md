# De novo small-molecule design

**Status: Specification.** Target: p38α. Related issue: #46.

Generate molecular candidates for one p38α target. The agent retrieves and prepares the public 1A9U structure for common final docking with Smina. Ten final records form the evaluation panel; an up-to-three shortlist is separate.

- [Agent task](tasks/p38alpha-design.md).
- [Environment specification](ENVIRONMENT_SPEC.md).
- [Owner/evaluator reference index](REFERENCES.md).
- [Shared status](../../research/small-molecules/STATUS.md).

Give the execution agent the task, property constraints (or explicitly none),
and resource limits. It discovers suitable authorized Boltzmann tools in the
active Agent Scientist profile and prepares or reuses and verifies the
input and scoring bundle. A separately controlled evaluator and a frozen shared
bundle are needed for a fair independent comparison. This is a specification;
the preparation and evaluation infrastructure have not been validated here.
