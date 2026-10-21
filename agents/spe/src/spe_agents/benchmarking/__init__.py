"""Controlled comparison framework for SPE decision policies."""

from .dataset import BenchmarkDataset, load_dataset
from .evaluator import BenchmarkEvaluator, EvaluationBundle, ReferenceStore
from .models import (
    Approach,
    BenchmarkBudget,
    BenchmarkCase,
    CaseExpectation,
    CaseRun,
    Decision,
    DecisionAction,
    Split,
)
from .policies import (
    AgentScientistPolicy,
    CommandDecisionProvider,
    FixedWorkflowPolicy,
    SpecialistAssistedPolicy,
)
from .runner import BenchmarkRunner, LocalSubprocessBackend

__all__ = [
    "AgentScientistPolicy",
    "Approach",
    "BenchmarkBudget",
    "BenchmarkCase",
    "BenchmarkDataset",
    "BenchmarkEvaluator",
    "BenchmarkRunner",
    "CaseExpectation",
    "CaseRun",
    "CommandDecisionProvider",
    "Decision",
    "DecisionAction",
    "EvaluationBundle",
    "FixedWorkflowPolicy",
    "LocalSubprocessBackend",
    "ReferenceStore",
    "SpecialistAssistedPolicy",
    "Split",
    "load_dataset",
]
