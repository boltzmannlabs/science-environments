# Environment specification

The agent receives the paper, selected endpoint structures, mapping metadata,
and permitted code/data. It must generate separate complex and solvent legs,
validate atom mapping, create the lambda schedule, and emit engine-ready setup
files. This task currently demonstrates independent paper-protocol
reconstruction and endpoint-readiness validation. A numerical free-energy
result is only evaluated when complete endpoint topologies, trajectories,
overlap, convergence, replica and uncertainty evidence are present.

The current `20/20` parameter result is configuration fidelity only. It must
not be reported as `100% FEP reproduction accuracy` or as a production
free-energy qualification.
