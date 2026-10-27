import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from run_toy_ti import run

def test_toy_ti_reproduces_analytic_reference():
    result = run(20261027, n_samples=5000)
    assert result["effective_samples"] == 5000
    assert result["min_adjacent_overlap"] > 0.5
    assert result["absolute_error"] < 0.05
