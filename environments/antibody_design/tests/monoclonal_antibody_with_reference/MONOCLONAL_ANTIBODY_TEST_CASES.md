# Monoclonal-Antibody Test Plan: DENV-2 EDIII with DV87.1 Reference

The DENV prompt variants referenced by these regression checks are retired fixtures under `tests/fixtures/retired_tasks/`. The active monoclonal tasks are the five documents in `tasks/monoclonal_antibody_design/`; this suite does not establish their scientific performance.

**Scope:** reference-guided paired-chain monoclonal antibodies only. The DENV case matrix below is a profile-level scientific test plan, not a count of implemented automated tests. Reusable contract regressions are in `tests/monoclonal_antibody_with_reference/test_reference_guided.py`; [coverage and gaps](COVERAGE.md) distinguishes software checks from unimplemented scientific verification.


## Purpose

This test plan defines how the benchmark tasks test monoclonal-antibody candidates in the
standard **reference-guided** scenario: a reference antibody (DV87.1) and a target antigen
(DENV-2 envelope protein, Domain III / EDIII) are supplied, and candidate heavy/light-chain
pairs derived from the reference must be assessed against the general monoclonal-antibody
testing program before any candidate may enter the shortlist.

The plan applies to both presentations of task `denv_antibody_001`:

- `tests/fixtures/retired_tasks/denv_antibody_001.md`: the method-neutral task.
- `tests/fixtures/retired_tasks/denv_antibody_001_tools.md`: the same task with expanded evidence requirements in its capability block.

Both variants must receive the same antigen, reference antibody, candidate limit, scientific
rules, evaluator, budget, random seed, and hidden outcomes. They must produce the same result
schema and be judged by the same scientific gates. The capability block is the only permitted
task-content difference; naming a service never relaxes a testing criterion.

The local executable tests validate the specification, the declared identities, the general
testing criteria, artifact integrity, rule decisions, and output consistency. They do not
predict structures, calculate binding, generate antibody sequences, or prove biological
activity.

## 1. Fixed biological test identity

Before a scientific test can start, the evaluator must supply and independently verify all of
the following. This is the same input-resolution gate that any antibody project applies when a
reference antibody and a target antigen arrive in the lab:

| Input | Required evidence |
| --- | --- |
| Antigen identity | DENV-2 strain/accession, exact envelope EDIII construct sequence, construct boundaries, presentation context, and source. |
| Antigen structure | Coordinate file, antigen chain IDs, coordinate-to-sequence residue map, unresolved/missing residues, and structure provenance. |
| Binding region | Reviewed EDIII residue annotation mapped to the supplied construct and coordinates. Residue numbers must not be inferred from a different strain or construct. |
| Reference antibody | DV87.1 complete paired heavy/light sequences, declared format, chain IDs, sequence source, and paired-sequence digest. |
| Antibody annotation | Numbering scheme, framework and CDR boundaries, insertions, allowed edit mask, protected residues, and sequence-to-structure mapping. |
| Reference evidence | Reference structure/complex evidence when available, binding evidence, assay conditions, and developability evidence, each with provenance. |
| Frozen protocol | Required metrics, units, scales, target/antibody scope, thresholds, uncertainty, method revisions, ranking, tie-break, and missing-evidence behavior. |
| Execution limits | Maximum evaluated candidates, requested final count, random seed, wall time, CPU/GPU limits, remote-service budget, and knowledge cutoff. |

If any required identity is absent or contradictory, the expected status is `NEEDS_INPUT`. If
inputs exist but a complete qualified evaluator or compatible method lock is missing, the
expected status is `PROTOCOL_REQUIRED`.

## 2. The general monoclonal-antibody testing program

When a reference antibody and a target antigen are given, standard antibody research
(regulatory practice per ICH Q6B and WHO mAb quality-control guidance, plus the discovery-stage
developability literature) characterizes every candidate across the following testing
categories. The benchmark encodes the same categories as frozen computational gates; the
qualified protocol supplies all scientific thresholds. Historical shortlist values are not
thresholds, and no criterion may be skipped because another criterion looks favorable.

### 2.1 Identity and lineage

- Every candidate is a complete, correctly paired heavy + light chain with a unique candidate
  ID, legal 20-letter amino-acid sequences, and a unique paired-sequence digest.
