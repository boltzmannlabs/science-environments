# Formulation Optimization Gym

Question: Can an evidence-led agentic system identify contributors to a ranolazine 500 mg extended-release dissolution failure and propose a more robust formulation? Current answer: public sources support recall/label identification and separately labeled research-prototype simulation, **not** a recalled-lot root cause or validated improved product.

Read the [full environment report](ENVIRONMENT_REPORT.md) for completed workflows, tools, model execution, specialist roles, assumptions, numerical scenario outcomes, limits and tests. See [ENVIRONMENT_SPEC.md](ENVIRONMENT_SPEC.md) for requirements and architecture, [STATUS.md](STATUS.md) for actual state, [config/README.md](config/README.md), [tasks/README.md](tasks/README.md), and [tests/README.md](tests/README.md) for links to runnable artifacts.
For observed run blockers, resolved implementation defects, mitigations and outstanding actions, see [ISSUES.md](ISSUES.md).

Research is filed separately as [research notes](../../research/formulation-optimisation-gym-environments/research-notes.md) and [references](../../research/formulation-optimisation-gym-environments/references.md). The original implementation remains a sibling; a runnable copy of its code, public snapshots, tests and outputs is in the [packaged gym](scripts/formulation-optimization-gym/). The top level of this folder indexes the runnable snapshot, config, tasks, tests, skills and results.

For local execution, enter `scripts/formulation-optimization-gym/` and run `python -m unittest discover -s tests -q` or `python run.py benchmark`. The opt-in modeling examples need an isolated Python environment with `openpkflow==2.9.0`. Source PDF integrity verification with `--pdf` requires a separately obtained, authorized PDF matching the saved SHA-256. Do not mistake packaged public snapshots for controlled batch data.

Verify the package itself from this folder using `python tests/verify_package_manifest.py` and `python tests/check_packaged_links.py`. The original working files remain in the sibling project; do not edit controlled sources or claim that copied FDA snapshots are signed GMP records.
