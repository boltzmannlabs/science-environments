# Agent-alone workflow and reporting source

Executed tasks retain actual historical agent-alone Python with source/export hashes. Task source folders distinguish exported execution code from future additions. Archived code requires its original frozen inputs and dependencies; a complete portable replay is not claimed.

`benchmark_reports.py` builds one concise Word comparison per task from saved published, agent-alone and newly calculated reference values. It makes no model or network calls. `evaluation.py` retains the original offline endpoint comparator. Native SCI infrastructure and scientific algorithms supplied by external tools remain external.

Archived workspace paths are parameterized through ENZYME_CAMPAIGN_ROOT, ENZYME_REPRODUCTIONS_ROOT, SCI_SOURCE_ROOT, SCI_HOME and BOLTZYME_TOOLS_ROOT. Two LEH verifier scripts also require the exact private input-key environment setting documented in their manifests; those storage keys are not published.

[Shared stability-prediction code](shared/stability_predictions/README.md) supports the additional RML/LEH checks. Run-specific extraction/audit copies are kept outside the repository.
