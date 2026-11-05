# Enzyme Variant Optimization Tasks

Each task is a complete design assignment using the [shared workflow](../ENVIRONMENT_SPEC.md). Agent-Scientist must generate variants with actual tools, evaluate them, execute a results-driven revision and compare final candidates with the parent. The tasks do not prescribe a vendor or one universal design algorithm.

Every case file contains its own Description, Target, Design Constraints, Computational Tool Capabilities, Evaluation Metrics, Expected Output and Important Instructions. The complete eight-stage execution table, initial limits and required artifacts are included in each task; the shared specification supplements them rather than replacing them.

| Task | Objective | Main design question |
| --- | --- | --- |
| [Est30 and MHET](est30_mhet.md) | Improve substrate processing while managing stability. | Can pocket redesign improve reaction-relevant evidence without losing the fold or catalytic features? |
| [RML stability](rml_stability.md) | Improve lipase stability while retaining substrate interactions. | Can a tool-generated design improve stability without harming the active site or lid? |
| [LEH stability](leh_stability.md) | Stabilize an epoxide hydrolase while retaining functional structure. | Do orthogonal checks eliminate apparently favorable but unreasonable variants? |
| [BLA high-temperature performance](bla_high_temperature.md) | Balance α-amylase stability and catalytic integrity. | Can less flexible designs retain the functional motions and metal environment? |
| [AtHOL1 substrate expansion](athol1_substrate.md) | Improve support for a non-native substrate. | Can redesign accommodate the substrate while retaining the reaction's required arrangement? |

Start with RML or LEH for the first full execution. AtHOL1 has the greatest chemistry/evaluator requirements. This order reflects preparation effort, not an expectation that improvement will be easy.

Use the limits in [workflow configuration](../config/workflow.json) unless a reviewed comparison freezes different equal limits. Each run targets approximately twelve initial variants, models the parent and at least five eligible initial candidates in detail, and evaluates at least one new tool-generated sequence batch based on actual results. Assess all final candidates; a smaller justified final set is acceptable.

Published winners and historical numerical results are evaluator information, not generation inputs. Do not read `benchmark/REFERENCE_VALUES.md` or the target papers' winner tables during design. Search other primary sources for parent identity and reaction chemistry. These are information-use rules, not an OS sandbox; record exposure if it occurs and use enforced isolation separately when claiming a blinded benchmark.
