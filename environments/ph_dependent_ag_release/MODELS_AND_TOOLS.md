# Models and tools

Choose implementations independently for the selected task. Use open-source software or software whose academic/noncommercial license permits the intended use. Check code, model-weight, database and service terms separately; save the applicable terms, version and access conditions in the run artifacts. Free access alone does not establish an open-source license.

## Modeling and static assessment

Resolve molecular identity and construct boundaries; prepare the target and antibody/scaffold; generate sequences only when requested; predict structures and complexes as needed; assess geometry and actual candidate-specific confidence outputs; estimate pKa values and relevant protonation microstates; and calculate condition-aware scores under matched definitions. Apply requested property or specificity assessments only when relevant to the task.

A predictor must represent pH or protonation to support a pH-dependent prediction. Changing a label on an otherwise identical pH-insensitive inference does not do so. Model-training correlations, selection cutoffs and published performance summaries are not outputs for the evaluated system.

## Simulation assessment

After the model-stage selection is frozen, prepare consistent physical systems and controls. Use suitable protonation sampling, equilibration, production sampling and any justified enhanced sampling. Calculate the task's actual observables from native trajectories and state histories. Check sampling support, uncertainty and convergence for each endpoint.

Fixed protonation assignments do not estimate sampled protonation probabilities. Local residue–water energies do not constitute binding free energies. Biased populations require a valid estimator or reweighting. Preserve these distinctions in reports.

## Capability and execution records

Before production, verify format support, molecular context, parameter compatibility, licenses, required resources and the complete path from raw output to the requested observable. Record actual invocations, versions, input hashes, seeds, outputs and failures. A catalogue entry, pilot or script is not completed scientific execution. Missing capabilities remain explicit gaps.

The detailed workflow and intended evidence requirements are in [ENVIRONMENT_SPEC.md](ENVIRONMENT_SPEC.md). Concrete runtime interfaces and an execution backend remain to be implemented.
