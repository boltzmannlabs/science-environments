"""Run every environment check (structure, config sync, README sync, benchmark
sync). Exit code 0 = environment valid. Usage: python3 scripts/validate_environment.py"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests"))
import env_lib  # noqa: E402
import test_structure  # noqa: E402
import test_config_sync  # noqa: E402
import test_readme_sync  # noqa: E402


def main():
    failures = []
    for mod, label in [
        (test_structure, "task-doc structure"),
        (test_config_sync, "config/benchmark sync"),
        (test_readme_sync, "README sync"),
    ]:
        errs = []
        for name in dir(mod):
            if name.startswith("test_"):
                try:
                    getattr(mod, name)()
                except AssertionError as exc:
                    errs.append(str(exc))
        status = "PASS" if not errs else "FAIL"
        print(f"[{status}] {label}")
        for e in errs:
            print(f"    {e}")
        failures.extend(errs)
    print(f"environment '{os.path.basename(env_lib.env_dir())}': "
          f"{'VALID' if not failures else f'{len(failures)} failure(s)'}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
