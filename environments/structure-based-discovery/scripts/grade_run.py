"""Grade one completed run. Usage: python3 scripts/grade_run.py task_006 results/task_006/run1"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import env_lib  # noqa: E402

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    ok = env_lib.grade_run(sys.argv[1], sys.argv[2])
    sys.exit(0 if ok else 1)
