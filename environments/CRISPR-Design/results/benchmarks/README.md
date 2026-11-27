# Completed benchmark execution results

Seven model evaluations are stored under `00N_<Model>/Run-4_2026-11-12/`.
Each package includes its report, predictions, metrics, benchmark record, execution
log and the available input/model/protocol snapshots. Run-4 identifies the original
campaign; these files were moved without rerunning it.

See the [benchmark registry](../../benchmark/BENCHMARK_RUNS.md) for report links,
evaluation scope and scientific limitations. Original execution scripts are under
[scripts/benchmarks/](../../scripts/README.md).

[PROVENANCE.json](PROVENANCE.json) binds 48 copied scientific artifacts to their
original source handles and SHA-256 hashes. Destination paths include both result
files and relocated scripts. Verify the checksum list from this directory with:

```bash
sha256sum -c PROVENANCE.sha256
```

Source datasets, weights and environments remain external. No full application,
wet-lab validation or safety claim follows from these endpoint evaluations.
