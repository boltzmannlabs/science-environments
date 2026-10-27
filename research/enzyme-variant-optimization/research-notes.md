# Enzyme variant optimization: research and design notes

## Scope

The task starts with an existing enzyme, its substrate, a prepared structure, and catalytic residues that must be preserved. Scientific tools evaluate candidate variants, and their results guide later decisions. When a benchmark uses a fixed list of previously measured variants, the agent must choose from that list. A new sequence outside the list has no experimental test answer in that benchmark.

The [environment specification](../../environments/enzyme-variant-optimization/ENVIRONMENT_SPEC.md) defines the executable contracts. This contribution packages existing development work for review rather than claiming a finished scientific benchmark.

## Why an environment and specialist

Agent-Scientist already provides general planning, tool use, and delegation. The environment adds checks that keep candidate identities and results consistent, records what happened, and enforces task limits. Both agent approaches use these common facilities. The specialist adds a separate proposal and review process, with decisions and results saved through DiscoveryRSI. It uses the existing language model. The comparison must establish whether that extra process helps.

## Evidence categories

- Source/contract tests establish code behavior and representation checks.
- Synthetic replay demonstrates state transitions and feedback under controlled fixtures.
- Real tool completion establishes that a particular job returned an interpretable output.
- Computational activity, stability, confidence, docking, or geometry results establish only their specified prediction/measurement.
- Experimental improvement requires suitable measured evidence and an independent evaluator.

The branch's fresh validation summary is linked from the environment `STATUS.md`. Ongoing scientific campaigns are not accessed or presented as completed benchmark results here.

## Scientific decisions and uncertainties

Activity depends on the enzyme, substrate, reaction state, and assay conditions. Stability, solubility, folding confidence, binding pose, and catalytic geometry are complementary signals; they are not interchangeable activity measurements. Reaction-specific geometric criteria require a justified state and source, rather than universal cutoffs. A critic's score evaluates an investigation proposal and cannot supply an assay label.

Each property prediction belongs to a particular sequence. Each quality or geometry result belongs to the structure version actually checked. A ligand's component name alone does not prove its chemical identity. The current implementation compares a returned SDF molecule file with the requested molecule and the returned coordinates. Without that information, it cannot mark ligand identity as verified.

The proposed three-way comparison holds the objective, public inputs, tool access, and resource ceilings constant. The fixed reference freezes its settings and ranking before results; the base agent and specialist may choose their own workflow. Model calls from proposer and critic count against the specialist's budget. Protected experimental answers stay outside tested-agent access. Full protocol and scoring implementation belong to `science-benchmarking`.

## Next research work

Finish live handoff qualification, review the fixed reference and assay endpoint, freeze a suitable development/evaluation split with an independent evaluator, and measure whether the specialist adds enough quality, reliability, or efficiency to justify its additional calls. Assess training or model changes only after a demonstrated gap. The proposed benchmark and current implementation are distinct from de novo enzyme creation.

Sources and source-version links are collected in [references.md](references.md).
