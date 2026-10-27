# Cross-Domain Scientific Problem-Solving Agents

**Status: Executable fixture qualification.** This package provides reusable
diagnosis, controlled-recovery, and independent-audit agents for SPE,
Geo-Opt, HOMO–LUMO, QM/MM, and FEP/TI workflows. It does not silently replace
the domain evaluators or claim production qualification.

## Agent groups

- Shared PS-01–PS-06: log analysis, root cause, recovery planning, bounded
  retry, independent audit, and provenance/regression audit.
- SPE PS-01–PS-06: SCF, method/basis, charge/spin, input geometry, numerical
  precision, and energy-reference recovery.
- Geo-Opt GEO-PS01–GEO-PS06: optimizer failure, geometry repair, derivative
  consistency, minimum verification, constraints/symmetry, and regression.
- HOMO–LUMO HL-PS01–HL-PS06: orbital indexing, occupations, gap arithmetic,
  electronic-state recovery, orbital character, and conformer/state checks.
- QM/MM QMMM-PS01–QMMM-PS07: region, boundary, charge/embedding, QM SCF,
  coupling/forces, region sensitivity, and trajectory recovery.
- FEP/TI FEP-PS01–FEP-PS10: mapping, transformations, lambda schedule,
  overlap, convergence, cycle closure, estimators, charge corrections,
  restraints/standard state, and result qualification.

The package contains 41 contracts in total.

Run the deterministic fixture harness:

```bash
python scripts/run_harness.py
```

The harness tests diagnosis and safe stopping on frozen evidence packets. Real
engine adapters and held-out scientific references remain required for domain
qualification.
