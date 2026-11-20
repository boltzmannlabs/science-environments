# Clarithromycin IR: formulation and dissolution research

## Question and boundary

Can 500 mg clarithromycin plus exactly eight specified excipients yield a constraint-valid 800 mg IR coated-tablet exploration set and scientifically informative next experiments? Does changing the curve-analysis workflow improve reconstruction of withheld published observations?

This research is not ranolazine ER, the earlier 750 mg exploratory screen, or proof of therapeutic equivalence. The [environment](../../environments/formulation_environment/README.md) implements the current study with matched Task - 01 folders.

## Literature-informed failure modes

Carboxylate/citrate-associated surface gel can impede penetration/disintegration (R2). Metastable form I can release more slowly from tablets despite faster intrinsic dissolution when surface form IV crystals form (R3). Acidic-medium gelation and degradation can couple (A1). API molecular descriptors or isolated solubility therefore cannot establish a tablet release profile. Exact recipe/process/medium applicability must be checked.

R1 is a nearest practical 500 mg IR comparator, not the same eight-excipient design. Its croscarmellose/starch/talc and coating differ, coated weight is roughly 875 mg, and individual-unit source records are unavailable. Six vessels are described. Its reported >100% values are preserved; they do not indicate extra physical drug release. Full versus truncated f2 arithmetic is not formal similarity.

## Executed findings

- Original 24 composition-valid designs under assumed bounds; information-design selection does not rank efficacy.
- Actual PTCalc.Core 1.1.0: 288 fit records on published curves. All early KP mechanism interpretations rejected after inspecting the all-point fallback.
- Source OF7 f2 reported 59.658; recomputed displayed-mean arithmetic 58.799762. This remains a source consistency issue, not a product pass/fail decision.
- v2: 15 deduplicated profiles, 11 configurations, 1,155 profile/model/split evaluations. Capped Weibull's forward30 RMSE fell 39.88% relative to our free model; aggregate LOTO error worsened 4.82%. Literature measurements are the target, not a defeated competing product.
- Four new recipe corners complete a nine-point CP/PVP factorial; the expanded pool has 28 valid designs. Interaction/curvature become algebraically estimable after actual responses are collected.

## Unresolved scientific work

No measured candidate dissolution, compatibility, stability or manufacturing data; no external batch/formulation holdout; no calibrated recipe intervals. Reference identity, method criteria, API solid form/PSD, grade/lot and process windows remain unverified. Early 1/2/3-minute samples, actual batches and stability are planned, not executed. Independent scientific review is required before product conclusions.

## Reproducibility

[Task](../../environments/formulation_environment/tasks/task-01-clarithromycin-ir-formulation-dissolution/README.md), [benchmark](../../environments/formulation_environment/benchmark/task-01-clarithromycin-ir-formulation-dissolution/README.md), [results](../../environments/formulation_environment/results/task-01-clarithromycin-ir-formulation-dissolution/README.md), [references](references.md). Root license selection remains pending; citations do not convey rights to full articles.