"""Runtime configuration failures never install software or touch source."""
import json
from pathlib import Path

import pytest

from enzyme_environment.runtime import NativeRuntime, regular_file


def config(tmp_path):
    for name in ("agent","python/bin","deps","profile"):(tmp_path/name).mkdir(parents=True)
    (tmp_path/"agent/run_agent.py").write_text("# synthetic entry\n")
    (tmp_path/"python/bin/python3").symlink_to(tmp_path/"python/bin/real-python")
    (tmp_path/"python/bin/real-python").write_text("synthetic")
    value={"schema_version":"enzyme-native-runtime/1","agent_source":str(tmp_path/"agent"),"agent_revision":"a"*40,
        "python_root":str(tmp_path/"python"),"site_packages":str(tmp_path/"deps"),"profile":str(tmp_path/"profile"),
        "bubblewrap":"/usr/bin/true","limit_python":"/usr/bin/python3"}
    return value


def test_config_parses_without_importing_or_launching_the_sdk(tmp_path):
    value=config(tmp_path)
    path=tmp_path/"runtime.json"
    path.write_text(json.dumps(value))
    runtime=NativeRuntime.from_file(path)
    assert runtime.agent_revision=="a"*40 and runtime.agent_source==tmp_path/"agent"


@pytest.mark.parametrize("key,value",[("agent_revision","main"),("schema_version","next"),("secret","not allowed"),
    ("agent_source","relative"),("profile",False),("bubblewrap","relative"),("python_root","")])
def test_bad_runtime_configuration_rejected(tmp_path,key,value):
    payload=config(tmp_path)
    payload[key]=value
    path=tmp_path/"runtime.json"
    path.write_text(json.dumps(payload))
    with pytest.raises((ValueError,TypeError)):NativeRuntime.from_file(path)


def test_escaping_native_binary_and_symlink_config_rejected(tmp_path):
    payload=config(tmp_path)
    # Replace only this test's own symlink to exercise an escaping interpreter.
    path=tmp_path/"python/bin/python3"
    path.unlink()
    path.symlink_to("/usr/bin/python3")
    cfg=tmp_path/"runtime.json"
    cfg.write_text(json.dumps(payload))
    with pytest.raises(ValueError):NativeRuntime.from_file(cfg)
    alias=tmp_path/"alias.json"
    alias.symlink_to(cfg)
    with pytest.raises(ValueError):regular_file(alias)
