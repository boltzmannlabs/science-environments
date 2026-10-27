"""Native six-column ThermoMPNN table compatibility; no remote calls."""
import csv, io
from pathlib import Path
import pytest
from enzyme_research.stability import parse_output
from enzyme_research.contracts import ResearchError
from test_stability_handoff import layout, table


def write_native(path, rows, *, chain=False):
    fields=['Model','Dataset','ddG_pred','position','wildtype','mutation']+(['chain'] if chain else [])
    stream=io.StringIO(newline='');writer=csv.DictWriter(stream,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(rows)
    path.write_bytes(stream.getvalue().encode())
    return path


def test_six_column_native_grid_uses_exact_verified_input_chain(layout,tmp_path):
    path=write_native(tmp_path/'parent.csv',table({'parent':layout}))
    original=path.read_bytes()
    matrix=parse_output(path,{'parent':layout})['parent']
    assert len(matrix['predictions'])==200
    assert matrix['input_layout']['pdb_sha256']==layout['pdb_sha256']
    assert {p['chain'] for p in matrix['predictions']}=={'A'}
    assert {p['chain_metadata_source'] for p in matrix['predictions']}=={'verified_input_layout'}
    assert path.read_bytes()==original


def test_optional_output_chain_is_checked_not_replaced(layout,tmp_path):
    rows=table({'parent':layout});rows[0]['chain']='B'
    path=write_native(tmp_path/'wrong_chain.csv',rows,chain=True)
    with pytest.raises(ResearchError,match='model/Dataset/chain'):
        parse_output(path,{'parent':layout})


def test_native_grid_still_rejects_wrong_dataset(layout,tmp_path):
    rows=table({'parent':layout});rows[0]['Dataset']='other'
    path=write_native(tmp_path/'wrong_dataset.csv',rows)
    with pytest.raises(ResearchError,match='model/Dataset/chain'):
        parse_output(path,{'parent':layout})
