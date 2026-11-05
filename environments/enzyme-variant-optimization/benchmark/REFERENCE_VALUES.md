# Published Reference Values for Evaluators

Operator/evaluator material, not design-agent input. These values identify comparison opportunities; they are not pass thresholds and must not be inserted into new run results. Inspect method compatibility before numerical comparison. Preserve the original units and sign definitions.

| Case | Published computational evidence | Experimental context, optional for computational evaluation | Comparison limitation |
| --- | --- | --- | --- |
| Est30 | Table 1 reports M13 binding-energy change −14.98 kcal/mol, folding-energy change +6.24 kcal/mol and catalytic-distance fraction 48.06%, versus parent fraction 11.66%. | Parent catalytic efficiency 0.13 and M13 8.11 mM−1 s−1 at the reported conditions. | Binding, folding and occupancy are different endpoints. A static pose cannot reproduce trajectory occupancy. |
| RML | Parent and combined-variant pNPL docking scores −5.5 and −5.6 kcal/mol; Table 1 reports per-substitution stability predictions from several methods. | Table 2 lists parent half-life 45 min and combined-variant half-life 462 min at 50°C. | The abstract rounds the parent half-life differently. A 0.1 kcal/mol docking difference is not compelling catalytic evidence; do not merge predictors with opposite sign conventions. |
| LEH | Figure 1 caption gives FoldX folding-energy changes −20 and −14 kJ/mol for T85I and T85V. | Combined variants increase apparent melting temperature from about 50°C to 85°C. | The combined designs used experimental screening; favorable single-mutant energy is not a predicted combined melting temperature. |
| BLA | 399 substitutions explored; 14 selected using reported ΔΔG < −0.85 kJ/mol. Per-variant values are in Supplementary Table S2. | Table 1 lists parent melting temperature 91.40°C and K319W 96.71°C. | The cutoff is not an achieved winning score. Supplementary values, reported energy units, construct/position labels and inconsistent assay-condition statements need reconciliation before historical scoring. |
| AtHOL1 | For ethyl iodide, reported electrostatic stabilization is −5.6 kcal/mol for the parent and −7.8 kcal/mol for V140T; projected fields are −35.2 ± 9.6 and −43.4 ± 5.7 MV/cm. | Other substrates have separate experimental activity comparisons; do not transfer their fold improvements to ethyl iodide. | Match the transition-state/electric-field definitions and chemical states. Generic docking cannot reproduce this endpoint. |

Sources:

- Est30: [Zhang et al., Communications Biology, 2023](https://doi.org/10.1038/s42003-023-05523-5), Table 1 and associated methods.
- RML: [Teng et al., Foods, 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC11727178/), Tables 1–2 and section 3.7.
- LEH: [Wijma et al., Protein Engineering Design and Selection, 2014](https://pmc.ncbi.nlm.nih.gov/articles/PMC3893934/), Figure 1 and design/screening methods.
- BLA: [Fan et al., Computational and Structural Biotechnology Journal, 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC10883975/), section 3.2, Table 1 and supplement.
- AtHOL1: [Shao et al., Chem Catal, 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12288847/), section 2e, Figure 8 and supplementary tables; original data [Zenodo](https://doi.org/10.5281/zenodo.11188126).

These cases have different preparation requirements. None is certified as an immediately executable historical reproduction. Use a shared contemporary evaluator when historical software, inputs, licenses or settings cannot be reconstructed, and name that comparison accurately. Do not disclose winners until selections are sealed.