- Every candidate must declare the reference antibody (DV87.1) as its direct parent, so the
  molecular entity is traceable across all stages.
- Rejected: one chain missing, chain pairing swapped, duplicate IDs, duplicate paired
  sequences, and candidates whose paired sequence is identical to the reference (reference
  leakage).
- Any change to either chain invalidates all prior measurements for that candidate; evidence is
  bound to the paired-sequence digest.

### 2.2 Physicochemical characterization

General mAb characterization (ICH Q6B / WHO) determines class/subclass, light-chain type,
primary structure, disulfide integrity, N-/C-terminal variability, pI, and glycosylation. In
this computational benchmark the corresponding contract checks are:

- The candidate record agrees with the declared construct format and chain assignment.
- The declared paired-sequence digest matches the actual heavy/light sequences.
- pI and glycosylation-related sequence features are recorded where the qualified protocol
  includes them; a consensus N-glycosylation sequon (N-X-S/T) in a variable domain is a
  developability liability, not an acceptable feature.
- Heterogeneity sources introduced by editing (new motifs, new termini) are reported as
  developability inputs, not silently accepted.

### 2.3 Framework preservation and permitted edits

- The reference framework must be preserved under the frozen numbering scheme (IMGT for this
  task); only the annotated CDRs (or a prequalified position mask) may vary.
- Sequence lengths follow the reference annotation; protected residues must not change.
- A candidate whose framework edits exceed the frozen mask fails the identity/framework gate
  regardless of its predicted binding.

### 2.4 Structural confidence (fold and interface, kept separate)

- Whole-antibody and per-chain fold confidence is reported separately from local
  (residue/loop) uncertainty, especially HCDR3.
- Coordinate integrity is checked: chain completeness, heavy/light orientation, variable-domain
  geometry, disulfides, clashes, and missing regions.
- **Fold confidence and interface confidence are distinct evidence types.** A high
  single-antibody fold score cannot satisfy a target-interface rule, and antigen–antibody
  interface evidence must not be replaced by heavy/light-chain (VH–VL) interface evidence.
- Missing structural values are reported as `null` with `UNRESOLVED` status and a reason.

### 2.5 Target binding: the non-interchangeable endpoint hierarchy

A proper binding characterization distinguishes separate, non-interchangeable endpoints. This
hierarchy is the core of the binding test; no endpoint may be used to fill, convert, or imply
another:

| Order | Endpoint | General meaning | Role in this benchmark |
| --- | --- | --- | --- |
| 1 | Predicted interaction energetics | Computed antibody–antigen interaction-energy estimate | Computational only; requires units, chain selection, conditions, and native output |
| 2 | Predicted interface confidence | Confidence that the modeled complex is correct | Computational only; must have antigen–antibody scope |
| 3 | Equilibrium affinity (Kd) | Binding strength under defined assay conditions | Only from a measured record with assay provenance (SPR/BLI/ITC class) |
| 4 | Binding kinetics (kon/koff) | Association and dissociation rates | Only from a measured record; kept separate from Kd |
| 5 | Binding EC50 (ELISA) | Assay-specific binding potency | Assay-specific; never interchangeable with Kd or functional potency |
| 6 | Neutralization potency (e.g., PRNT/FRNT IC50) | Viral-neutralizing activity in a defined assay | Measured only; DENV-specific functional endpoint |
| 7 | ADE risk (antibody-dependent enhancement) | Fc-mediated enhancement of infection at subneutralizing concentrations | Measured only; a DENV safety endpoint that must never be inferred from binding or interface scores |

Test rules:

- Each measured endpoint requires units, score direction, assay/model conditions, chain
  selection, applicability, uncertainty, and native evidence.
- Predicted values may never be converted into measured affinity, ELISA EC50, neutralization,
  or ADE claims.
- For DENV/EDIII candidates, neutralization and antibody-dependent enhancement are mandatory
  distinct safety/efficacy endpoints when experimental records exist; a binding pass alone
  establishes no protection and no ADE safety.

### 2.6 Specificity, cross-reactivity, and polyreactivity

- Specificity is assessed against a declared target panel (e.g., homologous dengue proteins or
  other DENV serotypes when the protocol defines them); cross-reactivity ratios require every
  panel member, construct, and normalization rule to be recorded.
- Polyreactivity/poly specificity (unwanted binding to unrelated proteins or surfaces) is a
  separate required group; computational predictors are risk indicators only and do not
  establish experimental specificity.
