# Zhang cellulase and β-glucanase: agent-alone results

## What is compared

Published Pythia/ESM scores are compared with our scores for the same variants and backgrounds. Our retained candidates and final published variants are also compared using common property predictors calculated in this work.

## Parent used

Published supplementary sequences: cellulase WT, 312 residues; β-glucanase WT, 215 residues.

The sequences were extracted from the original supplementary information. Published M2/M5 scoring backgrounds and final M5/M7 sequences are retained separately with their exact mutation sets.

## Calculations

Pythia used WT structures; ESM used the paper’s stabilized M2/M5 backgrounds. Newly predicted coordinates differ from the original paper inputs. Unitless score agreement and predicted Tm/solubility are presented as separate measurements.

The benchmark keeps published numbers and values calculated in this work separately labeled. Parent-relative changes use the exact parent recorded for each candidate.

The report shows leaders under the common negative-log-likelihood score convention. E158C/G74P opposite-sign diagnostic entries remain in the original candidate CSVs.

## Findings
Computational execution completed. Sealed structure/inference/scoring outputs retained; historical settings/eligibility gaps remain.

## Files

- [Benchmark report](../../../benchmark/evaluation/task_006_zhang_hydrolases/comparisons/benchmark_report.md)
- [Published reference values](../../../benchmark/reference_data/task_006_zhang_hydrolases/references.md)
- [Candidate sequences](sequences/sha256-2bfa1ad042ea8230909ed0e13056e9568d9424e44f7ed734a7971f5d74e43920-b89bca6b_unreported_unreported_09fec4_unreported_unreported.fasta)
- [Full-precision candidate predictions](reference_comparison/sha256-cb96b82f6750c405245ef8aa661c4aa4a8a4250b341909dec8cc535e63cd27c2-ad5cb62c_unreported_unreported_09fec4_unreported_unreported.csv)

## Execution records

- [Actual workflow](WORKFLOW.md)
- [Sequence identities](sequences/identities.json)
- [Reference property comparison](reference_comparison/README.md)
- [Step outputs](steps)

## Usage and time

| Measurement | Value |
|---|---:|
| Uncached input + output | 911,289 |
| Cache-read tokens | 54,630,400 |
| Reported cumulative total, lower bound | 55,541,689 |
| Recorded activity span, hours | 20.07 |

Recorded native activity includes pauses and follow-ups. Token totals include repeated cached context; these are not compute hours or cost estimates. Snapshot: 16 November 2026.

## Execution identity

Run: `20261107_144016_09fec4`. [Execution record](../../../runs/task_006_zhang_hydrolases/run_002_20261107_144016_09fec4/run.json) · [Provenance](provenance.json).
