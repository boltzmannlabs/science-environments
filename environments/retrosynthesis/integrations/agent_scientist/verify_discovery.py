"""Verify real plugin discovery and scoped dispatch without any model call.

Run with the installed Agent Scientist Python interpreter and --scientist-source.
All plugin state is created in temporary homes and removed afterward.
"""

import argparse
import json
import os
from pathlib import Path
import shutil
import site
import sys
import tempfile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scientist-source", type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.scientist_source.resolve()))
    from pm.environments import committed_venv, site_packages
    runtime = committed_venv(args.scientist_source.resolve())
    if runtime is None:
        raise RuntimeError("Agent Scientist has no committed dependency environment")
    site.addsitedir(str(site_packages(runtime)))
    with tempfile.TemporaryDirectory(prefix="srg-plugin-") as tmp:
        previous = os.environ.get("SCI_HOME")
        os.environ["SCI_HOME"] = tmp
        try:
            _verify(Path(tmp))
        finally:
            if previous is None:
                os.environ.pop("SCI_HOME", None)
            else:
                os.environ["SCI_HOME"] = previous


def _verify(tmp):
    package_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(package_root / "src"))
    from sci_constants import set_sci_home_override, reset_sci_home_override, sci_home_key
    from sci_cli.plugins import discover_plugins, get_plugin_manager
    from tools.registry import registry
    from synthesis_route_gym.agent_runner import bind_executor

    homes = [tmp / name for name in ("a", "b")]
    for home in homes:
        home.mkdir()
        (home / "config.yaml").write_text("plugins:\n  enabled: [retrosynthesis]\n", encoding="utf-8")
        shutil.copytree(Path(__file__).parent, home / "plugins" / "retrosynthesis")
    checked = []
    for home in [homes[0], homes[1], homes[0]]:
        token = set_sci_home_override(home)
        try:
            discover_plugins()
            entry = registry.get_entry("srg_action", scope=sci_home_key())
            assert entry is not None, "Plugin was not discovered"
            with bind_executor(lambda action, arguments: {"profile": home.name, "action": action}):
                output = registry.dispatch("srg_action", {"action": "inspect"}, scope=sci_home_key())
            result = json.loads(output) if isinstance(output, str) else output
            assert result == {"profile": home.name, "action": "inspect"}
            checked.append(home.name)
        finally:
            reset_sci_home_override(token)
    for home in homes:
        token = set_sci_home_override(home)
        try:
            get_plugin_manager().unload()
        finally:
            reset_sci_home_override(token)
    print(json.dumps({"verified": True, "scopes": checked, "model_calls": 0}))


if __name__ == "__main__":
    main()
