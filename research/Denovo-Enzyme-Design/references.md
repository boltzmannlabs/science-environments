# Denovo Enzyme Design — References

Sources support the [environment specification](../../environments/Denovo-Enzyme-Design/ENVIRONMENT_SPEC.md); they do not establish that the proposed environment has been implemented or validated.

- Task organization reference: [BioDesignBench binder_001](https://github.com/RomeroLab/BioDesignBench/blob/main/examples/demo_task/binder_001.md). The task, repository README and LICENSE were read. This package uses original enzyme-task text organized using that example; it does not reproduce the binder task body.
- [BioDesignBench LICENSE](https://github.com/RomeroLab/BioDesignBench/blob/main/LICENSE) contains Apache License 2.0, while the checked README describes code as MIT. That upstream metadata discrepancy remains unresolved. No upstream code or task body is redistributed here.

## Task format and scientific foundations

The agent task retains the reference's Description, Target, Design Constraints, Expected Output, Constraints and Important Instructions sections. Required Execution Steps replaces its software-list section to meet the user's revised requirement. The original binder-specific targets and numerical limits are not used as enzyme criteria.

| Scientific source | Relevance |
| --- | --- |
| [Computational enzyme design by catalytic motif scaffolding](https://doi.org/10.1038/s41586-025-09747-9) | Evidence that catalytic geometry and scaffold design matter to functional de novo enzymes; demonstrated reactions do not establish universal capability |
| [Curated enzyme mechanisms and catalytic-site evidence](https://doi.org/10.1093/nar/gkx1012) | Reaction-specific roles, state definitions and supporting literature for profile preparation |
| [Enzyme specificity prediction using cross-attention graph neural networks](https://doi.org/10.1038/s41586-025-09697-2) | Evidence that substrate compatibility is a distinct prediction problem; it does not substitute for full reaction chemistry |

The required operations, chemistry checks and controller behavior are defined independently of scientific software selection. Numerical acceptance thresholds, prediction applicability and chemical-method adequacy require reaction-specific qualification. The reward coefficients and learning procedure are proposed configuration choices; no training result is claimed.