- CDR charge descriptors (positive/negative CDR charge, heavy/light charge asymmetry) feed the
  polyreactivity and self-association risk assessment.

### 2.7 Developability panel

The developability program is tested as separate required groups, mirroring the standard
early-discovery screen. All computational outputs are risk indicators, never measured facts.

| Group | What is generally tested | Typical early (sequence/structure) indicators | Typical later (measured) confirmations |
| --- | --- | --- | --- |
| Stability | Conformational and chemical stability | Per-mutation stability (DDG) scores with declared reference state and sign convention; local structural uncertainty | Thermal melting (Tm/Tm-onset), forced degradation |
| Chemical liabilities | Degradation motifs that create heterogeneity | Motif scan: Asn deamidation (NG, N-S/T), Asp isomerization (DG, D-S/T), Met/Trp oxidation sites, variable-domain N-glycosylation sequons (N-X-S/T), unpaired cysteines, Asp-Pro cleavage sites | Forced degradation plus peptide mapping |
| Aggregation | Self-interaction and colloidal stability | Aggregation-prone scores, exposed hydrophobic patches, structural self-interaction indicators | DLS/size exclusion, viscosity at high concentration |
| Solubility | Low-solubility risk at process/storage conditions | Solubility predictions, CDR hydrophobicity | Precipitation-based solubility assays |
| Expression | Expression-related liabilities | Expression-risk predictions, CDR charge and length descriptors, pI | Host-cell expression titer |
| Polyreactivity | Non-specific binding risk | Polyspecificity predictors, CDR charge/asymmetry descriptors | Binding panels against irrelevant surfaces |
| Immunogenicity | Anti-drug antibody risk | Predicted T-cell epitopes, nonhuman residues, introduced glycosylation | In vitro T-cell/HLA assays |

Additional rules:

- Liability severity depends on position: a solvent-exposed CDR liability is a hard risk; the
  same motif buried in framework is flagged for formulation mitigation. The frozen protocol
  decides the gate outcome; the benchmark never applies ad hoc severities.
- A binding pass cannot compensate for a failed or unresolved mandatory developability group
  (no cross-rule compensation).
- pI, CDR total length, CDR hydrophobicity, CDR charge, and heavy/light charge asymmetry are
  guideline descriptors: the qualified protocol supplies the scientifically justified ranges.

### 2.8 Immunogenicity and safety indicators

- Immunogenicity indicators (predicted immunogenic sequences, nonhuman residues, introduced
  glycosylation) are reported as a distinct group, separate from polyreactivity.
- For this DENV-2 EDIII task, ADE risk is a safety endpoint with its own evidence requirement;
  no computational binding score may be reported as ADE safety.
- Predicted immunogenicity does not establish clinical immunogenicity or safety.

### 2.9 Dynamics (conditional)

- Run only when `execution.dynamics_required` is true.
- Record the starting complex, force-field/protocol identity, chain and atom selections,
  equilibration, sampling duration, replicates, alignment, and contact definition.
- Report numerical RMSD, RMSF, and interface-contact persistence with uncertainty and
  convergence limitations.
- Do not interpret one stable-looking trajectory as proof of affinity or biological function.

### 2.10 Qualification, ranking, and output integrity

- `PASS`, `FAIL`, and `UNRESOLVED` are recomputed from frozen predicates against current
  evidence; submitted labels are never trusted.
- Qualification requires **every** mandatory rule to pass. Missing values are `null` and
  `UNRESOLVED` with a reason; `UNRESOLVED` cannot qualify, and `FAIL` cannot qualify.
- Rank only eligible unique candidate pairs using the frozen ordered rules and candidate-ID
  tie-break; truncate deterministically to the requested final count; never pad with failed or
  unresolved candidates.
- Output bundle in `08_results/`: `designed_sequences.fasta` (headers `>candidate_id|H` and
  `>candidate_id|L`), `metrics.json`, `shortlist.csv` (`rank,candidate_id,sequence_sha256`),
  `report.md`; all hashes, provenance, and resource use must agree.
- The reference (DV87.1) belongs in `metrics.json` as the baseline record and must never
  appear in the FASTA, the shortlist, or the CSV.
