# Antibody Design Benchmarks

Reference metrics, reported values and task-specific interpretation for the ten antibody tasks. Benchmark folders and filenames match their corresponding files under `tasks/`.

## Task Benchmarks

| Task | Benchmark | Evidence type |
| --- | --- | --- |
| [HER2 reference optimization](../tasks/monoclonal_antibody_design/mab_her2_reference_optimization.md) | [Reference results](monoclonal_antibody_design/mab_her2_reference_optimization.md) | Released individual optimization endpoints. |
| [PD-L1 epitope design](../tasks/monoclonal_antibody_design/mab_pdl1_epitope_design.md) | [Reference results](monoclonal_antibody_design/mab_pdl1_epitope_design.md) | H5 structural agreement and campaign-level results. |
| [PD-1 epitope design](../tasks/monoclonal_antibody_design/mab_pd1_epitope_design.md) | [Reference results](monoclonal_antibody_design/mab_pd1_epitope_design.md) | Screening/recovery benchmarks; individual design scores unavailable. |
| [LCAT CDR design](../tasks/monoclonal_antibody_design/mab_lcat_cdr_design.md) | [Reference results](monoclonal_antibody_design/mab_lcat_cdr_design.md) | Single-case reconstruction compared with aggregate paper results. |
| [Gal-3BP reference design](../tasks/monoclonal_antibody_design/mab_gal3bp_reference_design.md) | [Reference results](monoclonal_antibody_design/mab_gal3bp_reference_design.md) | Interface contacts, stability and accessibility. |
| [HER2 biparatopic design](../tasks/bispecific_design/bispecific_antibody_design.md) | [Reference results](bispecific_design/bispecific_antibody_design.md) | Zanidatamab literature comparator; no public TxBench match. |
| [Cellular mechanism assessment](../tasks/bispecific_assessment/bispecific_cellular_mechanism_assessment.md) | [Reference results and trajectories](bispecific_assessment/bispecific_cellular_mechanism_assessment.md) | Adaptation of one public TxBench example. |
| [CNS delivery assessment](../tasks/bispecific_assessment/bispecific_cns_delivery_assessment.md) | [Evaluation requirements](bispecific_assessment/bispecific_cns_delivery_assessment.md) | Generic local task; related TxBench examples only. |
| [CNS readout comparison](../tasks/bispecific_assessment/bispecific_cns_readout_comparison.md) | [Reference results and trajectories](bispecific_assessment/bispecific_cns_readout_comparison.md) | Adaptation of one public TxBench example. |
| [CNS integrated gate](../tasks/bispecific_assessment/bispecific_cns_shuttle_integrated_gate.md) | [Reference results and trajectories](bispecific_assessment/bispecific_cns_shuttle_integrated_gate.md) | Adaptation of one public TxBench example. |

## Interpreting Reference Values

Published measurements, prompt-provided values and agent-reported observations are identified in each benchmark. Reference values become grading targets only when the dataset, metric definition and comparison conditions match and the evaluation has an established answer or acceptance rule.

The TxBench-derived assessment documents include values from public prompts or agent results. Those releases do not supply task-level grades or verified answer keys. The general CNS-delivery task requires study-specific values; the HER2 biparatopic task uses literature measurements and structural evidence.
