# BolChem sources — owner/evaluator only

Source list for a specification-only contribution, related to issue #46.
Keep this material outside agent execution prompts and permitted candidate inputs.

## De novo reference and software

- Qian et al., *AlphaDrug: protein target specific de novo molecular generation*,
  PNAS Nexus (2022), [DOI 10.1093/pnasnexus/pgac227](https://doi.org/10.1093/pnasnexus/pgac227).
  Computational reference, not evidence that this contribution has run the method.
- [Author implementation](https://github.com/CMACH508/AlphaDrug), reviewed source
  revision `0b182f94d3ec0a0ea750b57b9630a01da728fd5b`: prepared inputs, sampling,
  docking and descriptor definitions. Endpoints and intermediate search candidates
  are distinct; exact selection semantics must be checked before numeric comparison.
- [RCSB 1A9U](https://www.rcsb.org/structure/1A9U): p38 structure and bound ligand.
  The supplied prepared derivative must remain distinguishable from deposited data.
- [Official Smina project](https://sourceforge.net/projects/smina/): public docking
  software. Same software name alone does not establish protocol equivalence.

## Optimization reference and software

- He et al., *Evaluation of reinforcement learning in transformer-based molecular
  design*, Journal of Cheminformatics 16, 95 (2024),
  [DOI 10.1186/s13321-024-00887-0](https://doi.org/10.1186/s13321-024-00887-0).
  Original optimization endpoint uses predicted DRD2 activity, QED and similarity;
  docking and mandatory ADMET thresholds are not its published qualifying rule.
- [Author implementation](https://github.com/MolecularAI/transformer_rl), reviewed
  revision `a0622fc2fe16812c7530bca20dcca9a9fd874513`: predictor/config listings,
  descriptor construction and sampling similarity. Binary availability was listed;
  actual model loading is not qualified by this contribution.

The live issue check on 5 November confirmed
[#46](https://github.com/boltzmannlabs/science-environments/issues/46) is open and
assigned to Ankith116. Historical issue #89 could not be resolved by the API and
is not used as a verified tracking reference.
