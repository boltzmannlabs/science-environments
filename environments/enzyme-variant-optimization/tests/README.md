# What these tests check

The default suite runs on the installed package and uses artificial input files and tool responses. It does not need Agent-Scientist credentials, a GPU, or paid tool access.

It covers:

- Invalid tasks, changed catalytic residues, duplicate sequences, and candidate limits.
- Saved experiment records, restarts, job receipts, and uncertain submission outcomes.
- Real DiscoveryRSI execution using artificial hypotheses and observations.
- Keeping each sequence, structure version, ligand, and result linked correctly.
- Preparing/uploading inputs and transferring designed sequences between steps.
- Detecting changed, partial, corrupt, or mismatched result files.
- Mapping ThermoMPNN output positions to the actual structure and sequence.
- Combined reports that retain failed checks and missing results.
- Exact `Seq_id,Sequences,SMILES` headers when selected by the task configuration.
- Availability derived from current catalogue entries, without separate activation for deployed tools.
- EnzyControl, DeepAllo, and RFD3 file fields, supported formats, preserved coordinates, upload receipts, and scaffold sample limits.

Run `python -m pytest -q` after the README's installation and dependency setup. DiscoveryRSI tests require the actual pinned source checkout; a missing checkout fails clearly rather than silently replacing it with a mock.

The optional `native/` directory adds scripted tests of role context and native-host failure reporting. Run it with the documented `--native-support` option only when those separate support modules are available. It does not run an actual scientific campaign.

Dataset qualification, private evaluators, and comparison-runner tests are separate benchmark work and are not copied into this environment suite. Passing these software tests does not establish scientific accuracy or better enzyme activity.
