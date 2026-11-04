# SC-C — Derived Synthetic-Chemistry Research Topics

**Series:** Synthetic chemistry C — new research topics inspired by the SC01–SC12 papers
**Status:** These are independent research problems built on the papers' limitations — *not* claims the original papers solved them.

Each topic below is a standalone benchmark module. It attaches to a host task (where data already exists) and runs the same environment/protocol as the host, so no new ground-truth capture is needed beyond the host's.

---

## SC-C1 — Reaction Substrate Generalization

| Field | Value |
|---|---|
| Objective | Test whether conditions optimized on the paper's model substrates remain effective for **electron-rich, electron-poor, and sterically hindered** substrates outside the training matrix. |
| Expected outcome | An established **substrate-dependent limitation map**: predicted yield floor per substrate class, plus the first substrate class where the condition set breaks. |
| Host tasks | SC01 (Suzuki), SC02 (amidation), SC05 (thiazolopyridinone) |
| Protocol | Take the optimized condition set from the host task; have the tools predict yields on a standardized electron-rich/electron-poor/hindered probe set; validate the failure boundary against any substrate data the host paper reports. |
| Scoring | Correct ordering of substrate-class difficulty; failure boundary identified within one substrate class; no overconfident predictions (>90% predicted yield) on classes the paper shows fail. |

## SC-C2 — Catalyst Loading Reduction

| Field | Value |
|---|---|
| Objective | Identify the **minimum catalyst loading** that maintains acceptable yield (≥ 90% of optimal-performance yield) — including the trade-off curve, not just a single point. |
| Expected outcome | Reduced catalyst cost and **residual metal contamination** risk; a loading–yield curve with a defensible operating point. |
| Host tasks | SC01 (Pd-NHC), SC03 (green Suzuki), SC04 (organocatalyst) |
| Protocol | Predict yield across a loading ladder (e.g., 2.0 → 0.5 → 0.1 → 0.05 mol%); compare the predicted minimum-viable loading against the paper's final loading; for Pd systems, state the expected residual-metal implication at each loading (ICH Q3D context). |
| Scoring | Loading–yield curve shape correct (monotone or plateau); predicted minimum-viable loading within 2× of paper's demonstrated loading if data exists; metal-residual reasoning present. |

## SC-C3 — Solvent Replacement

| Field | Value |
|---|---|
| Objective | Replace **hazardous solvents** (Class 1/2: benzene, DCM, DMF, NMP, dioxane…) with safer alternatives **without sacrificing performance**. |
| Expected outcome | Improved process safety and environmental profile; a green-alternative condition set within −5 pp yield of the conventional optimum; E-factor direction quantified. |
| Host tasks | SC03 (DES Suzuki — primary), plus any SC01/SC02 optimum that uses a Class 2 solvent |
| Protocol | Constrain the condition tool to a green-solvent whitelist (2-MeTHF, CPME, EtOAc, ethanol/water, CPME, DES systems…); predict yield loss vs. unconstrained optimum; flag solubility/compatibility hazards of the swap. |
| Scoring | No Class 1–2 solvent in final recommendation; yield within −5 pp; swap risks (solubility, azeotrope, impurity shift) stated. |

## SC-C4 — Impurity Suppression

| Field | Value |
|---|---|
| Objective | Identify the **reaction parameters responsible for major side products** and suppress them **without sacrificing yield**. |
| Expected outcome | Impurity level reduced (predicted and, where paper data exists, confirmed); parameter-to-impurity causal map; control strategy per impurity. |
| Host tasks | SC02 (amidation side products), SC04 (competing pathways), SC09 (flow impurity control), SC07 (API impurities) |
| Protocol | Use impurity-prediction tool over the host's condition matrix: which condition moves each impurity; identify the dominant impurity's mechanistic driver (temperature, stoichiometry, exposure time, concentration); propose the suppression set and predicted yield impact. |
| Scoring | Dominant impurity correctly identified; suppression lever matches paper's (if reported); predicted yield retention ≥ 90% after suppression. |

## SC-C5 — Reaction Time Optimization

| Field | Value |
|---|---|
| Objective | Investigate the **time–temperature–conversion–selectivity** surface: find the shortest cycle maintaining conversion and selectivity (including ramp/hold structure). |
| Expected outcome | Shorter reaction cycles and improved productivity; a time–temperature equivalence statement (Arrhenius-style reasoning) with an operating recommendation. |
| Host tasks | SC02 (µw time), SC06 (residence time), SC08 (DoE time axis), SC09 (flow time) |
| Protocol | Predict conversion/selectivity across time × temperature grid; locate the knee of the conversion curve; check selectivity decay at over-hold conditions; recommend cycle time with margin. |
| Scoring | Knee location within ± 25% of paper's optimal time (if data); over-hold degradation direction correct; productivity (cycles/shift) improvement quantified. |

---

## Cross-topic reporting

Run these modules on their hosts **after** the host task completes, reusing the host's ground truth. Report each topic as: host task ID × topic ID × pass/fail per scoring line — a matrix showing which capability (generalization, economy, greenness, purity, speed) our tools can trade against yield and which they cannot.
