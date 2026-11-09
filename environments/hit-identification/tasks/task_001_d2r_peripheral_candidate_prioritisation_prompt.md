# Agentic execution prompt — task_001_d2r_peripheral_candidate_prioritisation

Use case: autonomous execution of this task by an agent scientist using the Boltzmann small-molecule discovery suite.

```text
Execute this task autonomously:

https://github.com/boltzmannlabs/science-environments/blob/Boltchem/environments/hit-identification/tasks/task_001_d2r_peripheral_candidate_prioritisation.md

Use the Boltchem branch and work from environments/hit-identification/ so the supplied input paths resolve correctly.

Read task.md and the supplied input metadata. Use your own scientific reasoning to design an appropriate workflow, select relevant tools from the Boltzmann small-molecule discovery suite, execute the work and interpret the results. Do not perform molecular dynamics simulations.

I authorize you to upload the supplied public inputs, submit Boltzmann jobs, monitor execution and retrieve results. Make routine decisions and resolve recoverable problems without asking for confirmation. Request input only if an essential unresolved dependency prevents further progress.

Base your recommendations on your executed results. Do not use evaluator-only outcomes to guide candidate selection.

Complete the outputs specified in task.md, including the ranked candidates, assessment and detailed scientific report. Retain supporting inputs, settings, job identifiers and result artifacts. Explain consequential decisions, uncertainty, failures and limitations.

Continue through execution and reporting; do not stop at a plan or job submission. Report incomplete work honestly without inventing results.

Finish with the completion status, principal findings and paths to all deliverables.

Do not modify task.md, commit changes or push to GitHub.
```
