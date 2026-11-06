# Antibody Design

A scientific environment for antibody discovery, design, optimization and evaluation with Agent-Scientist. It brings together explicit scientific tasks, task-specific benchmarks and a common structure for agent implementations, execution scripts, specialized skills and reproducible results.

The environment's development scope covers **monoclonal, bispecific and multispecific antibodies**, including **de novo design and optimization of existing antibodies**. The [environment specification](ENVIRONMENT_SPEC.md) defines the scientific requirements guiding these capabilities.

## Scientific Scope

| Area | Design focus |
| --- | --- |
| Monoclonal antibody design | Target-directed candidate design, reference-guided refinement, epitope recognition and structural assessment. |
| Bispecific antibody design | Two intended binding specificities, with evaluation of each component and the assembled molecule. |
| Multispecific antibody design | Three or more intended binding specificities, with attention to component compatibility and overall architecture. |
| De novo design | Candidate discovery from a defined target and design objective, using an optional framework or scaffold. |
| Antibody optimization | Interaction quality, specificity, humanization, developability and molecular architecture, guided by declared constraints. |
| Reconstruction and benchmarking | Controlled comparisons of sequence recovery, structural agreement and other task-defined endpoints. |

Tasks specify the molecular format and representation appropriate to their objective, including paired-chain antibodies, fragments, scFv constructs and other architectures described in the specification.

