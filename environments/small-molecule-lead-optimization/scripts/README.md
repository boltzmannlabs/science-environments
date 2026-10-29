# Local plugin installation

The directory installer copies the standalone `leadopt_env` package, campaign implementation, manifest and skill to an explicit destination. It refuses to overwrite an existing directory. It neither enables the plugin nor edits Agent-Scientist settings.

From this environment directory, supply the plugin directory of the intended Agent-Scientist installation:

```bash
python3 scripts/install_plugin.py --destination /absolute/intended/SCI_HOME/plugins/leadopt_env
```

Then use Agent-Scientist's existing plugin controls to enable `leadopt_env`. Configure its one setting, `plugins.entries.leadopt_env.settings.db_path`, as an absolute path for the local SQLite campaign database. This is campaign storage, not scientific-service configuration. For example, merge the following structure with the existing settings instead of overwriting them:

```yaml
plugins:
  entries:
    leadopt_env:
      settings:
        db_path: /absolute/campaign-storage/leadopt.sqlite
```

Run `sci plugins enable leadopt_env` in the intended host context and start a fresh session. The package's skill is registered as `leadopt_env:lead-optimization`; it is read from the installed plugin rather than copied separately into the host's skill directory. Plugin tools may be deferred and discoverable through the host's tool-search interface.

The package also declares the standard `sci_agent.plugins` Python entry point and the `leadopt-env` local CLI in `pyproject.toml`. No changes to Agent-Scientist source are required.

## Offline package check

Using Python with `pip`, `setuptools` and `wheel` already available, run:

```bash
python3 scripts/check_package.py --output /absolute/new/disposable-check-directory
```

This builds a wheel from a temporary source copy without contacting an index, installs it into a fresh virtual environment, and exercises the installed entry point, skill, CLI and core campaign operations outside the source tree. It does not install into the active Agent-Scientist runtime. Dependency installation, if needed, is separate from this offline check.

## Isolated native check

Use an existing Agent-Scientist source checkout and its Python executable. The check installs into a temporary directory, writes a temporary host configuration, uses the real loader and tool registry, checks skill discovery, and tears down registrations. It makes no model or scientific-service calls and does not change the active user configuration.

```bash
LEADOPT_AGENT_SOURCE=/absolute/path/to/agent-scientist \
LEADOPT_AGENT_PYTHON=/absolute/path/to/agent-scientist/.venv/bin/python \
python3 -m unittest discover -s tests -p 'test_plugin_native.py' -v
```

Successful loader/dispatch checks establish the local integration path only. They do not qualify remote workers, show a model following the skill, or establish scientific improvement. Campaign advice and recording are explicit operations; this implementation does not automatically observe every scientific call.
