# Benchmark: IgGM: Paired Six-CDR Sequence/Structure Co-Design

**Task ID:** `task_018_iggm_paired_cdr_sequence_structure_codesign`

**Task:** [IgGM: Paired Six-CDR Sequence/Structure Co-Design](../../tasks/monoclonal_antibody_design/task_018_iggm_paired_cdr_sequence_structure_codesign.md)

## Published Computational Metrics

**Source:** [IgGM, ICLR 2025 paper](https://proceedings.iclr.cc/paper_files/paper/2025/file/fa5b423e24b442180bcd4e13ae75a27f-Paper-Conference.pdf), Table 2; [author results page](https://iggm.rubo.wang/); source revision [TencentAI4S/IgGM @ `06abc563b3fc`](https://github.com/TencentAI4S/IgGM/tree/06abc563b3fc8c7ea020543add16b69b6f8a1c8d). The original preprint began in 2024; this benchmark uses the 2025 conference version, not the later foundation-model update.

| CDR | IgGM AAR | IgGM backbone RMSD (Å) |
| --- | --- | --- |
| H1 | 0.740 | 0.555 |
| H2 | 0.644 | 0.486 |
| H3 | 0.360 | 2.131 |
| L1 | 0.750 | 0.589 |
| L2 | 0.743 | 0.378 |
| L3 | 0.635 | 0.847 |

These are Table 2 six-CDR antibody-design results on SAb-2023H2-Ab under the source sampling protocol. AAR favors higher values and backbone RMSD favors lower values.

## Evaluation Protocol

- Use the paired-antibody test manifest and corresponding six-CDR masks from the conference evaluation.
- Compare the same initialization condition and five-sample budget; report each initialization track separately.
- Calculate AAR independently for H1, H2, H3, L1, L2 and L3.
- Match the source backbone atom correspondence, alignment and aggregation for RMSD.
- Keep filtered-target results and full-source aggregate results separately labelled.
