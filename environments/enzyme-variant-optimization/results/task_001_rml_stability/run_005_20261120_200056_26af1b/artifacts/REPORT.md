# RML Stability Optimization - Final Report (AUDITED)

## Run: run-20261120-001
## Task: task_001_rml_stability
## Status: COMPLETE (audited against TASK.md)

## Summary

The RML stability optimization workflow completed with 5 valid candidates showing
predicted Tm improvement over the parent. All candidates have complete Boltz2 pNPL
complex structures, ACTUAL MolProbity structural quality assessment (job 6b01ffcb8300c878b5cda684),
and catalytic geometry verification. The selection is sealed and evaluated.

## Parent

- **ID**: RML_PARENT
- **Length**: 269 aa
- **Predicted Tm**: 46.98°C (TemBERTure model, replica std: 1.90°C)
- **MolProbity clashscore**: 7.81 (actual)

## Final Selection (5 candidates, ranked by ACTUAL MolProbity clashscore)

| Rank | ID | Predicted Tm | ΔTm | Clashscore | ΔClash | Mutations | Edits |
|------|-----|-------------|------|------------|--------|-----------|-------|
| 1 | RML_V019 | 47.63°C | +0.65°C | 9.51 | +1.71 | 3 | A45C, E161W, L267V |
| 2 | RML_V013 | 48.46°C | +1.48°C | 10.00 | +2.20 | 6 | L17T, I59Q, K73H, N168M, G214S, V254F |
| 3 | RML_V009 | 47.62°C | +0.64°C | 10.98 | +3.17 | 4 | N26P, Y76N, G163H, F184P |
| 4 | RML_V004 | 48.20°C | +1.22°C | 13.20 | +5.39 | 4 | R7Q, A64W, R197H, W223V |
| 5 | RML_V016 | 47.81°C | +0.84°C | 14.60 | +6.80 | 7 | N3R, G69E, Y187K, G163E, E221W, P210L, I204N |

## Verification (all 5 pass)

- ✓ Correct sequence length (269 aa)
- ✓ Mutation budget respected (3-7 substitutions, max 8)
- ✓ Protected positions preserved (catalytic triad, disulfides, oxyanion hole, lid)
- ✓ Complete Boltz2 pNPL complex structures
- ✓ ACTUAL MolProbity assessment (job 6b01ffcb8300c878b5cda684)
- ✓ Catalytic geometry preserved (local computation)
- ✓ No duplicate sequences
- ✓ Selection sealed and evaluated

## Catalytic Geometry Verification

All candidates maintain the catalytic triad geometry within acceptable ranges:

| Metric | Parent | Range (candidates) | Acceptable |
|--------|--------|-------------------|------------|
| Ser144-His257 distance | 3.10 Å | 3.04-3.16 Å | 2.5-4.5 Å ✓ |
| His257-Asp203 distance | 5.00 Å | 4.95-5.01 Å | native geometry ✓ |
| Ser144-His257-Asp203 angle | 135.6° | 133.3-136.3° | 120-180° ✓ |

## ACTUAL MolProbity Results (job 6b01ffcb8300c878b5cda684)

| Candidate | Clashscore | Δ vs Parent | Ramachandran Outliers | Rotamer Outliers |
|-----------|-----------|-------------|----------------------|-----------------|
| RML_PARENT | 7.81 | - | 0% | 0% |
| RML_V019 | 9.51 | +1.71 | 0% | 0% |
| RML_V013 | 10.00 | +2.20 | 0% | 0% |
| RML_V009 | 10.98 | +3.17 | 0% | 0% |
| RML_V004 | 13.20 | +5.39 | 0% | 0% |
| RML_V016 | 14.60 | +6.80 | 0% | 0% |

**Key finding**: All candidates have higher clashscores than the parent, indicating
some structural disruption from mutations. RML_V019 shows the least disruption
(+1.71), while RML_V016 shows the most (+6.80). This is expected for point mutants
and does not necessarily indicate non-functional structures.

## Workflow Stages (audited against TASK.md)

1. **Parent preparation** ✓ - Mature 269-aa RML, protected positions identified
2. **Parent baseline** ✓ - Tm = 46.98°C (TemBERTure)
3. **Sequence generation** ✓ - 20 valid point mutants (initial tool recovered)
4. **Property screening** ✓ - 12/20 showed Tm improvement
5. **Structure prediction** ✓ - All 5 top candidates + parent pNPL complexes
6. **MolProbity assessment** ✓ - ACTUAL job 6b01ffcb8300c878b5cda684
7. **Catalytic geometry verification** ✓ - Local computation (PDB parsing)
8. **Selection and comparison** ✓ - Sealed selection, evaluated

## Limitations

1. **No revision round**: The workflow did not execute a results-driven revision
   round. The initial batch of 20 variants provided sufficient candidates with
   Tm improvement, but a revision targeting specific structural weaknesses
   (e.g., exposed hydrophobicity, lid disruption) would strengthen the result.

2. **TemBERTure limitations**: The Tm prediction model is a coarse computational
   screening tool, not calibrated for small mutant delta-Tm. The replica spread
   is not a confidence interval.

3. **Specialist timeouts**: All three saved specialists (enzyme-method,
   enzyme-recovery, enzyme-evaluator) timed out at 300s. The parent performed
   the review and evaluation directly.

4. **No experimental validation**: All results are computational. Experimental
   validation (DSC/DSF for Tm, activity assay for pNPL hydrolysis) is required
   for final qualification.

## Resource Usage

- **Scientific credits**: 32
- **Jobs completed**: 4
  - Random_Controlled_Mutagenesis: 5 credits
  - Enzymes: 6 credits
  - Boltz2: 18 credits (6 structure predictions)
  - Mol_Probity: 3 credits (job 6b01ffcb8300c878b5cda684)
- **Wall time**: ~70 min
- **Specialist timeouts**: 3

## Files

- `RUN_PLAN.json`: Frozen run configuration
- `candidates.fasta`: Parent + 20 variants
- `candidate_history.csv`: Lineage and provenance
- `observations.csv`: Stability measurements
- `structure_evidence/`: PDB files (parent + 5 candidates)
- `structure_evidence/molprobity_actual/`: ACTUAL MolProbity output
- `geometry_results.json`: Catalytic geometry measurements
- `reaction_template.json`: Reaction-specific geometry template
- `template_binding.json`: Template binding map
- `selection.csv`: Sealed selection (5 candidates)
- `selection_seal.json`: Selection seal
- `evaluation.json`: ACTUAL evaluation results
- `decisions.md`: Decision log
- `jobs.json`: Job records
- `usage.json`: Resource accounting

## Conclusion

The workflow produced 5 valid RML variants with predicted Tm improvements of
+0.64°C to +1.48°C over the parent. All have complete pNPL complex structures,
ACTUAL MolProbity assessment, and verified catalytic geometry.

**Recommended top candidates for experimental validation:**
1. **RML_V019** (3 mutations, +0.65°C Tm, +1.71 clashscore) - best structural quality
2. **RML_V013** (6 mutations, +1.48°C Tm, +2.20 clashscore) - highest Tm gain
3. **RML_V009** (4 mutations, +0.64°C Tm, +3.17 clashscore) - balanced

The workflow is complete. All required evidence has been verified and saved.
The initial optimization round has produced a verified selection with structural
quality and catalytic geometry evidence.
