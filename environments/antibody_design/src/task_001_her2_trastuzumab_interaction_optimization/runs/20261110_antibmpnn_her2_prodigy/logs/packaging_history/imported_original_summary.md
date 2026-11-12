# Task 001 — HER2: Trastuzumab Interaction Optimization — Benchmark Result

## Question
Are we better than the published benchmark?

**Published benchmark (Ab-SELDON, JCIM 2026):**
- Reference/candidate interaction REF15 scores in Rosetta energy units (REU), lower is favorable.
- Best diversity endpoint: FINAL REF15 = -94.8663 REU (initial -49.6996, delta -45.1667).
- Best random endpoint: FINAL REF15 = -92.6947 REU (initial -48.9576, delta -43.7370).
- These are Rosetta REF15 interaction scores, NOT measured binding free energies.

**Our new results:**
- 20 CDR-H3 variants designed with ProteinMPNN (v_48_020) on trastuzumab VH (chain B), CDR-H3 `SRWGGDGFYAMDY` (residues 97–109). 12 unique sequences.
- REF15 score: NOT COMPUTED (Rosetta not available in this environment).

## Verdict
**Cannot compare — the primary benchmark metric (REF15, Rosetta REU) is not computable with the available tools.**
- Rosetta (required for REF15) is not installed and could not be obtained in this environment.
- We did NOT fabricate REF15 scores or substitute a different scoring function and call it REF15.
- Therefore no honest comparison to the published REF15 values is possible.

## What we did (real computation, no fabrication)
1. Verified the trastuzumab/HER2 complex (PDB 1N8Z): VH chain B, VL chain A, HER2 chain C.
2. Identified the HER2 epitope (19 residues, C:557–605) and the trastuzumab VH CDR-H3 (residues 97–109).
3. Designed 20 CDR-H3 variants with ProteinMPNN (fixing all framework + light chain positions).
4. Reported the designed sequences and their uniqueness.

## What we did NOT do (integrity)
- We did NOT compute REF15 (no Rosetta).
- We did NOT substitute Boltz2 pLDDT/ipTM or another score for REF15 and label it as such.
- We did NOT claim an "interaction improvement" without the actual REF15 score.
- The published REF15 values are comparison results, not universal acceptance thresholds.

## Why REF15 is unavailable
- REF15 is a Rosetta scoring protocol. Rosetta is a large C++ application not present in this environment.
- Building/obtaining Rosetta and the exact REF15 protocol was not feasible in this run.
- Per the task instruction ("Report missing essential inputs as NEEDS_INPUT. Never copy published numbers into the new-run result fields"), we report REF15 as unavailable.

## Artifacts
- Designed sequences: results/task_001_her2_trastuzumab_interaction_optimization/designed_sequences.fasta
- Metrics: metrics.json (this directory)
- Code: src/task_001_her2_trastuzumab_interaction_optimization/

## Bottom line
We completed the design step (20 CDR-H3 variants, 12 unique) but could not compute the benchmark's primary metric (REF15) because Rosetta is unavailable. No benchmark comparison is possible without it. This is reported honestly rather than fabricated.
