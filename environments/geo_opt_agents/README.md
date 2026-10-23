# Geo-Opt Agents Environment

**Status:** Validated (frozen contract qualification and declared live GPU cases)

This environment contains 18 geometry-optimisation specialist contracts,
task packets, molecular fixtures, deterministic graders, GPU-backed evidence,
and BioDesignBench-style task/result cards.

## Scope

- Structure validation, connectivity, convergence, recovery, minimum checks,
  conformers, protein–ligand checks, and orchestration.
- Frozen task and result manifests under `examples/geo_opt_tasks/` and
  `examples/geo_opt_results/`.
- GPU4PySCF/PySCF evidence where the backend was available.

## Validation

```bash
pytest -q tests
```

The result cards explicitly distinguish live GPU engine results from
deterministic or contract fixtures. Review entries are retained and are not
silently promoted to successful production optimisation.

## Deliverables

- [`ENVIRONMENT_SPEC.md`](ENVIRONMENT_SPEC.md)
- [`REFERENCES.md`](REFERENCES.md)
- [`examples/geo_opt_tasks/`](examples/geo_opt_tasks/)
- [`examples/geo_opt_results/`](examples/geo_opt_results/)
- [`reports/`](reports/)
