# Local validation — 28 October 2026

Version 0.1 was checked with Python **3.13.7**. The isolated native integration used Agent-Scientist revision `062351dd048c142840f78ea198f22417d983ccda` and its Python **3.14.7** environment. The host checkout had pre-existing unrelated edits; this is a local compatibility observation, not certification of a clean released host.

## Executed checks

| Check | Result and scope |
| --- | --- |
| Combined software suite | **49 tests passed, zero failures/skips**, including the real native loader/registry test. [Log](software-tests.log). |
| Offline package build/install | Passed: wheel built without an index, installed in a fresh virtual environment, then entry point, packaged skill, CLI and campaign create/report exercised outside source. [Log](package-check.log). |
| Synthetic episode | Passed: scripted task/check/action/evidence/decision/freeze/offline-evaluation sequence with artificial records. [Run receipt](synthetic-run.log), [evaluation output](synthetic-evaluation.json). |
| Independent critique | Critic-authored regression cases exposed and drove fixes to objective support, unchecked rule findings, cross-campaign association, overflow, resource eligibility, exact-budget handling, final-evidence claims and final-rule validation. These cases are included in the passing suite. |
| Documentation/catalogue | All 87 relative links across 17 Markdown files resolved, including heading anchors. All 29 mapped jobs remained present in the inspected catalogue, its hash matched, and whitespace checks passed. |

Reproduce from the environment directory:

```bash
LEADOPT_AGENT_SOURCE=/home/boltzmann13/agent-scientist \
LEADOPT_AGENT_PYTHON=/home/boltzmann13/agent-scientist/.venv/bin/python \
python3 -m unittest discover -s tests -v

python3 scripts/check_package.py --output /absolute/new/package-check
python3 scripts/run_synthetic.py --output /absolute/new/synthetic-run
```

Replace host paths with the intended installed checkout and interpreter. The package check requires local pip/setuptools/wheel; the campaign runtime has no third-party Python dependencies. Package and synthetic output directories must be new. Native checks use temporary host configuration and storage, not the user's active installation.

[validation.json](validation.json) records versions, the tested source digest and built-wheel digest. Wheel builds may differ in archive timestamps; the digest identifies this build rather than promising bit-for-bit reproducibility. Source hashing is defined in that file.

## What this evidence does not establish

**Zero model calls and zero scientific-service calls were made.** The fixture's counted submission is artificial. No COVID/Moonshot task, live worker qualification, base-agent comparison or scientific performance evaluation has run.

Native registry dispatch does not prove a model will follow the skill or that real service outputs are correctly interpreted. Record provenance and resource completeness remain agent supplied. The evaluator verifies recorded identities, rules and retained digests; it does not isolate files or authenticate measurements. Final labels in the synthetic test are public invented values.

The broader qualification and contribution work remains listed in [STATUS.md](../STATUS.md).
