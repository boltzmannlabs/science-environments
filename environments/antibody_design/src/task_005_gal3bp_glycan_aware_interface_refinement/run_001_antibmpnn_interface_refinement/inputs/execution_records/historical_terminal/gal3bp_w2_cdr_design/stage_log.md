# W2 CDR design
Input: ref_rank1_clean.pdb (AFM rank_001 ternary).
Tool: AntiBMPNN doc 6af89b4ed29658acc304eef4 (chains A,B designed; masks A:27-38,56-65,105-119 / B:27-38,55-61,105-106; antigen C fixed; 20 generations). First attempt 6af8999b9030bff4164485c2 validation_failed (mask position 113 > VL length 106; masks rebuilt from non-gap ANARCI indices).
Outputs: outputs/candidate_designs.json (19 unique of 20; scores 0.336-0.400) + native zip.