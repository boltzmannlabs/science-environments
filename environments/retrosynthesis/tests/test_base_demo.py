"""The exported base example exercises an offline synthetic route end to end."""
import importlib.util
import json
from pathlib import Path


def test_base_demo_imports_checks_ranks_and_submits_without_external_assets(capsys):
    path=Path(__file__).parents[1]/'examples/base_demo.py'
    spec=importlib.util.spec_from_file_location('base_demo',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    assert module.main()==0
    output=json.loads(capsys.readouterr().out)
    assert output['example_kind']=='synthetic_software_demo'
    assert output['claims_experimental_validation'] is False
    assert output['submission']['status']=='ok'
    assert output['submission']['result']['accepted_route_ids']==['synthetic-fixture']
    assert output['import']['evidence_status']=='predicted'
