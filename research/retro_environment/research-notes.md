# Retrosynthesis of a fluorinated quinoline ether: research notes

## Objective

Evaluate computational retrosynthesis pathways for target
`CC1=C(C=C2C=CC(=C(C2=N1)F)F)OC3=C(C(=CC=C3)F)C(C)(C)O`; assess the model's central disconnection and compare reaction families with accessible, clearly labeled experimental references. The separate `synth-test` forward-reaction experiment is **out of scope**.

## Inputs and observations

The private authenticated platform returned 16 top-level paths. We preserve sanitized pathway precursors, product SMILES, ranking metadata and model yield fields in `../../environments/retro_environment/results/route_summary.json`. The result's raw `num_steps` disagrees with counts reconstructed from the reaction-node tree. `top0` comprises TBS protection, proposed phenol–aryl bromide ether formation, and deprotection.

The expected top0 protected ether appeared last among forward predictions (score zero), whereas a quinolinol O-silylation was strongly ranked. The proposed protection conditions contained fluoride, which challenges TBS installation, and the proposed coupling conditions lacked a coupling catalyst. Atom mapping for the desired products was internally consistent with depicted bonds, but does not demonstrate that the reactions occur. The deprotection motif is plausible conditionally on accessing the intermediate.

`top1` had the largest illustrative compounded model percentage among the routes (39.15% versus top0's 30.91%). These values are arithmetic of uncalibrated model step fields; the branch structure, purification, reaction compatibility and overall process yield are not captured. **There is no target-specific experimental yield or proof that our route performed better.**

## Public benchmark and limitations

Corey/Venkateswarlu [1] describe the TBS-protection class; their publisher procedure was inaccessible in this review. The general Ullmann-type paper [2] describes diaryl-ether synthesis as a class; the full article was access-limited. An openly accessible ChemSpider SyntheticPages procedure [3] demonstrates TBAF/THF deprotection of an *unrelated* silyl ether and reports 32% isolated yield **for that unrelated substrate**. That observation neither validates this target nor calibrates the model's 62.02% condition yield. Two broadly retrieved patent documents [4,5] were screened but did not establish the exact route. Text search cannot prove novelty, patent absence or freedom to operate.

Reagent supply, selectivity (including O/N arylation), actual conversion, isolable intermediate stability, measured impurities and overall route feasibility remain unknown. Any proposed experimental program requires qualified chemist review, starting material verification and analytical characterization.

See [references.md](references.md) for evidence URLs and [environment status](../../environments/retro_environment/STATUS.md) for implementation readiness.
