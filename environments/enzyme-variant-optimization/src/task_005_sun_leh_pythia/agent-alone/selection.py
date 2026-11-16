"""Deterministic, nonself per-position selection on already executed score rows."""
def select(rows, score_column, cutoff):
    best = {}
    for row in rows:
        if row['mutant'] == row['wildtype']:
            continue
        key = (row['chain'], int(row['position']))
        order = (float(row[score_column]), row['mutant'])
        if key not in best or order < (float(best[key][score_column]), best[key]['mutant']):
            best[key] = row
    ranked = sorted(best.values(), key=lambda row: (float(row[score_column]), row['chain'], int(row['position']), row['mutant']))
    return ranked, [row for row in ranked if float(row[score_column]) < cutoff]
