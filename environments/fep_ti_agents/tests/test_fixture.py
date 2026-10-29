import json
from pathlib import Path
def test_fixture_is_explicitly_incomplete_on_overlap():
    case=json.loads((Path(__file__).parents[1]/'cases/fixture.json').read_text())
    assert case['provenance_complete'] is True
    assert case['overlap_available'] is False
