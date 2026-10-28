"""Synthetic fixtures only; held-out experimental outcomes are not exposed."""
import csv
from copy import deepcopy

import pytest

from synthesis_route_gym.condition_data import (
    load_condition_records, public_condition_records, summarize_condition_records,
    condition_source_metadata,
)


SOURCE_ID = "gauche_suzuki_miyaura"


def fixture_row(**updates):
    row = {
        "reactant_1_smiles": "Brc1ccccc1.CC", "reactant_2_smiles": "OB(O)c1ccccc1",
        "catalyst_smiles": "CC(=O)O~CC(=O)O~[Pd]", "ligand_smiles": "P",
        "reagent_1_smiles": "[OH-].[Na+]", "solvent_1_smiles": "CCO.O",
        "rxn": "Brc1ccccc1.CC.OB(O)c1ccccc1.CC(=O)O~CC(=O)O~[Pd].P.[OH-].[Na+].CCO.O>>c1ccc(-c2ccccc2)cc1",
        "yield": "42.5",
    }
    return {**row, **updates}


def write_csv(tmp_path, rows, name="fixture.csv"):
    path = tmp_path / name
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return path


def test_loader_preserves_source_roles_provenance_and_exposes_yield_only_to_private_records(tmp_path):
    records = load_condition_records(write_csv(tmp_path, [fixture_row()]), SOURCE_ID)
    record = records[0]
    assert record["outcome_yield_percent"] == 42.5
    assert len(record["reactants"]) == 3  # Source mixture is retained, not silently pruned.
    assert "CC" in record["reactants"]
    assert record["source_family"] == "doi:10.1126/science.aap9112"
    assert "data-row=1" in record["source_locator"]
    assert record["conditions"]["reagent_1"] == "[Na+].[OH-]"
    assert record["doyle_predictor_applicability"] == "outside_model_domain"
    assert record["source_input_roles"] == "reported_input_fields_not_atom_contribution_assignment"


def test_public_projection_is_allowlisted_deep_copied_and_independent_of_outcomes(tmp_path):
    records = load_condition_records(write_csv(tmp_path, [fixture_row()]), SOURCE_ID)
    changed = [{**record, "outcome_yield_percent": 90, "hidden_rank": 1} for record in records]
    public = public_condition_records(records)
    assert public_condition_records(changed) == public
    assert "outcome_yield_percent" not in public[0] and "hidden_rank" not in public[0]
    assert "source_locator" not in public[0]  # Exact label-bearing source lookup stays private.
    public[0]["conditions"]["ligand"] = "N"
    assert records[0]["conditions"]["ligand"] == "P"
    other = load_condition_records(write_csv(tmp_path, [fixture_row(**{"yield": "99"})], "other.csv"), SOURCE_ID)
    assert other[0]["record_id"] == records[0]["record_id"]


def test_empty_optional_source_cells_remain_explicitly_unspecified(tmp_path):
    row = fixture_row(ligand_smiles="", reagent_1_smiles="")
    row["rxn"] = "Brc1ccccc1.CC.OB(O)c1ccccc1.CC(=O)O~CC(=O)O~[Pd].CCO.O>>c1ccc(-c2ccccc2)cc1"
    record = load_condition_records(write_csv(tmp_path, [row]), SOURCE_ID)[0]
    assert "ligand" not in record["conditions"] and "reagent_1" not in record["conditions"]
    assert record["unspecified_condition_roles"] == ["ligand", "reagent_1"]
    assert record["missingness_scope"] == "empty_source_cell_does_not_distinguish_absent_from_unreported"


@pytest.mark.parametrize("bad", ["", "nan", "inf", "-1", "101", "outcome-secret"])
def test_invalid_outcomes_fail_without_echoing_hidden_value(tmp_path, bad):
    path = write_csv(tmp_path, [fixture_row(**{"yield": bad})])
    with pytest.raises(ValueError, match="outcome") as error:
        load_condition_records(path, SOURCE_ID)
    assert "outcome-secret" not in str(error.value)


@pytest.mark.parametrize("field,bad", [
    ("reactant_1_smiles", ""), ("reactant_2_smiles", "not-a-molecule"),
    ("catalyst_smiles", ""), ("solvent_1_smiles", ""),
    ("rxn", "CCO"), ("rxn", "CC>>bad-product"),
    ("rxn", "CC>>CC.O"), ("rxn", "CC>>"),
])
def test_invalid_or_ambiguous_structure_contracts_fail_closed(tmp_path, field, bad):
    path = write_csv(tmp_path, [fixture_row(**{field: bad})])
    with pytest.raises(ValueError):
        load_condition_records(path, SOURCE_ID)


def test_unknown_source_missing_schema_empty_dataset_and_role_mismatch_fail(tmp_path):
    path = write_csv(tmp_path, [fixture_row()])
    with pytest.raises(ValueError, match="source"):
        load_condition_records(path, "unknown_publication")
    missing = fixture_row()
    del missing["ligand_smiles"]
    with pytest.raises(ValueError, match="columns"):
        load_condition_records(write_csv(tmp_path, [missing], "missing.csv"), SOURCE_ID)
    path.write_text(",".join(fixture_row()) + "\n")
    with pytest.raises(ValueError, match="empty"):
        load_condition_records(path, SOURCE_ID)
    with pytest.raises(ValueError, match="input"):
        load_condition_records(write_csv(tmp_path, [fixture_row(ligand_smiles="N")], "mismatch.csv"), SOURCE_ID)


def test_summary_counts_independent_groups_without_exposing_outcomes(tmp_path):
    rows = [fixture_row(), fixture_row(**{"yield": "71"})]
    records = load_condition_records(write_csv(tmp_path, rows), SOURCE_ID)
    summary = summarize_condition_records(records)
    assert summary["record_count"] == 2
    assert summary["target_count"] == 1
    assert summary["product_scaffold_count"] == 1
    assert summary["source_family_count"] == 1
    assert summary["source_group_inference_supported"] is False
    assert summary["outcome_validity"] == {"valid_percent_count": 2, "invalid_percent_count": 0}
    assert "yield_values" not in summary and "best_condition" not in summary
    assert summary["duplicate_chemical_record_count"] == 1
    metadata = condition_source_metadata(SOURCE_ID)
    metadata["source_family"] = "changed"
    assert condition_source_metadata(SOURCE_ID)["source_family"] != "changed"


def test_summary_handles_invalid_supplied_private_values_without_printing_them(tmp_path):
    records = load_condition_records(write_csv(tmp_path, [fixture_row()]), SOURCE_ID)
    mutated = deepcopy(records)
    mutated[0]["outcome_yield_percent"] = float("nan")
    assert summarize_condition_records(mutated)["outcome_validity"]["invalid_percent_count"] == 1
    with pytest.raises(ValueError, match="nonempty"):
        summarize_condition_records([])


def test_malformed_csv_row_and_invalid_reaction_input_fail_closed(tmp_path):
    path = write_csv(tmp_path, [fixture_row()])
    with path.open("a") as handle:
        handle.write("too,few,columns\n")
    with pytest.raises(ValueError, match="columns"):
        load_condition_records(path, SOURCE_ID)
    path = write_csv(tmp_path, [fixture_row(rxn="not-a-molecule>>c1ccccc1")], "bad-reaction.csv")
    with pytest.raises(ValueError, match="reaction input"):
        load_condition_records(path, SOURCE_ID)
