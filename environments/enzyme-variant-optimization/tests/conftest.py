"""Portable environment fixtures; no profile, platform or development-tree access."""
import os
from pathlib import Path
import sys
import pytest

from enzyme_research.demo import fixture_task

ROOT = Path(__file__).resolve().parents[1]


def pytest_addoption(parser):
    parser.addoption("--native-support", help="Explicit source directory containing optional enzyme_environment/enzyme_benchmark modules")


def pytest_configure(config):
    source = config.getoption("--native-support")
    if source:
        source = Path(source).resolve()
        if not all((source / name).is_dir() for name in ("enzyme_environment", "enzyme_benchmark")):
            raise pytest.UsageError("--native-support must contain both optional host-support modules")
        sys.path.insert(0, str(source))


def pytest_ignore_collect(collection_path, config):
    if collection_path == ROOT / "tests" / "native" and not config.getoption("--native-support"):
        return True


@pytest.fixture
def task(tmp_path):
    return fixture_task(tmp_path)


@pytest.fixture
def store(tmp_path):
    from enzyme_research.store import Store
    return Store(tmp_path / "state")


@pytest.fixture
def campaign(store, task):
    return store.start(task, "specialist")


@pytest.fixture
def upstream():
    source = Path(os.environ.get("ENZYME_DISCOVERY_SOURCE", str(ROOT / ".runtime" / "DiscoveryRSI")))
    if not source.is_dir():
        pytest.fail("Run scripts/fetch_discovery.py or set ENZYME_DISCOVERY_SOURCE to the pinned checkout")
    return source