- Status semantics: `QUALIFIED` (requested count met), `PARTIAL` (fewer eligible than
  requested), `NO_QUALIFYING_DESIGNS` (every evaluated candidate has a verified required
  failure — a completed negative), `INCOMPLETE` (required work unresolved — not a completed
  negative), and preflight statuses `NEEDS_INPUT` / `PROTOCOL_REQUIRED`.

## 3. Test levels

| Level | What it tests |
| --- | --- |
| Specification | Both task files exist and declare the shared identity; only the capability block differs; schemas are valid; the test plan covers the criteria above. |
| Input and preflight | Every artifact path is relative to the declared input root with matching SHA-256; missing antigen or reference inputs fail closed; identical/overlapping chain IDs and reversed construct ranges are rejected; cutoff and method-lock eligibility are enforced for both variants. |
| Reference baseline | Exactly one reference record with ID `DV87.1`, role `reference`, no parent; its paired digest is recomputed; the same metric definitions apply to reference and candidates; the reference is excluded from all shortlist outputs. |
| Candidate identity and lineage | Complete pairs, legal sequences, unique IDs and digests, DV87.1 parentage, framework preservation, reference-leakage rejection, stale-evidence invalidation. |
| Structure | Coordinate integrity, fold confidence separate from interface confidence, VH–VL-only evidence rejected for target binding. |
| Binding endpoints | Endpoint hierarchy enforced; units/conditions/native evidence per measurement; no conversion of predictions into measured endpoints; DENV neutralization and ADE kept as distinct experimental endpoints. |
| Specificity | Panel-based cross-reactivity definitions; polyreactivity as its own group. |
| Developability | All required groups tested separately; sequence-liability motifs (deamidation, isomerization, oxidation, glycosylation, unpaired cysteine) gate the developability rule; no compensation across groups. |
| Dynamics | Conditional execution; full protocol recording; no over-interpretation. |
| Qualification and output | Frozen rule recomputation, eligibility, deterministic ranking, status semantics, FASTA/CSV/metrics/report agreement, budget enforcement. |

## 4. Executable test-case matrix

| ID | Test case | Expected result |
| --- | --- | --- |
| MAB-001 | Both task files after allowed normalization (variant line and capability block only) | Identical scientific content and output contract. |
| MAB-002 | Named computational service appears in either task prompt | Test fails. |
| MAB-003 | Legacy `StabDDG` or `Boltz2` name appears in the registered method inventory | Test fails. |
| MAB-004 | Named-method protocol declares Stability-Binding DDG, PRODIGY, and ipSAE with their declared evidence roles | `CONTRACT_READY` when all other inputs pass. |
| MAB-005 | General request uses an independently qualified complete protocol | `CONTRACT_READY` when all other inputs pass. |
| MAB-006 | Missing antigen construct, sequence, structure, chain IDs, residue map, or strain | `NEEDS_INPUT`. |
| MAB-007 | Missing DV87.1 paired sequences, format, chain IDs, numbering scheme, or region annotation | `NEEDS_INPUT`. |
| MAB-008 | Heavy and light chain IDs are identical | Request rejected. |
| MAB-009 | Antigen chain ID overlaps an antibody chain ID | Request rejected. |
| MAB-010 | Protocol omits any mandatory evidence group (identity, framework, fold, interface, binding, developability, stability, aggregation, solubility, expression, polyreactivity, immunogenicity) | `PROTOCOL_REQUIRED`. |
| MAB-011 | A method or protocol release is newer than the knowledge cutoff | `PROTOCOL_REQUIRED`. |
| MAB-012 | Method revision is not immutable or the adapter is unverified | `PROTOCOL_REQUIRED`. |
| MAB-013 | An interface or binding rule uses antibody-only scope | Protocol rejected. |
| MAB-014 | Candidate has only one chain | Candidate/output rejected. |
| MAB-015 | Duplicate candidate ID or duplicate paired sequence | Candidate/output rejected. |
| MAB-016 | Candidate declares a parent other than DV87.1 | Candidate/output rejected. |
| MAB-017 | Candidate paired sequence is identical to the reference (reference leakage) | Candidate rejected. |
| MAB-018 | A chain sequence changes but the old evidence digest remains | Bundle rejected as stale evidence. |
| MAB-019 | Resolved metric has no native artifact | Bundle rejected. |
| MAB-020 | Evidence file hash changes after scoring | Bundle rejected. |
| MAB-021 | Required value is missing but the rule is labeled `PASS` | Bundle rejected. |
| MAB-022 | Binding rules pass but a mandatory developability group fails | Candidate excluded; no cross-rule compensation. |
| MAB-023 | Only antibody fold confidence exists; no target-interface evidence | Interface rule stays `UNRESOLVED`; candidate cannot qualify. |
| MAB-024 | Interface confidence covers only VH–VL instead of antigen–antibody | Evidence rejected for target binding. |
| MAB-025 | Predicted interaction energy is reported as, or converted into, measured Kd or ELISA EC50 | Claim rejected (endpoint conflation). |
| MAB-026 | Neutralization potency or ADE risk is inferred from binding or interface predictions | Claim rejected; DENV functional endpoints require actual assay evidence. |
| MAB-027 | Variable-domain N-X-S/T glycosylation sequon, or deamidation (NG/N-S/T) / isomerization (DG/D-S/T) liability in the editable region | Developability gate fails per the frozen protocol. |
| MAB-028 | CDR hydrophobicity/charge, heavy/light charge asymmetry, or pI outside the frozen guideline range | Developability risk gate fails per the frozen protocol. |
| MAB-029 | Fewer candidates pass than requested | `PARTIAL` with the exact returned count. |
| MAB-030 | Every evaluated candidate has a verified required failure | `NO_QUALIFYING_DESIGNS` (completed negative). |
| MAB-031 | No candidate passes because required work is unresolved | `INCOMPLETE`, not a completed negative. |
| MAB-032 | Eligible candidates exceed the final count | Deterministic ranking truncates to the requested count. |
| MAB-033 | FASTA omits a chain, has a malformed header, or disagrees with metrics/CSV | Bundle rejected. |
| MAB-034 | Resource use exceeds a frozen budget | Bundle rejected. |
| MAB-035 | Synthetic unit fixture submitted as scientific evidence | Bundle rejected unless test-only validation is explicitly enabled. |
| MAB-036 | Reference DV87.1 appears in the shortlist, FASTA, or CSV | Bundle rejected. |
| MAB-037 | The same missing input or cutoff violation is exercised on both variants | Identical failure status (variant parity). |

