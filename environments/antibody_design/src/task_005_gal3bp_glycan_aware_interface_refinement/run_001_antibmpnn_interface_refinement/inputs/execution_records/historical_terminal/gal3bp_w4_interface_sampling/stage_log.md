# W4 interface sampling
Input: ref_rank1_clean.pdb + the 5 AFM reference models (outputs_afm zip).
Tools: w4_interface_sampling.py (local); Protenix base 3 seeds x 5 samples with real MSAs (GPU RTX 3090, 4m19s).
Headline: 0/130 reference contact pairs persist >=3/5 models (RMSD 18-28 A); Protenix iptm 0.146-0.166 with no pair shared by >1 sample — three independent engines agree the borrowed-scaffold interface is not reproducible at predictor level.