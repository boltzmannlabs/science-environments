# Task: md_paper_001

**Task family:** Paper-based MD environment reconstruction
**Status:** executable setup benchmark; scientific outcome qualification is separate.

## Research paper

Exploring ligand binding pathways on proteins using hypersound-accelerated
molecular dynamics. DOI: `10.1038/s41467-021-23157-1`.

Selected system: human CDK2 with ATP-competitive ligand CS3. The selected
crystal input is PDB `4EK5`; the paper also provides trajectory/input data in
BSM-00027. This task first reconstructs the conventional MD setup and treats
hypersound perturbation as an optional adapter.

## Agent objective

Read `PAPER_REFERENCE.md` and the permitted PDB input, extract the reported
protocol, and generate an executable setup. Do not infer hypersound parameters
when the supplementary table is unavailable.

## Required outputs

`reference/extracted_parameters.json`, `configs/config_A_reference.json`,
`configs/config_B_agent.json`, `configs/config_C_alternative.json`,
`configs/config_D_perturbed.json`, and an evaluation JSON under
`expected_outputs/`.

## Acceptance criteria

Score parameter extraction, input identity, protocol fidelity, environment
validity, and execution separately. A successful short run cannot receive
scientific-outcome credit for the paper's 100-ns multi-replica results.
