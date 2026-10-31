# Denovo Enzyme Design — References

Sources support the [environment specification](../../environments/Denovo-Enzyme-Design/ENVIRONMENT_SPEC.md); they do not establish that the proposed environment has been implemented or validated.

- Task organization reference: [BioDesignBench binder_001](https://github.com/RomeroLab/BioDesignBench/blob/main/examples/demo_task/binder_001.md). The task, repository README and LICENSE were read. This package uses original enzyme-task text organized using that example; it does not reproduce the binder task body.
- [BioDesignBench LICENSE](https://github.com/RomeroLab/BioDesignBench/blob/main/LICENSE) contains Apache License 2.0, while the checked README describes code as MIT. That upstream metadata discrepancy remains unresolved. No upstream code or task body is redistributed here.

## Task format and scientific foundations

The agent task retains the reference's Description, Target, Design Constraints, Expected Output, Constraints and Important Instructions sections. Required Execution Steps replaces its software-list section to meet the user's revised requirement. The original binder-specific targets and numerical limits are not used as enzyme criteria.

| Scientific source | Relevance |
| --- | --- |
| [Computational enzyme design by catalytic motif scaffolding](https://doi.org/10.1038/s41586-025-09747-9) | Evidence that catalytic geometry and scaffold design matter to functional de novo enzymes; demonstrated reactions do not establish universal capability |
| [Curated enzyme mechanisms and catalytic-site evidence](https://doi.org/10.1093/nar/gkx1012) | Reaction-specific roles, state definitions and supporting literature for profile preparation |
| [Enzyme specificity prediction using cross-attention graph neural networks](https://doi.org/10.1038/s41586-025-09697-2) | Evidence that substrate compatibility is a distinct prediction problem; it does not substitute for full reaction chemistry |

The required operations, chemistry checks and controller behavior are defined independently of scientific software selection. Numerical acceptance thresholds, prediction applicability and chemical-method adequacy require reaction-specific qualification. The reward coefficients and learning procedure are proposed configuration choices; no training result is claimed.

## Assembly and homodimer evidence

Reviewed 26 October 2026. Labels describe the scientific contribution; they do not prescribe named execution software. Each source supports the stated requirement, not an implemented enzyme-design pipeline.

| Source | Finding and use in this specification |
| --- | --- |
| [RCSB: biological assemblies](https://pdb101.rcsb.org/learn/guide-to-understanding-pdb-data/biological-assemblies) | Distinguish biological assemblies from asymmetric units and reconstruct recorded transformations. |
| [L-DEX YL structure and primary structural study](https://www.rcsb.org/structure/1JUD) | Hisano et al. (1996), doi:10.1074/jbc.271.34.20322: homodimeric reference; the inserted subdomain contributes to its interface. |
| [Thermodynamic inference of biological assemblies](https://doi.org/10.1016/j.jmb.2007.05.022) | Krissinel and Henrick (2007): assembly inference supplies evidence with limitations; a structural contact alone is not proof of a solution assembly. |
| [Symmetric scaffold and motif generation](https://doi.org/10.1038/s41586-023-06415-8) | Watson et al. (2023): experimentally tested symmetric designs support assembly-conditioned generation, without establishing universal enzyme activity. |
| [Coupled protein sequence design](https://doi.org/10.1126/science.add2187) | Dauparas et al. (2022): corresponding positions can be tied across chains; supports one shared homodimer sequence. |
| [Structural asymmetry in homodimers](https://pubmed.ncbi.nlm.nih.gov/22629324/) | A structural survey (2012): identical subunits can exhibit structural asymmetry; sequence equality does not imply identical coordinates. |
| [Experimental evidence of asymmetric catalytic states](https://pmc.ncbi.nlm.nih.gov/articles/PMC2548373/) | Biotin-carboxylase structures support state-dependent asymmetry in a homodimer. This is not evidence that L-DEX YL has the same half-sites mechanism. |
| [Evaluation of complex-confidence metrics](https://doi.org/10.1002/pro.70327) | A 2025 primary benchmark studied heterodimers; its cutoffs must not be assumed to transfer to newly designed enzyme homodimers. |
| [Experimental L-DEX YL mechanism](https://pubmed.ncbi.nlm.nih.gov/7629151/) | Liu et al. (1995): evidence for a covalent intermediate and subsequent hydrolysis supports evaluating the complete catalytic cycle rather than only initial attack geometry. |
| [Authoritative haloacid-dehalogenase reaction definition](https://iubmb.qmul.ac.uk/enzyme/EC3/8/1/2.html) | EC 3.8.1.2 specifies conversion of an (S)-2-haloacid into an (R)-2-hydroxyacid. Supports the example's stereochemical direction; charge/proton bookkeeping still requires molecular validation. |

## Scientific audit: conditions, kinetics and chemistry

| Source | Finding and use in this specification |
| --- | --- |
| [Concentration-dependent monomer–dimer equilibrium](https://doi.org/10.1021/bi961347a) | Gallagher and Huber (1997): an experimental example showing concentration and solution conditions can affect assembly populations. It does not determine the equilibrium of L-DEX YL. |
| [Enzyme activity reporting requirements](https://www.beilstein-institut.de/en/projects/strenda/guidelines/) | Official reporting guidelines require conditions, units and whether activity is relative to a subunit or oligomeric form. Reporting completeness is not validation of a measurement or prediction. |
| [Sampled free-energy pathways in enzyme reactions](https://doi.org/10.1021/ct600240y) | Hu, Lu and Yang (2007): energy-path optimization and free-energy estimation are distinct; environment sampling and convergence affect the latter. Supports route-specific validation rather than labeling a static barrier as free energy. |

## Execution diagnostics

Additional structural-validation sources checked 29 October 2026:

- [MolProbity validation guide](https://molprobity.lbl.gov/help/): non-Pro cis peptides are rare and require strong supporting evidence; they are not categorically impossible. This informs the declared limitation of the development preparation adapter.
- [MolProbity: more and better reference data for improved all-atom structure validation](https://pmc.ncbi.nlm.nih.gov/articles/PMC5734394/): geometric validation covers complementary checks; one valid torsion, a low RMSD or a successful minimization cannot establish overall structural correctness.

Inspected on 27 October 2026; claims apply to the pinned source and retained local attempts.

| Source | Use |
| --- | --- |
| [Prescribed generator sampler at d365cbf](https://github.com/RosettaCommons/RFdiffusion2/blob/d365cbf4db3958814a9f8e4f6f94fa309dfebc2b/rf_diffusion/inference/model_runners.py) | Legacy symmetry branches read `idx_pdb` before local assignment; the local failure log matches this path. This is not a claim that every version lacks homodimer support. |
| [Agent-selected sampler at 86507b6](https://github.com/RosettaCommons/RFdiffusion/blob/86507b6538f51fce57b5a72477165f03999ed7ae/rfdiffusion/inference/model_runners.py) | The final sampling branch copies predicted coordinates and subsequently applies symmetry. Investigate motif geometry at this boundary. |
| [Agent-selected output writer at 86507b6](https://github.com/RosettaCommons/RFdiffusion/blob/86507b6538f51fce57b5a72477165f03999ed7ae/scripts/run_inference.py) | Saves final denoised coordinates and input-derived residue labels. Residue-label retention alone does not establish coordinate retention. |
