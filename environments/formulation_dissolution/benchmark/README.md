# Benchmark tracks and interpretation

The [configuration](benchmark_config.yaml) links existing code/data rather than adding a disconnected benchmark implementation.

- Published pH 6.8: six related examples, whole-formulation leave-one-out mean baseline at seven nonzero aligned times, separate reference context. Original transcription not independently source-verified; same publication across train/test. Historical macro MAE 7.58095 pp, RMSE 8.83341 pp. Descriptive, not product validation.
- Published HCl: three SR patent summaries, separate LOFO comparison; IR excluded. Prior primary-HTML Table 4 sequence check retained. Historical macro MAE 12.73333 pp, RMSE 14.63276 pp. Dose/process/unit variability incomplete; not a QC method.
- Six-model published fits: 59 converged reconstructions; errors on fitted curves are in-sample, not blind holdout. KP early-segment AICc is not compared to full-curve AICc.
- Synthetic batches: 24 Weibull-generated batches, seed 31415, 12/4/8 whole-batch split; validation-only selection. Test residuals, MAE/RMSE/bias, illustrative intervals and mathematical f2. Weibull preference is expected from the generating law, not evidence of ranolazine predictive superiority.
- Research grid: 117 feasible 500 mg / 695 mg designs and 256 assumed scenarios/design; seed 2931; shared-draw F8/F1 comparisons, zero-effect controls and sign sensitivity. No real commercial QC pass fraction or validated optimized formulation.
- Commercial measured holdout/replay: not_evaluated; no authorized linked measured formulation-profile groups/frozen historical pool supplied. No matched base-agent or A/B/C/D scientific comparison.

Reproduce through the environment README. New outputs belong in ignored `.runs/`. Bounded historical artifacts under `data/processed/` support regression checks; [integration receipt](../results/validation.json) records fresh command execution separately.
