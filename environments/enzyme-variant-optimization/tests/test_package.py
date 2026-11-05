"""Package navigation/configuration checks, not scientific acceptance tests."""
import json
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parents[1]


class PackageTests(unittest.TestCase):
    def test_each_task_contains_the_full_workflow_and_antibody_style_sections(self):
        config = json.loads((ROOT / "config/workflow.json").read_text(encoding="utf-8"))
        sections = ["Description", "Target", "Design Constraints", "Computational Tool Capabilities",
                    "Evaluation Metrics", "Expected Output", "Important Instructions"]
        artifacts = ["RUN_PLAN.json", "candidates.fasta", "candidate_history.csv", "observations.csv",
                     "structure_evidence/", "decisions.md", "jobs.json", "usage.json",
                     "selection.csv", "selection_seal.json", "REPORT.md", "evaluation.json"]
        for task_id, path in config["tasks"].items():
            text = (ROOT / path).read_text(encoding="utf-8")
            with self.subTest(task=task_id):
                self.assertEqual(text.splitlines()[0], f"# Task: {task_id}")
                self.assertEqual(re.findall(r"^## (.+)$", text, re.MULTILINE), sections)
                capabilities = text.split("## Computational Tool Capabilities\n", 1)[1].split("## Evaluation Metrics\n", 1)[0]
                self.assertIn("| Stage | Capability | Expected Evidence |", capabilities)
                self.assertEqual([int(n) for n in re.findall(r"^\| ([0-9]+)\. ", capabilities, re.MULTILINE)],
                                 list(range(1, len(config["stages"]) + 1)))
                self.assertIn("| Criterion | Measurements and Evidence | Evaluation Rule |", text)
                output = text.split("## Expected Output\n", 1)[1].split("## Important Instructions\n", 1)[0]
                for artifact in artifacts:
                    self.assertIn(f"`{artifact}`", output)

    def test_task_execution_limits_agree_with_shared_configuration(self):
        config = json.loads((ROOT / "config/workflow.json").read_text(encoding="utf-8"))
        limits = config["starting_limits_per_approach"]
        labels = {"Maximum unique sequences including parent": "unique_sequences_including_parent",
                  "Maximum substitutions per variant": "maximum_substitutions_per_variant",
                  "Maximum scientific submission attempts": "scientific_submission_attempts",
                  "Maximum final candidates": "final_candidates_maximum"}
        for task_id, path in config["tasks"].items():
            text = (ROOT / path).read_text(encoding="utf-8")
            with self.subTest(task=task_id):
                for label, key in labels.items():
                    match = re.search(r"^\| " + re.escape(label) + r" \| ([0-9]+) \|$", text, re.MULTILINE)
                    self.assertIsNotNone(match, label)
                    self.assertEqual(int(match.group(1)), limits[key])
                revisions = re.search(r"^\| Sequence revision rounds \| .*maximum ([0-9]+)\. \|$", text, re.MULTILINE)
                self.assertIsNotNone(revisions)
                self.assertEqual(int(revisions.group(1)), limits["sequence_revision_rounds"])

    def test_catalog_paths_and_required_structure_are_real(self):
        config = json.loads((ROOT / "config/workflow.json").read_text(encoding="utf-8"))
        self.assertTrue(config["generation_requires_executed_tool"])
        self.assertEqual(len(config["tasks"]), 5)
        self.assertEqual(set(config["providers"]), {"boltzmann", "tooluniverse"})
        for path in config["tasks"].values():
            self.assertTrue((ROOT / path).is_file(), path)
        for name in ("README.md", "ENVIRONMENT_SPEC.md", "STATUS.md", "MODELS_AND_TOOLS.md"):
            self.assertTrue((ROOT / name).is_file(), name)
        for name in ("config", "tasks", "tests", "scripts", "src", "benchmark", "results"):
            self.assertTrue(any(p.is_file() for p in (ROOT / name).rglob("*")), name)

    def test_local_documentation_links_resolve_and_specialists_are_not_bundled(self):
        research = REPOSITORY / "research/enzyme-variant-optimization"
        for document in [*ROOT.rglob("*.md"), *research.rglob("*.md")]:
            for raw in re.findall(r"\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
                url = urlsplit(raw)
                if url.scheme or not url.path:
                    continue
                with self.subTest(document=document, link=raw):
                    self.assertTrue((document.parent / unquote(url.path)).exists(), raw)
        self.assertFalse((ROOT / "specialist").exists())
        self.assertFalse((ROOT / "specialists").exists())
        self.assertFalse((ROOT / "subagents").exists())


if __name__ == "__main__":
    unittest.main()
