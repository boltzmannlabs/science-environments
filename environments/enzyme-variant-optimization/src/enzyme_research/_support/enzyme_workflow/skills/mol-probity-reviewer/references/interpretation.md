# Structural-quality interpretation

Clashscore measures serious overlaps after hydrogen placement/optimization; use
localized atom pairs, not the score alone. Ramachandran evaluates backbone phi/psi;
rotamers evaluate side-chain conformations. C-beta deviations flag local
stereochemistry; CaBLAM uses C-alpha and peptide-plane geometry. Cis non-proline
and twisted peptides deserve local inspection. Bond-length/angle outliers compare
coordinates against chemistry restraints, not a catalytic mechanism.

Invalid file/chemistry → explicit preparation. Local side-chain defect → proposed
repack/minimize. Backbone defect → proposed remodeling/refolding. Widespread
defects → reject or broader reconstruction. After any repair recheck catalytic
roles, geometry and quality; catalytic strain cannot be automatically excused.

Hosted outputs: candidate_summary.csv, validation_outliers.csv,
invalid_candidates.csv, quality_thresholds_used.json, manifest.json and raw_json.
Compute is CPU only; no NFS weights. Read availability from the current catalogue;
a published contract and a successful worker run are separate evidence.
