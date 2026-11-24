# MD Agent Qualification Report

Packets executed: **62**

| Agent | Adapter | Qualification | Evidence |
|---|---|---|---|
| MD-01 — System Input Validation | PASS | PASS | fixture format, atom count, and finite coordinate/topology evidence verified |
| MD-02 — System Preparation | PASS | REVIEW | domain-specific trajectory/reference evaluator and agent output are required |
| MD-03 — Force-Field Selection | PASS | PASS | fixture format, atom count, and finite coordinate/topology evidence verified |
| MD-04 — Parameterization | PASS | REVIEW | domain-specific trajectory/reference evaluator and agent output are required |
| MD-05 — Solvation and Ion Placement | PASS | REVIEW | domain-specific trajectory/reference evaluator and agent output are required |
| MD-06 — Energy Minimization | PASS | REVIEW | domain-specific trajectory/reference evaluator and agent output are required |
| MD-07 — Equilibration | PASS | REVIEW | domain-specific trajectory/reference evaluator and agent output are required |
| MD-08 — Integrator and Timestep | PASS | PASS | fixture format, atom count, and finite coordinate/topology evidence verified |
| MD-09 — Thermostat and Barostat | PASS | REVIEW | domain-specific trajectory/reference evaluator and agent output are required |
| MD-10 — Simulation Execution | LIVE | PASS | live OpenMM CUDA result independently checked by core evaluator |
| MD-11 — Failure Diagnosis and Recovery | PASS | REVIEW | domain-specific trajectory/reference evaluator and agent output are required |
| MD-12 — Sampling Strategy | PASS | REVIEW | domain-specific trajectory/reference evaluator and agent output are required |
| MD-13 — Enhanced Sampling | PASS | REVIEW | domain-specific trajectory/reference evaluator and agent output are required |
| MD-14 — Trajectory Quality Control | PASS | REVIEW | domain-specific trajectory/reference evaluator and agent output are required |
| MD-15 — Structural Analysis | PASS | REVIEW | domain-specific trajectory/reference evaluator and agent output are required |
| MD-16 — Interaction Analysis | PASS | REVIEW | domain-specific trajectory/reference evaluator and agent output are required |
| MD-17 — Free-Energy Analysis | PASS | REVIEW | domain-specific trajectory/reference evaluator and agent output are required |
| MD-18 — Statistical and Uncertainty Analysis | PASS | REVIEW | domain-specific trajectory/reference evaluator and agent output are required |
| MD-19 — Resource Optimization | PASS | PASS | fixture format, atom count, and finite coordinate/topology evidence verified |
| MD-20 — MD Orchestrator and Audit | PASS | REVIEW | domain-specific trajectory/reference evaluator and agent output are required |
| MD-21 — Online Scientific Literature | PASS | REVIEW | resource claims require source URL, version, licence, hash, and independent retrieval evidence |
| MD-22 — Model and Checkpoint Discovery | PASS | REVIEW | resource claims require source URL, version, licence, hash, and independent retrieval evidence |
| MD-23 — Scientific Dataset Discovery | PASS | REVIEW | resource claims require source URL, version, licence, hash, and independent retrieval evidence |
| MD-24 — Resource Download and Cache | PASS | REVIEW | resource claims require source URL, version, licence, hash, and independent retrieval evidence |
| MD-25 — Model Compatibility | PASS | REVIEW | resource claims require source URL, version, licence, hash, and independent retrieval evidence |
| MD-26 — Dataset Integrity | PASS | REVIEW | resource claims require source URL, version, licence, hash, and independent retrieval evidence |
| MD-27 — Scientific Reproduction | PASS | REVIEW | resource claims require source URL, version, licence, hash, and independent retrieval evidence |
| MD-28 — Model Evaluation and Selection | PASS | REVIEW | resource claims require source URL, version, licence, hash, and independent retrieval evidence |
| MD-29 — Online Resource Update | PASS | REVIEW | resource claims require source URL, version, licence, hash, and independent retrieval evidence |
| MD-30 — Provenance and Licence | PASS | REVIEW | resource claims require source URL, version, licence, hash, and independent retrieval evidence |
| MD-31 — Protein Folding and Misfolding Specialist | PASS | REVIEW | domain-specific trajectory/reference evaluator and agent output are required |
| MD-32 — Protein–Protein Interaction MD Specialist | PASS | REVIEW | domain-specific trajectory/reference evaluator and agent output are required |
| MD-33 — Membrane Protein MD Specialist | PASS | REVIEW | domain-specific trajectory/reference evaluator and agent output are required |
| MD-34 — Nucleic Acid Dynamics Specialist | PASS | REVIEW | domain-specific trajectory/reference evaluator and agent output are required |
| MD-35 — Enzyme Mechanism MD Specialist | PASS | REVIEW | domain-specific trajectory/reference evaluator and agent output are required |
| MD-36 — Binding-Site Water Thermodynamics Specialist | PASS | REVIEW | domain-specific trajectory/reference evaluator and agent output are required |
| MD-37 — Conformational State Clustering Specialist | PASS | REVIEW | domain-specific trajectory/reference evaluator and agent output are required |
| MD-38 — Markov State Model Specialist | PASS | REVIEW | domain-specific trajectory/reference evaluator and agent output are required |
| MD-39 — Transition Path Analysis Specialist | PASS | REVIEW | domain-specific trajectory/reference evaluator and agent output are required |
| MD-40 — Replica Exchange MD Specialist | PASS | REVIEW | domain-specific trajectory/reference evaluator and agent output are required |
| MD-41 — Potential of Mean Force Specialist | PASS | REVIEW | domain-specific trajectory/reference evaluator and agent output are required |
| MD-42 — Ligand Unbinding Pathway Specialist | PASS | REVIEW | domain-specific trajectory/reference evaluator and agent output are required |
| MD-43 — Relative Binding Affinity Validation Specialist | PASS | REVIEW | domain-specific trajectory/reference evaluator and agent output are required |
| MD-44 — QM/MM Boundary and Region Specialist | PASS | REVIEW | domain-specific trajectory/reference evaluator and agent output are required |
| MD-45 — Machine-Learned Potential Validation Specialist | PASS | REVIEW | domain-specific trajectory/reference evaluator and agent output are required |
| MD-46 — Adaptive Sampling Controller | PASS | REVIEW | domain-specific trajectory/reference evaluator and agent output are required |
| MD-47 — Trajectory Reproducibility Auditor | PASS | REVIEW | domain-specific trajectory/reference evaluator and agent output are required |
| MD-48 — Statistical Convergence and Uncertainty Specialist | PASS | REVIEW | domain-specific trajectory/reference evaluator and agent output are required |
| MD-49 — MD Benchmark Dataset Builder | PASS | REVIEW | domain-specific trajectory/reference evaluator and agent output are required |
| MD-50 — End-to-End MD Qualification Orchestrator | PASS | REVIEW | domain-specific trajectory/reference evaluator and agent output are required |
| MD-51 — Molecular System Preparation Scenarios | PASS | REVIEW | fixture is valid, but diagnosis/recovery requires comparing agent output with the planted fault |
| MD-52 — Force-Field and Parameterization Failure Scenarios | PASS | REVIEW | fixture is valid, but diagnosis/recovery requires comparing agent output with the planted fault |
| MD-53 — Minimization and Equilibration Failure Scenarios | PASS | REVIEW | fixture is valid, but diagnosis/recovery requires comparing agent output with the planted fault |
| MD-54 — Production MD Execution Failure Scenarios | PASS | REVIEW | fixture is valid, but diagnosis/recovery requires comparing agent output with the planted fault |
| MD-55 — Trajectory and Structural Analysis Scenarios | PASS | REVIEW | fixture is valid, but diagnosis/recovery requires comparing agent output with the planted fault |
| MD-56 — Sampling and Convergence Failure Scenarios | PASS | REVIEW | fixture is valid, but diagnosis/recovery requires comparing agent output with the planted fault |
| MD-57 — Drug Discovery and Binding Scenarios | PASS | REVIEW | fixture is valid, but diagnosis/recovery requires comparing agent output with the planted fault |
| MD-58 — Machine-Learning Potential Scenarios | PASS | REVIEW | fixture is valid, but diagnosis/recovery requires comparing agent output with the planted fault |
| MD-59 — Online Model and Dataset Retrieval Scenarios | PASS | REVIEW | fixture is valid, but diagnosis/recovery requires comparing agent output with the planted fault |
| MD-60 — Compute and Resource Constraint Scenarios | PASS | REVIEW | fixture is valid, but diagnosis/recovery requires comparing agent output with the planted fault |
| MD-61 — Scientific Validation and Reproducibility Scenarios | PASS | REVIEW | fixture is valid, but diagnosis/recovery requires comparing agent output with the planted fault |
| MD-62 — Autonomous Agent and Orchestration Scenarios | PASS | REVIEW | fixture is valid, but diagnosis/recovery requires comparing agent output with the planted fault |

## Interpretation

Adapter PASS means the fixture was consumed by the selected software adapter. Qualification PASS is reserved for independently verifiable checks. REVIEW means the required trajectory, reference, sampling, recovery, or provenance evidence is not present; it is not a successful scientific result.
