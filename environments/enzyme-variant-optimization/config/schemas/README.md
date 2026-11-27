# Configuration schemas

`task_configuration.schema.json` validates stored task configurations, including the difference between recoverable historical metadata and complete launch settings. `launch_settings.schema.json` validates explicit model/provider/reasoning fields in the original launch snapshots. Validate with `python scripts/validate_run_records.py`; no scientific jobs run.
