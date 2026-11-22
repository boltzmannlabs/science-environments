# Residue-level MolProbity geometry review

Source: measurement-only validation_outliers.csv and candidate_summary.csv in the two bundled archives. Counts are validator records, not unique residues. An event is counted as touching H3 if any reported atom or clash partner involves chain A residues 97–110 (PDB numbering; no insertion code). Counts per chain or residue can overlap; top-residue parentheses are incident-record counts. For omega records, both previous and current residues are included. CaBLAM and omega records can include disfavored/nontrans entries, not only the candidate-summary outlier count. No pass/fail cutoffs were applied.

| Rank | Bond outliers touching H3 / total | Angle outliers touching H3 / total | Clash records touching H3 / total | Ramachandran outliers touching H3 / total |
|---:|---:|---:|---:|---:|
| 1 | 6 / 156 | 13 / 130 | 28 / 350 | 1 / 11 |
| 2 | 9 / 155 | 10 / 142 | 27 / 269 | 0 / 7 |
| 3 | 8 / 117 | 7 / 100 | 98 / 357 | 2 / 10 |
| 4 | 10 / 163 | 7 / 95 | 23 / 223 | 0 / 6 |
| 5 | 9 / 144 | 14 / 128 | 34 / 308 | 1 / 11 |

## H3-localized hotspots

Rank 1:
- bonds: A:101 (3), A:102 (2), A:103 (2), A:100 (1), A:104 (1)
- angles: A:104 (5), A:101 (4), A:105 (4), A:106 (4), A:103 (3)
- clashscore2: A:102 (13), A:101 (7), A:105 (6), A:108 (1), A:99 (1)
- ramalyze: A:102 (1)
Rank 2:
- bonds: A:103 (4), A:100 (2), A:101 (2), A:99 (2), A:102 (1)
- angles: A:106 (4), A:107 (4), A:100 (3), A:101 (3), A:104 (3)
- clashscore2: A:104 (6), A:103 (5), A:107 (4), A:102 (4), A:108 (3)
- ramalyze: none
Rank 3:
- bonds: A:101 (3), A:106 (2), A:102 (1), A:105 (1), A:107 (1)
- angles: A:101 (4), A:100 (3), A:105 (2), A:102 (1), A:104 (1)
- clashscore2: A:102 (40), A:101 (23), A:103 (21), A:105 (7), A:100 (4)
- ramalyze: A:101 (1), A:103 (1)
Rank 4:
- bonds: A:102 (3), A:101 (2), A:107 (2), A:98 (2), A:103 (1)
- angles: A:105 (6), A:104 (3), A:106 (3), A:108 (1), A:109 (1)
- clashscore2: A:102 (5), A:109 (4), A:101 (4), A:103 (3), A:107 (3)
- ramalyze: none
Rank 5:
- bonds: A:100 (2), A:101 (2), A:102 (2), A:103 (2), A:99 (2)
- angles: A:101 (5), A:100 (4), A:102 (4), A:103 (4), A:104 (3)
- clashscore2: A:100 (13), A:109 (11), A:102 (11), A:101 (2), A:104 (2)
- ramalyze: A:101 (1)

## Interpretation and boundaries

The records identify locations for manual structural review, not automatic repair instructions. Bond/angle flags and clashes occur in unrelaxed coordinates; no minimization, remediation, re-prediction, or post-repair validation was performed. Geometry problems are not evidence of experimental nonbinding, and correcting geometry would not establish the native interface or affinity. Rank 1 provenance is based on the user-supplied output filename and matching atom/residue counts; the output lacks an input-coordinate checksum. Ranks 2–5 cross-file inventory validation was partial due to the receipt-size limit.

Full chain and residue incidence counts: geometry_review_counts.csv. Detailed atom identities and score definitions are in the bundled MolProbity ZIP files.
