"""Copy the standalone plugin to an explicit destination; never edit host config."""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil


def install(destination: Path) -> Path:
    source = Path(__file__).resolve().parents[1] / "src" / "leadopt_env"
    destination = destination.expanduser().absolute()
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f"Refusing to replace existing destination: {destination}")
    if destination == source or source in destination.parents:
        raise ValueError("Destination must be outside the source package")
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, required=True,
                        help="Explicit plugin directory, normally SCI_HOME/plugins/leadopt_env")
    args = parser.parse_args()
    try:
        destination = install(args.destination)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"{exc}\n")
    print(f"Copied plugin to {destination}")
    print("No Agent-Scientist settings were changed. Enable it with the host's plugin controls, "
          "set an absolute db_path in its settings, then start a new session.")


if __name__ == "__main__":
    main()
