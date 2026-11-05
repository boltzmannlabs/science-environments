"""Environment README indexes every task with correct paper links. Standalone or pytest."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import env_lib  # noqa: E402


def test_readme_indexes_every_task_and_paper():
    readme = open(os.path.join(env_lib.env_dir(), "README.md"), encoding="utf-8").read()
    for fname in env_lib.task_files():
        parsed = env_lib.parse_task(os.path.join(env_lib.tasks_dir(), fname))
        assert f"tasks/{fname}" in readme, f"README missing link to {fname}"
        if parsed["pmc"]:
            assert parsed["pmc"] in readme, f"README missing {parsed['pmc']}"
        if parsed["doi"]:
            assert parsed["doi"].replace("https://doi.org/", "") in readme, \
                f"README missing DOI for {fname}"


def test_root_readme_counts():
    root_path = os.path.join(os.path.dirname(env_lib.env_dir()), os.pardir, "README.md")
    root_path = os.path.normpath(root_path)
    root = open(root_path, encoding="utf-8").read()
    name = os.path.basename(env_lib.env_dir())
    assert f"environments/{name}/README.md" in root, \
        f"root README should link to the {name} environment"
    if f"| [{name}](environments/{name}/) |" in root:
        rows = [line for line in root.splitlines()
                if line.startswith(f"| [{name}](environments/{name}/) |")]
        assert len(rows) == 1, f"root README duplicates {name}"
        assert rows[0].split("|")[-2].strip() == str(len(env_lib.task_files())), \
            f"root README count differs from {name} task files"


if __name__ == "__main__":
    for name in [n for n in dir() if n.startswith("test_")]:
        getattr(sys.modules[__name__], name)()
        print(f"ok: {name}")
