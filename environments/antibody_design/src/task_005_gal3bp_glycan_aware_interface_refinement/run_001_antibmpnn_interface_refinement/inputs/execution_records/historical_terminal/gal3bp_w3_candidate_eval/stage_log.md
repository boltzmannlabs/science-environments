# W3 matched candidate evaluation
Inputs: payload_G3BPD-{14,04,17}.txt (programmatic, sha256-verified 122/106/567 segments), candidates_all.fasta.
Tools: Multimer_Structure_Prediction docs 6af89d409850a93adf67dbf3 (G3BPD-14), 6af89d539030bff41644864d (G3BPD-04), 6af8a897445ae94313c3cfa6 (G3BPD-17); interface_chemistry.py; Prodigy; glycan_dsasa.py; candidate_persistence.py; ANARCI.
Verification: every downloaded model's VH/VL byte-verified vs candidate_designs.json.
Headline: iptm 0.68/0.66/0.56 vs ref 0.32; glycan dSASA 222.2/217.2/217.5 A2 (0 clashes); 0 rank-1 pairs persist >=3/5 models; Prodigy -8.7/-8.7/-8.6. Voided submissions listed in outputs/w3_job_registry.json.