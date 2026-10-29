# MD benchmark

The benchmark compares adapter execution with independent scientific
qualification. It must not collapse these into a single success flag.

## Tracks

1. **Packet track** — all 62 explicit agent packets and their native adapters.
2. **Core execution track** — reproducible OpenMM/CUDA water-box repeats.
3. **Real-system track** — bounded villin, DNA, barnase–barstar, and
   trypsin–benzamidine runs.
4. **Recovery track** — frozen crash, NaN, parameter, checkpoint, resource,
   and false-success fixtures.

## Metrics

Record adapter completion, diagnosis accuracy, scientifically valid recovery,
false-PASS rate, runtime, resource use, provenance completeness, and
reproducibility. A packet is `PASS` only when its independent evaluator has
the evidence required by its task; otherwise it is `REVIEW` or `FAIL`.

See `results/agent_qualification_report.md` and
`results/real_system_production/RESULTS.md` for the current evidence.
