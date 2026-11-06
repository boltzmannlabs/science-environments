"""Ensure invalid input bundles cannot pass the static environment validator."""
import csv
import shutil
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from validate_environment import ROOT,validate

def test_current_bundle():
    assert validate()==[]

def test_changed_molecular_input_is_rejected(tmp_path):
    copied=tmp_path/'env';shutil.copytree(ROOT,copied)
    library=copied/'inputs/library/compounds_400.csv'
    with library.open() as f:rows=list(csv.DictReader(f));fields=list(rows[0])
    rows[0]['smiles']='CC'
    with library.open('w') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
    errors=validate(copied)
    assert any('checksum mismatch' in x for x in errors)
    assert any('CSV/SDF identity metadata mismatch' in x for x in errors)

def test_missing_reference_is_rejected(tmp_path):
    copied=tmp_path/'env';shutil.copytree(ROOT,copied)
    (copied/'inputs/controls/domperidone_pubchem_3151.sdf').unlink()
    errors=validate(copied)
    assert any('Missing registered input' in x for x in errors)
