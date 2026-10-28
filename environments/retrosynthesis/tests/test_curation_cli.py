import hashlib
import json

import pytest

from synthesis_route_gym.curation_cli import curate_from_config, main
from synthesis_route_gym.route_data import parse_paroutes_record


def setup_config(tmp_path):
    rows = []
    for index, target in enumerate(["CC", "CO", "CN"]):
        tree = {"type": "mol", "smiles": target, "children": [{"type": "reaction",
                "metadata": {"patent_id": f"doc{index}"}, "children": [
                    {"type": "mol", "smiles": "C"}, {"type": "mol", "smiles": "O"}]}]}
        row = parse_paroutes_record(tree, "synthetic", index)
        rows.append(row)
    paths = {"routes": tmp_path / "routes.json", "stock": tmp_path / "stock.txt",
             "fresh_conditions": tmp_path / "fresh.csv", "seen_doyle": tmp_path / "seen.csv"}
    paths["routes"].write_text(json.dumps(rows))
    paths["stock"].write_text("C\nO\nN\n")
    paths["fresh_conditions"].write_text('reactant_1_smiles,reactant_2_smiles,catalyst_smiles,ligand_smiles,reagent_1_smiles,solvent_1_smiles,rxn,yield\nC,Cl,[Pd],N,O,CCO,C.Cl.[Pd].N.O.CCO>>CCl,25\n')
    paths["seen_doyle"].write_text('aryl halide,ligand,additive,base,rxn,yield\nCBr,N,O,O,CBr.N>>CCBr,42\n')
    config = {"schema_version": "1.0", "seed": "test", "quotas": {"smoke": 1, "development": 1, "sealed_final": 1},
              "inputs": {key: {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                         for key, path in paths.items()},
              "provenance": {"sources": [{"source_id": key, "url": f"https://example.org/{key}",
                             "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "license": "synthetic-test"}
                            for key, path in paths.items()]}}
    p = tmp_path / "config.json"
    p.write_text(json.dumps(config))
    return p, paths


def test_curation_cli_complete_bundle_and_reports(tmp_path, capsys):
    config, _ = setup_config(tmp_path)
    result = main(["--config", str(config), "--public-output", str(tmp_path / "public"),
                   "--private-output", str(tmp_path / "private"), "--report-output", str(tmp_path / "report")])
    assert result == 0
    report = json.loads((tmp_path / "report/curation.json").read_text())
    assert report["route_targets"] == 3
    assert report["final_run_authorized"] is False
    assert (tmp_path / "private/assignments.json").is_file()
    output = capsys.readouterr().out
    assert "outcome" not in output and "CCl" not in output
    assert main(["--config", str(config), "--public-output", str(tmp_path / "public"),
                 "--private-output", str(tmp_path / "private"), "--report-output", str(tmp_path / "report")]) == 1


def test_input_hash_change_rejected_before_outputs(tmp_path):
    config, paths = setup_config(tmp_path)
    paths["stock"].write_text("C\n")
    with pytest.raises(ValueError, match="hash"):
        curate_from_config(config, tmp_path / "public", tmp_path / "private", tmp_path / "report")
    assert not (tmp_path / "public").exists()
    assert not (tmp_path / "report").exists()
