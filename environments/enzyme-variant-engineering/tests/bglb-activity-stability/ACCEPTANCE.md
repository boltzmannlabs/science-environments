# BglB scientific acceptance and evaluation

Applies to [TASK.md](../../tasks/bglb-activity-stability/TASK.md), identically for
base-agent and specialist-assisted outputs. A recovery continuation is reported
separately from an independent matched comparison.

## Checks and expected behavior

| Check | Evidence / expected behavior |
| --- | --- |
| Parent and numbering | Use the supplied 445-residue study-numbered modelling core. Do not apply its mutations directly to full UniProt or tagged coordinates. |
| Design constraints | Each selected sequence has one actual substitution, an agreeing mutation label, no protected-site edit and no duplicate identity/sequence. |
| Shortlist | Unique, contiguous ranks; at most five nonparent candidates. A header-only file is an honest empty outcome, not success. |
| Catalytic efficiency | Primary measured endpoint is kcat/KM in M^-1 min^-1; reference point value 174,000. A higher comparable value is descriptively improved. |
| Functional stability | Reference point value 39.93 degrees C in this activity-after-heat assay. A generic unfolding Tm or delta-delta-G cannot fill this field. |
| Joint objective | Published matching variant expresses, has kcat/KM greater than reference and functional Tm at least reference. This point-estimate rule is project policy, not a significance test. |
| Structure/chemistry | If claimed, evidence must match the selected sequence, structural state and substrate; missing geometry ranges are descriptive, not invented pass criteria. |
| Units | kcat: min^-1 to s^-1 divides by 60; KM: mM to M multiplies by 0.001; efficiency: M^-1 min^-1 to M^-1 s^-1 divides by 60. Keep units visible. |
| Source measurements | Join by the exact single mutation in study numbering, not rank, filenames or nearest sequence. Do not transfer a single-mutant measurement to a combined mutant. |
| Missing/censored values | NA/blank is unknown, not zero. Very low activity at/below the paper's 10 M^-1 min^-1 detection limit is flagged, not treated as an exact calibrated point. |
| Novel designs | No source-table match means unmeasured, not failed activity or successful measured improvement. |
| Sources and method | Report public-data access, literature rediscovery and possible training overlap. This task is not blinded. |
| Failure recovery | A specialist recommendation cites the actual failure/evidence and a targeted alternative. No threshold changes or fabricated winning result. |
| Resource use | Retain actual native session/job references; state unknown costs. Include specialist calls and any inherited work in continuation totals. |

## Evaluate saved outputs

From the environment directory, after an actual base run has produced the file:

```bash
python3 tests/bglb-activity-stability/evaluate.py \
  --selection results/bglb-activity-stability/agent-alone/candidates.csv \
  --output results/bglb-activity-stability/agent-alone/evaluation.json
```

Use the corresponding assisted paths for its output. Output creation is exclusive:
choose a fresh result path rather than overwrite earlier evaluation evidence.
The default reference is the attributed, checksum-verified published S1 Table.

The evaluator checks the shortlist's scientific constraints and attaches known
published values. It reports measured/unmeasured coverage, point-rule outcomes,
and parent-relative ratios with explicit denominators. It never reranks a sealed
selection or calls a predictor. An unknown result cannot be counted as a success.
Reference values come from the source's `BglB` row, not invented model scores.

Manual scientific review still checks `report.md`, `evidence.json`, `usage.json`,
native artifacts and method suitability. The small CSV evaluator does not verify
that tools actually ran, validate chemistry, establish statistical significance,
prove independence of public data or assess assay equivalence for a new construct.

## Software regression scenarios

Tests cover valid and empty shortlists; wrong sequence/mutation pairs; numbering
and protected-site edits; parent/combined/duplicate designs; noncontiguous ranks;
invalid sequences; changed reference files; source joins; missing measurements;
unit conversions; censored activity; unknown variants; and stable-but-inactive
trade-offs. These are labelled checks of evaluation behavior, not molecular results.

## Source limitations

The paper discusses 129 mutants; the retrieved S1 CSV contains 128 mutant rows
and one BglB reference row. Use those actual records and retain the discrepancy.
The paper's point estimates and its error columns do not establish a new assay
comparison or justify selecting only favorable replicates. The evaluator does not
train on this table or claim a new molecular model.
