"""Environment ownership and portable shared-runner contracts."""
from pathlib import Path
import importlib
import json
import os
import subprocess
import sys
import tempfile
import unittest

ENV = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ENV / 'src'))


class StructureTests(unittest.TestCase):
    def test_required_environment_layout(self):
        root_files = {p.name for p in ENV.iterdir() if p.is_file()}
        self.assertEqual(root_files, {'README.md', 'pyproject.toml', 'requirements.txt', '.gitignore', '.gitattributes'})
        for name in ['config', 'docs', 'tasks', 'tests', 'scripts', 'src', 'benchmark', 'results']:
            self.assertTrue((ENV / name / 'README.md').is_file(), name)
        for name in ['ENVIRONMENT_SPEC.md', 'STATUS.md', 'MODELS_AND_TOOLS.md', 'TASK_STRUCTURE.md', 'THIRD_PARTY_NOTICES.md']:
            self.assertTrue((ENV / 'docs/shared' / name).is_file(), name)

    def test_registered_tasks_own_all_sections(self):
        tasks = json.loads((ENV / 'config/shared/tasks.json').read_text())['tasks']
        self.assertIn('Task - 01', tasks)
        self.assertIn('Task - 02', tasks)
        sections = [('task_dir', 'tasks'), ('benchmark_dir', 'benchmark'), ('results_dir', 'results'),
                    ('config_dir', 'config'), ('docs_dir', 'docs'), ('script_dir', 'scripts')]
        slugs, packages = set(), set()
        for task_id, task in tasks.items():
            with self.subTest(task_id=task_id):
                number = int(task_id.removeprefix('Task - '))
                slug = task['folder_slug']
                self.assertRegex(slug, rf'^task-{number:02d}-[a-z0-9]+(?:-[a-z0-9]+)*$')
                self.assertNotIn(slug, slugs)
                slugs.add(slug)
                package = slug.replace('-', '_')
                packages.add(package)
                self.assertEqual(task['python_package'], package)
                for key, section in sections:
                    self.assertEqual(task[key], f'{section}/{slug}')
                self.assertEqual(task['source_dir'], f'src/formulation_environment/{package}')
                self.assertEqual(task['test_dir'], f'tests/{package}')
                for key in [key for key, _ in sections] + ['source_dir', 'test_dir']:
                    self.assertTrue((ENV / task[key] / 'README.md').is_file(), key)
                module, function = task['entrypoint'].split(':')
                self.assertEqual(module, f'formulation_environment.{package}')
                self.assertTrue(callable(getattr(importlib.import_module(module), function)))
        expected = {section: slugs for _, section in sections}
        expected.update({section: slugs | {'shared'} for section in ['config', 'docs', 'scripts']})
        expected['tests'] = packages | {'shared'}
        expected['src/formulation_environment'] = packages
        for section, folders in expected.items():
            directory = ENV / section
            actual = {p.name for p in directory.iterdir() if p.is_dir() and p.name != '__pycache__'}
            self.assertEqual(actual, folders, section)
            allowed = {'README.md', '__init__.py'} if section == 'src/formulation_environment' else {'README.md'}
            self.assertFalse([p.name for p in directory.iterdir() if p.is_file() and p.name not in allowed], section)

    def test_shared_runner_is_portable_and_rejects_unknown_tasks(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, str(ENV / 'scripts/shared/run_task.py'), '--task', 'unknown', '--out', str(Path(directory) / 'run')], cwd=directory, env={**os.environ, 'PYTHONPATH': ''}, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Unknown task', result.stderr)
            self.assertFalse((Path(directory) / 'run').exists())
