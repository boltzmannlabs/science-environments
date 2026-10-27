# Configuration and dependency boundary

Use Python 3.10+ for the included technical CLI and tests; no pip dependencies are needed. That is not the dependency specification for scientific inference.

Copy templates into a new external run/project directory before filling them. Leave the repository and source case studies unchanged. `environment.example.json` intentionally has no installed paths; preflight should exit 2 with BLOCKED_MISSING_CONFIGURATION. It checks files and hashes without executing commands or loading models. Do not store API keys/tokens here.

`capability_registry.json` records what this contribution implements versus externally observed tools. External host observations are not portable deployment claims. Recheck actual SCI schemas, source/checkpoint versions and rights on each host. Consult the destination build's local operating manual; installing the skill does not register native tools.

The original host separately exercised OligoFormer/RNA-FM, RN.Ai-Predict/RNAiSpline, a frozen Ridge asset, ViennaRNA and human GENCODE/seed references. Their historically observed Python/CUDA choices are documented in the central research references, not an automatic cross-platform lockfile. No single environment.yaml can honestly install/validate this heterogeneous stack without further integration work and license/asset approvals.

Use `scripts/run.py verify-history --evidence-root /absolute/KRAS_siRNA_case_study` only when the user authorizes local access to the original historical files. It reads expected small summary/receipt files and checks hashes but does not rerun original scientific or verification scripts. Missing evidence returns a structured blocker rather than inventing results.
