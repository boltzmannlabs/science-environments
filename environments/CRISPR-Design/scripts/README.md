# Execution scripts

`benchmarks/00N_<Model>/inference.*` contains the original inference scripts retained
from the completed benchmark campaigns. These files are preserved byte-identically;
their source handles and SHA-256 hashes are in
[the provenance manifest](../results/benchmarks/PROVENANCE.json).

These are historical execution recipes with external data, model and runtime paths,
not standalone commands that work from a fresh clone. Consult the corresponding
[benchmark definition](../benchmark/README.md) and captured execution protocol before
use. This restructuring does not install their dependencies or rerun inference.

The current knockout implementation and backend probe remain in [src/](../src/CONTRACTS.md).
