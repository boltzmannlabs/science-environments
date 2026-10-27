# Coarse-Grained MD Environment Specification

## Objective

Provide auditable workflows for constructing, executing, analysing, and
qualifying coarse-grained molecular simulations while keeping resolution and
force-field assumptions explicit.

## Inputs

System representation or atomistic source, mapping definition, CG topology,
force-field/model and version, engine, thermodynamic state, box, timestep,
seed, replica plan, resource limits, and reference observables where available.

## Outputs

Validated system/topology, run manifest, trajectory and logs, observables,
uncertainty/reproducibility analysis, provenance, and PASS/FAIL/REVIEW status.

## Failure taxonomy

Invalid mapping, topology/parameter failure, numerical instability, inadequate
equilibration, insufficient sampling, observable mismatch, reconstruction
failure, resource failure, provenance/licence failure, and unresolved failure.

## Qualification boundary

Contracts and the toy bead-spring profile are implemented. Protein, membrane,
LLPS, polymer, nanoparticle, multiscale, parameter-fitting, and learned-CG
profiles require dedicated fixtures, references, and independently repeated
engine runs before they can be called qualified.
