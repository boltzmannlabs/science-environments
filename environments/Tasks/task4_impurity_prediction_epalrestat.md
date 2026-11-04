# Task 4 — Impurity Prediction vs. Literature: Scale-Dependent Impurity Escalation in Epalrestat Synthesis

**Environment:** `task4_impurity_epalrestat`
**Tool under test:** Impurity prediction
**Benchmark class:** Process-impurity structure/mechanism prediction vs. a published process-chemistry case study

---

## 1. Paper Under Comparison

| Field | Value |
|---|---|
| Title | Overcoming Scale-Dependent Impurity Escalation in Epalrestat Synthesis: Identification, Mechanistic Elucidation, and Robust Process Control |
| Authors | Y. Feng et al. (confirm full list from paper) |
| Journal | *Organic Process Research & Development* **2025**, *29*(7), p. 1749 ff. — published **2025-07-18** |
| DOI | on article page (capture when full text is opened) |
| Links | [ACS OPRD article](https://pubs.acs.org/oprdfk/article/29/7/1749/3760483/Overcoming-Scale-Dependent-Impurity-Escalation-in), [Issue TOC](https://pubs.acs.org/oprdfk/issue/29/7) |

## 2. Why This Paper

- A real industrial case: an unknown impurity tracked at **RRT 0.47 escalated from negligible lab levels to ~2% in 100 kg pilot batches** — exactly the scenario an impurity-prediction tool should anticipate *before* scale-up, not explain after.
- Epalrestat (an aldose reductase inhibitor for diabetic neuropathy) is built on a **rhodanine-N-acetic acid / thiazolidinone motif** — a famously impurity-prone scaffold (Michael-acceptor + acidic methylene + hydrolysable thioamide-imide system). Rich, mechanistically traceable impurity chemistry.
- The paper supplies structure elucidation + formation mechanism + control strategy, i.e., complete ground truth for scoring predicted impurities, pathways, and mitigations.

## 3. Ground Truth from the Paper

> ⚠️ Verified at abstract/indexing level; full text needed for structures. Transcribe into `ground_truth/` before running.

Verified so far:
- **Observed impurity:** unknown at RRT 0.47; grew to ≈ **2% at 100 kg scale** while lab batches were acceptable.
- **Mechanistic finding (indexed summary of this work/issue):** formation involves **base-mediated hydrolysis of the rhodanine-N-acetic acid unit followed by a Michael addition** — i.e., a degradation-recombination (dimeric-type) impurity pathway. Capture the exact proposed structure, sequence, and kinetics from the paper.
- **Control strategy:** the paper's mitigation (parameter changes; capture from full text).

Also build background ground truth (standard epalrestat process knowledge, useful as "known impurities" the tool should also find):
- Final-step formation of epalrestat is a **Knoevenagel-type condensation** of a methyl-substituted cinnamaldehyde with rhodanine-N-acetic acid under basic conditions (confirm exact substrates/conditions from the paper).
- Known impurity families for such scaffolds: (E/Z)-geometric isomers, hydrolysis products, dimer/oligomer Michael adducts, oxidation/desulfurization products.

## 4. Objective of the Task

The agent scientist, using only the **impurity prediction tool** (paper masked), must:

1. **Predict the impurity profile** for the final condensation step under the paper's conditions (input: reactants, base, solvent, temp, workup from `input/process.yaml`): top-10 predicted impurity structures, each with a formation-pathway hypothesis and a relative-abundance rank.
2. **Flag the scale-up risk:** identify which predicted impurity is most likely to escalate on scale-up and *why* (thermal mass, local concentration, mixing, hold time).
3. **Propose control levers** ranked by expected impact (temperature cap, base charge, quench timing, hold-time limits, order of addition).
4. (Stretch) Predict an ICH-relevant classification for the top impurities (ordinary vs. structural-alert/mutagenic-flag worthy).

## 5. Environment Setup

```
sci_paper/
└── env/task4_impurity/
    ├── input/
    │   ├── process.yaml              # step recipe: substrates (SMILES), base, solvent, T, time, workup
    │   └── scale_context.yaml        # lab vs. 100 kg heat/mixing context (for risk-flagging mode)
    ├── ground_truth/
    │   ├── impurities.yaml           # RRT 0.47 structure + any other observed impurities (fill from paper)
    │   ├── mechanism.md              # hydrolysis → Michael-addition pathway as published
    │   └── control.yaml              # published process-control solution
    ├── runs/
    └── scores/
```

Tool interface (adapt):

```
predict_impurities --process input/process.yaml --topk 10 \
                   --scale input/scale_context.yaml \
                   --out runs/impurities_<timestamp>.json
```

## 6. Expected Results & Scoring

| # | Metric | Expected / pass threshold |
|---|---|---|
| 1 | Observed impurity in top-5 predictions | The published RRT 0.47 impurity (hydrolysis → Michael-addition product) appears among the tool's top-5 predicted structures, matched by structure or by mechanistic class |
| 2 | Pathway match | Tool's proposed formation pathway contains both key events: (a) rhodanine-N-acetic acid hydrolysis under base, (b) subsequent Michael addition |
| 3 | Known-family coverage | Top-10 also includes ≥ 2 of: E/Z isomers, simple hydrolysis products, other addition oligomers (sanity coverage) |
| 4 | Scale-risk call | Tool flags the escalating impurity as a scale-up risk (not merely a trace analytical curiosity) |
| 5 | Control overlap | ≥ 1 proposed control lever matches the paper's implemented control (e.g., parameter constraint on the base/temperature axis) |
| 6 | False-positive discipline | ≤ 3 predicted "major" impurities that the paper shows were never observed above threshold at any scale |

**Expected result profile:** mechanistic impurity predictors with Michael-acceptor awareness should find the dimeric/hydrolysis family; the discriminating test is whether they *rank* it as the dominant scale-dependent impurity (matching the ~2% @ 100 kg observation) rather than burying it among generic degradation products.

## 7. Sources

- [ACS OPRD article page](https://pubs.acs.org/oprdfk/article/29/7/1749/3760483/Overcoming-Scale-Dependent-Impurity-Escalation-in)
- [OPRD Vol. 29 Issue 7 TOC](https://pubs.acs.org/oprdfk/issue/29/7)
- Context: [FDA ICH Q3A guidance (impurities in new drug substances)](https://www.fda.gov/media/71727/download)
