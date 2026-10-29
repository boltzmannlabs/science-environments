# COVID Moonshot Mpro retrospective selection task — preparation dossier

**Status: PENDING_DATA_AND_PROTOCOL_REVIEW.** This directory contains a task proposal, not a runnable scientific task or a completed evaluation. Reviewed on 28 October 2026. No compound labels, generated molecules, or scientific tool outputs are bundled here.

## Intended question

Can an agent prioritize compounds with improved measured Mpro inhibition relative to a supplied starting lead, within a frozen set of already measured compounds and a declared resource allowance?

This would exercise the general environment on one specific target. It measures retrospective selection within a library. It cannot establish experimental improvement of newly generated analogues, antiviral efficacy, selectivity, or drug-development success.

The [source review](../../../../research/small-molecule-lead-optimization/moonshot-task-review.md) records the accessible files, licence evidence, and assay/identity limitations. The [general comparison protocol](../../tests/COMPARISON_PROTOCOL.md) defines the information to settle before comparing the base agent and environment-assisted agent.

## Source candidate

The inspected public candidate source is [ASAP Discovery's cleaned Moonshot repository](https://github.com/asapdiscovery/COVID_moonshot_data_clean), particularly its [achiral/enantiopure CSV](https://github.com/asapdiscovery/COVID_moonshot_data_clean/blob/main/cdd_achiral_enantiopure_dates_2023_10_18_filt.csv). It offers a starting point for curation, not an already qualified benchmark cohort. These `main` links are moving references: an immutable source revision and raw-file hashes have not yet been recorded for this task.

The planned primary endpoint is source fluorescence-assay inhibitory potency, subject to methods and compatibility review. No numeric potency target, hit threshold, selection count, series, lead, split, or resource allowance has been chosen.

## Proposed task assets

These are proposed artifact roles, not frozen filenames or an implemented task schema.

| Agent-visible assets | Evaluator-only assets |
| --- | --- |
| Task question, target context, starting lead(s), and the exact allowed candidate membership. | Compatible measured labels for final-scored compounds, assay qualifiers, and source-row/identity crosswalk. |
| Candidate IDs and reviewed molecular representations; approved source/structure context when required. | Source snapshot and hashes, curation decisions, duplicate groups, and excluded records/reasons. |
| Explicitly designated visible baseline/development observations with their endpoint and assay context. | Frozen final-scoring rules, reference comparator outputs, and evaluation receipts. |
| Permitted capabilities, declared allowances, expected submission format, and selection eligibility rules. | Locked membership and representation checks, input/output hashes, and protocol version. |

Reference measurements must be outside the tested agent's actual accessible files, tools, and artifacts. Do not distribute the raw measured-data CSV as an agent task input and then describe its labels as hidden. Because the source is public, network/retrieval rules and possible model exposure must also be addressed. Opaque compound IDs alone cannot establish independence when molecular structures can identify a published compound.

## Curation work before a runnable task

1. Retrieve an immutable source snapshot, record the exact URLs/revision, retrieval time, byte hashes, and applicable notices. Review the referenced assay methods.
2. Define molecular-form eligibility and resolve source identity issues without silently converting compounds. Preserve stereo, salt, tautomer, and normalization decisions in an evaluator crosswalk.
3. Review quantitative versus censored measurements and assay-quality fields. Decide before comparing agents whether a compatible quantitative-only cohort is appropriate or whether interval-aware scoring is required. Do not replace censored values with invented point measurements.
4. Resolve duplicates and repeated assays, preserving the source rows and a documented aggregation or exclusion rule. Do not mix endpoints merely to increase the cohort.
5. Identify a scientifically justified starting lead and any congeneric series using independent provenance. Select a frozen candidate cohort without tailoring its membership to either agent's results. The cleaned file alone does not establish a temporal or single-series split.
6. Specify visible baseline/development evidence and protected final labels, then review training/source exposure for the models used. Public historical data cannot support a claim that a model has never encountered the compounds.
7. Agree the primary metric, selection count, tie/missing-data policy, allowances, repeats, baselines, and interpretation. Freeze task assets and final-evaluation rules before a comparison begins.
8. Verify the actual task/evaluator access boundary and submission-freezing behavior. Then run a data/identity dry check and record the resulting eligibility counts before any scientific evaluation.

These steps are task-preparation gates. The environment's warning-only behavior does not make a task scientifically eligible when the required curation or evaluator boundary is unresolved.

## Evaluation intent

The agent submits a final ordered or unordered selection, as the reviewed task later specifies. Final scoring joins those exact frozen candidate identities to compatible measured labels in the evaluator. A different molecular form, unknown member, duplicate submission, or late candidate replacement must not silently acquire another compound's measurement.

The report should include per-selected-compound assay evidence and qualifiers, comparisons to the visible starting lead where valid, task-defined aggregate metrics, eligibility, observable usage, and unresolved costs or internal service work. An allowed generated analogue outside the measured library would require another evaluation route; it cannot receive an experimental score through this task.

## Current readiness

Accessible source files and licence documentation have been identified. Exact immutable source capture, full data audit, assay-method qualification, lead/series selection, final metric, protected-label packaging, and an actual independent run remain outstanding. No complete source dataset was imported, no cohort counts were computed, and no scientific or base-agent comparison result is claimed.
