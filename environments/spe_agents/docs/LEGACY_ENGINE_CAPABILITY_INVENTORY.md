# Legacy Boltzmann SPE Engine Capability Inventory

Inventory date: 2026-10-19

Evidence level: static source review only

Operational verification: **not performed**

## Scope and evidence

This inventory examines the Git snapshot at commit `7a802e94`, under
`Esther/Esther/boltzmann_api/spe`. That legacy working-tree path is currently
deleted, so the review used committed source rather than an installed or running
service. The findings below are implementation evidence for adapter planning;
they are not evidence that an endpoint, dependency set, CPU path, or GPU path is
currently available.

Primary evidence inspected:

- `common/constants.py`
- `common/utils.py`
- `api/schemas.py`
- `api/routes.py`
- `pipeline/executor.py`
- `autonomy/orchestrator.py`
- `requirements.txt` and `Dockerfile`
- the committed README and GPU/autonomy change report

## Declared calculation surface

| Area | Static implementation evidence | Adapter interpretation |
|---|---|---|
| Engine | PySCF `>=2.4.0`; GPU4PySCF CUDA 12 installation attempted in the Docker build | Exact installed versions must be discovered at runtime; no version may be inferred from the requirement range |
| HF | CPU RHF/UHF selected for `HF` | Declared CPU capability; real smoke tests required |
| DFT | CPU RKS/UKS and optional GPU RKS/UKS | GPU support is conditional on import and CUDA availability |
| Functionals | HF, LDA, PBE, B3LYP, PBE0, TPSS, M06-2X, CAM-B3LYP, wB97X-D, wB97X-D3, wB97M-V | These are API allow-list entries, not a verified method-by-element matrix |
| Basis sets | STO-3G, 6-31G, 6-31G*, 6-311G**, cc-pVDZ, cc-pVTZ, cc-pVQZ, aug-cc-pVDZ, aug-cc-pVTZ, def2-SVP, def2-TZVP, def2-TZVPP, def2-QZVP | These are API allow-list entries; actual PySCF coverage varies by element |
| Elements | Constants enumerate H through Ba | Input validation only capitalizes symbols; it does not enforce this list, and no basis compatibility matrix is exposed |
| ECP | def2 ECP inference for atoms with atomic number 37 or greater | Only the def2/heavy-element path has explicit ECP selection logic |
| Charge and spin | Integer charge; optional multiplicity; RHF/RKS for singlets and UHF/UKS for open shell; electron-parity preflight exists in the autonomy layer | Explicit user charge/multiplicity must be preserved by the adapter; auto-selection needs separate policy review |
| Coordinates | Cartesian coordinates interpreted as Angstrom | The legacy API has no coordinate-unit field |
| Dispersion | Executor accepts D3, D3BJ, or D4 and assigns the corresponding PySCF dispersion setting | The dedicated `dispersion_energy_ha` result is never populated in the inspected executor; support must remain unverified |
| Solvent | ddCOSMO with a named-solvent dielectric lookup | Unknown solvent names silently fall back to water dielectric (`78.4`), which is unsuitable for a strict adapter and must be rejected or made explicit |
| Density fitting | Optional, enabled by the autonomy path with size-dependent logic | Behavior needs CPU/GPU and numerical-regression tests |

## Declared results and properties

The executor has structured fields for:

- total, nuclear-repulsion, and derived electronic energies in Hartree;
- converted total energy in eV, kcal/mol, and kJ/mol at the API layer;
- SCF convergence, iteration count, final change, and energy history;
- HOMO, LUMO, HOMO-LUMO gap, and all orbital energies;
- dipole vector and magnitude;
- Mulliken and approximate Hirshfeld charges;
- point-group label when PySCF symmetry detection succeeds;
- a small same-basis functional ensemble and sensitivity summary;
- wall time, start/completion timestamps, backend label, warnings, and an error message.

Important limitations from static inspection:

- `dispersion_energy_ha` and `solvation_energy_ha` are initialized to `None`
  and are not assigned computed component energies.
- A failed executor result uses numeric zero placeholders for energy fields.
  The new adapter must translate these as absent outputs, never as physical
  zero-energy results.
- Hirshfeld charges use an internal approximate free-atom-density construction;
  scientific validation is required before treating them as a promoted property.
- The response records `CPU` or `GPU`, but it does not include the concrete
  PySCF/GPU4PySCF version.

## Inputs, artifacts, and service lifecycle

The committed service declares JSON coordinates plus upload parsers for XYZ,
SDF/MOL, CIF, and Gaussian GJF/COM-family files. A separate command-line runner
also describes SMILES ingestion. Export routes can produce XYZ, SDF, and CSV;
the standalone runner describes JSON result files as well.

The legacy `/calculate` route is synchronous. `/status` reports service
capabilities, not per-job state, and there is no per-job cancellation endpoint.
Artifacts are not returned as a checksum-bearing manifest. Consequently, a
conforming `SPEAdapter` will need either:

1. an asynchronous wrapper that owns job state and cancellation semantics; or
2. an explicitly synchronous transport implementation with cancellation marked
   unsupported and deterministic artifact collection after completion.

## Gaps that block a real adapter from promotion

1. Restore or identify the actual deployable engine source and container image.
2. Probe exact PySCF, GPU4PySCF, CUDA, dispersion, and parser versions at runtime.
3. Replace broad method/basis/element allow lists with an executable compatibility
   matrix, including ECP requirements.
4. Reject atom/coordinate count mismatch, non-finite coordinates, invalid element
   symbols, invalid multiplicity, unknown solvents, and unsupported dispersion
   modes before engine submission.
5. Decide whether automatic charge, spin, method, basis, and solvent choices are
   prohibited by the adapter or represented as reviewable planning decisions.
6. Preserve raw input/output/log artifacts with SHA-256 checksums.
7. Translate failed zero placeholders to missing values plus a classified failure.
8. Add explicit engine-version provenance and immutable request fingerprints.
9. Verify water, methane, ammonia, and ethanol through CPU and available GPU paths,
   then test invalid input, non-convergence, unavailable tool, and malformed output.
10. Numerically validate density fitting, dispersion, ddCOSMO, charge analyses, and
    any patched GPU4PySCF behavior against controlled references.

Until those gates pass, the correct integration status for all environments that
name `boltzmann-spe-api` remains `unverified`.
