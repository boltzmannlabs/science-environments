"""Structural validity of every task document. Runnable standalone
(python3 tests/test_structure.py) or under pytest."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import env_lib  # noqa: E402


def test_every_task_doc_has_valid_structure():
    files = env_lib.task_files()
    assert files, "no task documents found"
    errors = []
    for fname in files:
        parsed = env_lib.parse_task(os.path.join(env_lib.tasks_dir(), fname))
        errors.extend(env_lib.check_structure(parsed))
    assert not errors, "\n".join(errors)


def test_task_files_use_canonical_naming():
    import re
    for fname in env_lib.task_files():
        assert re.match(r"^task_\d{3}_[a-z0-9_]+\.md$", fname), fname
    ids = [f[5:8] for f in env_lib.task_files()]
    assert ids == [f"{i:03d}" for i in range(1, len(ids) + 1)], ids


if __name__ == "__main__":
    for name in [n for n in dir() if n.startswith("test_")]:
        getattr(sys.modules[__name__], name)()
        print(f"ok: {name}")
