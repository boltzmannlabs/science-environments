# RML Stability Optimization - Decision Log

## Stage 1: Parent Preparation
- **Decision**: Use supplied parent sequence (269 aa) as RML_PARENT
- **Rationale**: Sequence verified from inputs/parent.fasta, matches expected mature RML construct
- **Evidence**: Parent SHA256: 6d120cb07f40cd383b33ce70bedb8b9adfdaa4346dacadfbaae42dc55073b684

## Stage 2: Parent Baseline
- **Decision**: Use Enzymes tool (tmPred_enzymes) for stability endpoint
- **Rationale**: TemBERTure model provides predicted Tm in degC, suitable for computational screening
- **Result**: Parent Tm = 46.98°C (replica std: 1.90°C)
- **Evidence**: retained-private-evidence/6b00b5660d6c3e1e11b8a4c6_pred.csv

## Stage 3: Sequence Generation
- **Decision**: Use Random_Controlled_Mutagenesis with 20 samples, 8 mutations/epoch
- **Rationale**: Available Boltzmann tool for sequence generation with protected position constraints
- **Result**: 20 unique sequences generated, but all task-ineligible
- **Issue**: Tool generated sequences with incorrect length (258-273 aa) and excessive mutations (161-196)
- **Evidence**: retained-private-evidence/6b00ae770d6c3e1e11b8a417.csv
- **Specialist review**: enzyme-recovery called (timed out at 300s)

## Stage 4: Property Screening
- **Decision**: Screen parent + 2 correct-length candidates with Enzymes tool
- **Rationale**: Only 2 of 20 sequences matched parent length (269 aa)
- **Result**: Both candidates showed Tm improvement (+4.73°C, +3.96°C) but exceeded mutation budget
- **Evidence**: retained-private-evidence/6b00b5660d6c3e1e11b8a4c6_pred.csv

## Stage 5-8: Structure, Optimization, Re-evaluation, Selection

- **Reason**: Generation tool failure prevents valid candidate assessment
- **Required**: New generation approach before these stages can proceed

## Recovery Assessment
- **Problem**: Random_Controlled_Mutagenesis does not appear to support constrained point mutations
- **Options**:
  1. Investigate alternative Boltzmann tools for point mutation generation
  2. Review if Random_Controlled_Mutagenesis has a different mode
  3. Use a targeted mutation approach with specific position selection
- **Recommendation**: New generation round required before workflow can complete
