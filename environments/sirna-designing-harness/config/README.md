# Configuration and dependency boundary

## Portable technical environment

Python3.10+ and its standard library run the technical CLI, report generator and tests; no pip dependency is required. [technical_gate_policy.json](technical_gate_policy.json) records explicit research-operational bounds and all seven mandatory technical categories. Missing categories cannot be removed to obtain a pass. A policy revision must be explicit and separately evaluated; the included policy preserves the exercised native defaults.

[output_contracts.json](output_contracts.json) separates the positive `PASSED_DECLARED_TECHNICAL_GATES` aggregate from individual gate statuses and downstream scientific scopes. The technical report retains raw model statuses, native gate records, predicted/calculated properties, source Ridge annotations, reproducibility differences and risk flags.

Use the recorded bundle at [bundle.json](../results/case_studies/KRAS_14_technical_validation/bundle.json) as a concrete input example, not as expected results for another target. All evidence paths are relative and SHA-256 bound. Source job identity and a distinct earlier job must be declared. Guide/passenger RNA cores are unchanged; DNA-reference comparison requires literal explicit approval. No credential is part of this contract.

## Scientific execution configuration

[environment.example.json](environment.example.json) is intentionally incomplete. Copy it into a new approved project/run directory, fill reviewed paths/checksums and verify rights. `preflight` checks presence and hashes without running backends; the untouched template must report `BLOCKED_MISSING_CONFIGURATION` with exit2.

The original host separately executed OligoFormer/RNA-FM, RN.Ai-Predict/RNAiSpline, the frozen Ridge estimator, ViennaRNA and human transcript/seed reference tools. They remain external scientific dependencies, with separate runtimes, source/checkpoint versions, licensing and permissions. The repository is not a universal installer and does not modify SCI profiles or service settings. No single conda/pip lockfile is asserted to reproduce the heterogeneous scientific stack.

[capability_registry.json](capability_registry.json) distinguishes repository-executable checks/reports from separately configured scientific integrations. Recheck tools, schemas, resources, rights and actual inference on the destination host. External historical observations are not portable deployment claims.

## Evidence reuse

`verify-technical-case` verifies the included bounded recorded assessment without original sources. `technical-report` rechecks the evidence and creates a new report, not a new scientific prediction.

`verify-history --evidence-root /absolute/approved/KRAS_siRNA_case_study` optionally checks the expected small historical summaries/receipts on the original host. Only use it with approved local access. It never calls an old verifier that writes to originals and never reruns scientific models. Source metadata paths are locators, not authority to read or upload unrelated files.
