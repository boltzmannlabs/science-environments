"""Lossless views of already-validated single-substitution candidates."""


def candidate_index(rows):
    return {"columns":["candidate_id","mutation"],"rows":[[row["candidate_id"],row["mutation"]] for row in rows]}


def compact_scores(result):
    """Lossless value matrix: every candidate, value and ledger field is retained."""
    return {**result,"row_columns":["candidate_id","predicted_score"],
        "rows":[[row["candidate_id"],row["predicted_score"]] for row in result["rows"]]}
