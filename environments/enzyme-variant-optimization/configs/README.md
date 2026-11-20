# Run configurations

Each task contains only compact actual-run JSON files, using the antibody-design format: `use_subagent`, `llm_model`, `llm_version`, `tokens_used` and `time_budget`. The enzyme runs used GPT-6.1-Sol through Codex.

`input_output` counts uncached input plus output; `cache_reads` counts cached context across calls. Snapshot: 16 November 2026. A `null` time budget means no fixed total campaign budget was established; recorded elapsed time is in task result READMEs.

These are historical run records. New executions require separately approved frozen settings.
