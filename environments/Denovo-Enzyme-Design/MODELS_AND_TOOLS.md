# Models and tools

Scientific models are selected for the requested reaction, assembly and operating domain. The environment defines required operations; the run's capability registry records exact tool identifiers, versions, schemas, settings and limitations.

## Provider policy

In `agent_selected` mode, discover real executors through Boltzmann or ToolUniverse. A catalogue entry is not proof of an accessible backend or suitable combined capability. Do not install local predictive models, download their weights, train substitutes or patch inference as an automatic fallback.

The generic configuration contains a documented external-chemistry exception. The user's current platform-only pilot request excludes that exception: freeze and enforce this stricter request before initialization. `tools_specified` mode preserves the request's exact implementations and allowed providers; do not silently substitute another model.

Small Python scripts may prepare and convert inputs, map atoms/residues/chains, inspect coordinates and analyze real outputs. They cannot replace a scientific predictor or turn a descriptor into evidence of solubility, activity or catalytic mechanism.

## Required capabilities

| Operation | Capability and evidence needed |
|---|---|
| Reference and reaction resolution | Traceable sequence, biological assembly, reaction and mechanistic records; explicit uncertainty and mappings. |
| Backbone generation | Verified support for the requested assembly, catalytic motif and ligand/state representation; structural-integrity review of actual outputs. |
| Sequence design | Correct fixed/designable residue policy; identical sequence copies for a homodimer; independent sequence verification. |
| Folding and assembly assessment | Sequence-bound independent predictions, disclosed MSA/template/restraint information, applicable controls and geometry/interface checks. |
| Solubility and aggregation | Applicable prediction endpoints and controls; descriptors and aggregation hotspot counts alone do not establish solution behavior. |
| Operating-condition characterization | Distinct thermal, pH and other requested endpoints, with uncertainty and domain applicability. Tm, pH optimum and pKa are not interchangeable. |
| Catalytic chemistry | State-specific mapping, protonation, substrate stereochemistry, control-tested geometry and an applicable reaction calculation for claims that require it. |

Classical dynamics, geometry scores and predicted catalytic rates are adjuncts. None alone establishes a complete reaction mechanism, a free-energy barrier or experimentally measured activity.

## Execution evidence and review

Require actual invocation receipts, provider/job identifiers when available, raw outputs and hashed input/output bindings. Record unavailable versions instead of inventing them. Reviewers evaluate the artifacts and scientific applicability; their opinions cannot replace missing calculations or override a failed mandatory gate. Keep independent eligible work moving and report a partial outcome when a required capability remains unavailable.

See [runtime contracts](src/CONTRACTS.md#execution-evidence), [configuration](config/environment.yaml) and the [scientific specification](ENVIRONMENT_SPEC.md).
