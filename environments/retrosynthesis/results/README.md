# Validation status

The renamed monorepo installation passed **2,650 tests**, with **13 optional skips** and **94.57% coverage**, plus fresh installation and actual Agent Scientist/LocalRetro integration checks. See [migration verification](MIGRATION_VERIFICATION.md). GitHub publication and tests from the published revision remain pending.

The pre-migration base release passed **2,646 tests**, with **13 optional skips** and **94.57% package coverage**. Actual Agent Scientist plugin-discovery and LocalRetro bridge checks passed. The [base verification report](../docs/BASE_RELEASE_VERIFICATION.md) records scope, reproduction instructions and limitations.

These results belong to the original tested base file set. Renaming/restructuring and the new installed distribution require fresh installation, command, fixture and Agent Scientist checks. Their completed local verification is recorded in the linked migration report; no successful post-push check is claimed before a push and clean checkout actually occur.

Full held-out comparative benchmarking, specialist promotion and independent chemical review remain deferred. Existing scientific acceptance remains 8/14 steps. Neither test pass counts nor successful model inference establish chemical feasibility or improved research outcomes.

Keep only small validation summaries here. Do not add model weights, unrestricted run logs, hidden benchmark answers or raw experimental tables. The original [22 October snapshot](../STATUS.md) remains an unchanged historical record.

## Verification after an approved GitHub update

1. Record the exact published commit SHA and obtain a fresh checkout of that commit. Do not reuse this preparation working tree as proof of published contents.
2. Create a clean Python environment and install `environments/retrosynthesis` with the documented test/API/search extras. Check `retrosynthesis --help`, the legacy CLI, imports and dependency consistency.
3. Run the portable test suite with the 80% coverage gate and run the offline demo. Record skipped optional checks and warnings separately.
4. Verify native Agent Scientist plugin discovery and session isolation using the main/default profile. Confirm its existing tools remain registered.
5. With explicitly configured compatible scientific assets, exercise the actual chemistry host: create task, generate draft routes, inspect/import, validate, rank, explicitly submit and close. Record model/asset identity and resource use; do not treat model output as experimental support.
6. Save a small receipt tied to the published commit with installation, test and integration outcomes. Report any failure and avoid claiming post-publication validation until these checks finish.

This procedure is planned. No GitHub update or post-publication test is claimed by this preparation record.
