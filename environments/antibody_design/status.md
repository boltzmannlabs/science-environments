# Antibody Design Collection

The collection is organized around monoclonal antibody task definitions, published benchmark references, completed computational run packages and standalone task result summaries. Its [main README](README.md) describes the directory tree, and the [environment specification](ENVIRONMENT_SPEC.md) defines the file conventions.

| Collection area | Guide |
| --- | --- |
| Task definitions and recording conventions | [Tasks](tasks/README.md) |
| Reference documents, calculated comparisons and figures | [Benchmarks](benchmark/README.md) |
| Methods, code, prepared inputs and execution records | [Source](src/readme.md) |
| Scientific configurations, reports, native outputs and task summaries | [Results](results/README.md) |
| Model and tool landscape | [Models and tools](MODELS_AND_TOOLS.md) |

Agent-Scientist settings use `configs/<task_id>/<run_id>.json`. Scientific configurations use `results/<task_id>/<run_id>/run.json`. Matching source packages use `src/<task_id>/<run_id>/`, with exactly two Markdown files in each `logs/` directory.