## 5. Scientific benchmark scenarios

After exact biological inputs and a qualified evaluator exist, run both task variants
independently with matched seeds and budgets over the same hidden evaluation set. Include at
least:

1. A reference-only control proving DV87.1 identity and evaluator operation (reference never
   enters any shortlist output).
2. An unchanged-reference candidate that must be detected as duplicate/reference leakage.
3. A permitted single-CDR mutation with current evidence for both chains.
4. A forbidden framework mutation that must fail the identity/framework gate.
5. A chain-swapped or mismatched VH/VL candidate that must fail pairing.
6. A structurally plausible candidate (good fold confidence) with weak or unresolved
   antigen–antibody interface — fold confidence must not satisfy the interface rule.
7. A predicted binder carrying a mandatory developability liability (e.g., an exposed CDR
   deamidation or glycosylation motif) that must fail the developability gate.
8. A candidate with complete passes across every frozen computational gate.
9. A candidate whose score changes after rescoring, proving stale evidence is rejected.
10. An empty eligible set with verified failures, proving completed-negative handling.
11. A candidate with measured endpoint records (Kd, ELISA EC50, neutralization IC50, ADE
    result), verifying that measured endpoints stay separate from predicted ones and that ADE
    is reported only from assay evidence.

Compare the two task variants on valid completion, candidate uniqueness, rule coverage, status
accuracy, runtime, resource use, and the eligible sequence set. Do not require identical
generated sequences unless the generation path, versions, seed handling, and determinism
contract make that expectation valid. Scientific comparison must use the same independent
evaluator and must report uncertainty rather than choosing the better prompt from one run.

## 6. Evidence boundary

Passing these tests means the benchmark package is internally consistent and the declared
artifacts satisfy the frozen contract: the identity, lineage, physicochemical, structural,
binding-endpoint, specificity, developability, immunogenicity, and qualification criteria are
enforced exactly as specified. It does not mean a designed antibody binds DENV-2 EDIII,
preserves the intended epitope in virion context, neutralizes dengue virus, avoids
antibody-dependent enhancement, expresses successfully, or is safe. Those claims require
appropriate experimental evidence.
