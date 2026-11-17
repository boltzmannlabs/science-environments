# Recorded runs and launch profiles

Each task contains compact `run_*.json` summaries, following the antibody-design environment: specialist use, LLM, cumulative tokens and time. The model is GPT-6.1-Sol through Codex (`openai-codex`). Ten actual approach records cover the six tasks; BLA and AtHOL1 have only agent-alone records.

`tokens_used.input_output` excludes cached input. `cache_reads` counts repeated cached context. The reported total is a persisted lower bound, not cost or newly generated text. Recorded time spans include pauses and follow-ups; they are distinct from configured budgets and scientific compute time. Snapshots are dated in each file.

The retained `v1/` profiles are prospective launch settings, not the effective configuration of historical runs. `v2/` remains unselected. See task READMEs for the actual run files. Exclude MLDE from future launches.
