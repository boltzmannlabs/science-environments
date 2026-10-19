"""Lossless views of already-validated single-substitution candidates."""


def candidate_index(rows):
    return {"columns":["candidate_id","mutation"],"rows":[[row["candidate_id"],row["mutation"]] for row in rows]}
