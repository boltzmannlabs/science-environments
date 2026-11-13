# BLA high-temperature performance: launch and continuation

Prepare a fresh run with `python scripts/launch_task.py --task task_003_bla_high_temperature --approach agent_alone --run-dir /path/to/new-run` from the environment directory.
Use `agent_with_specialist` for reviewed native proposer/critic assistance; inspect/freeze settings and contracts before adding `--start`.
For an existing run, use `sci --resume <native-session-id>` in its original profile/workspace; do not execute archived source against it.
Offline benchmark regeneration: `python scripts/build_reports.py`. This performs no scientific or network calls.
