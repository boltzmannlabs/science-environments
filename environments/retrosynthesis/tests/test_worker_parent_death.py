"""Linux kernel parent-death cleanup precedes heavy model imports."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import pytest
from synthesis_route_gym.adapters import common

pytestmark=pytest.mark.skipif(not sys.platform.startswith('linux'),reason='Linux PR_SET_PDEATHSIG contract')


def alive(pid):
    try:return Path(f'/proc/{pid}/stat').read_text().split()[2]!='Z'
    except FileNotFoundError:return False


def test_backend_dies_when_owning_host_dies_and_sentinel_survives(tmp_path):
    marker=tmp_path/'worker.json';worker=tmp_path/'_worker.py'
    worker.write_text('import json,os,time\nfrom pathlib import Path\nPath('+repr(str(marker))+').write_text(json.dumps([os.getpid(),os.getpgrp()]))\ntime.sleep(30)\n')
    parent_code=('import os,subprocess,sys,time; '
        'subprocess.Popen([sys.executable,"-c",'+repr(common.WORKER_BOOTSTRAP)+','+
        repr(str(worker))+',str(os.getpid())],start_new_session=True); time.sleep(30)')
    sentinel=subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)'])
    parent=subprocess.Popen([sys.executable,'-c',parent_code])
    pid=None
    try:
        end=time.monotonic()+10
        while not marker.exists() and time.monotonic()<end:time.sleep(.02)
        assert marker.exists(),'Worker startup did not reach safe bootstrap'
        pid,group=json.loads(marker.read_text());assert pid==group
        parent.kill();parent.wait(timeout=5)
        end=time.monotonic()+5
        while alive(pid) and time.monotonic()<end:time.sleep(.02)
        assert not alive(pid)
        assert sentinel.poll() is None
    finally:
        if parent.poll() is None:parent.kill()
        parent.wait()
        sentinel.terminate();sentinel.wait()
        if pid and alive(pid):os.killpg(pid,signal.SIGKILL)


def test_dead_parent_race_is_checked_before_scientific_code(tmp_path):
    marker=tmp_path/'must-not-exist';worker=tmp_path/'_worker.py'
    worker.write_text('from pathlib import Path\nPath('+repr(str(marker))+').touch()\n')
    result=subprocess.run([sys.executable,'-c',common.WORKER_BOOTSTRAP,str(worker),'0'],
        start_new_session=True,capture_output=True,timeout=10)
    assert result.returncode == -signal.SIGKILL
    assert not marker.exists()
