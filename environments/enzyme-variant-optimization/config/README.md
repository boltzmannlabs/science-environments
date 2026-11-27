# Configuration

| Location | Purpose |
|---|---|
| [environment.yaml](environment.yaml) | Environment identity, catalog/schema links and explicit shared-settings policy. |
| [schemas/](schemas/README.md) | Real validation schemas for task records and launch snapshots. |
| [shared/](shared/README.md) | Common settings referenced by the applicable tasks, not automatically imposed on history. |
| [tasks/](tasks/README.md) | Descriptive model/approach filenames for all six tasks. |

Tokens, runtime, job status and execution logs belong in [runs](../runs/README.md). Complete original launch settings are preserved there with hashes. Unknown historical settings remain explicit; these records cannot silently become executable defaults.

All path references in `environment.yaml` resolve from that file’s directory (`path_base: environment_file_directory`). Task-level references resolve from their own configuration file’s directory. The validator uses these declaring directories rather than the shell working directory and rejects paths outside this environment, including symlink escapes.
