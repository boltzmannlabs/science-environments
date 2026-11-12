# Hit identification environment specification

Environment ID: `virtual-screening`.

Provide a scientific objective, target information, a fixed compound library and reference controls. The agent determines a suitable approach and reports the results, scientific reasoning, evidence, failures and limitations.

Task documents contain Objective, Target, Inputs, Constraints, Expected Output and Important Instructions. Task-specific output counts are permitted. Tools, a fixed sequence of scientific methods, simulations, published winner identities and source-score targets are not prescribed in the agent-facing task.

Keep benchmark definitions, evaluation methods, metrics, comparison criteria and source-reference data in `benchmark/`. Keep experiment outputs, benchmark results, execution records and evaluation reports in `results/`. Supply the execution agent only the selected task and scientific inputs. Prediction, preparation and scientific interpretation remain execution responsibilities.

No automatic scientific pass/fail criterion is defined for this version. File validation checks bundle consistency; it does not certify scientific execution or results. Resource limits and job permissions are supplied with each execution request rather than imposed by the task document.

The first task uses the original 6CM4 crystal complex, reference sequence and the paper's 400 source molecular records. Source duplicates and unspecified stereochemistry are preserved and documented. No inferred receptor is substituted into the input bundle.
