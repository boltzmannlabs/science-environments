# task_007_huj3_gp120_fixed_framework_design — Results

**Task ID:** `task_007_huj3_gp120_fixed_framework_design`
**Run:** `run_20261109_001`
**Published comparison:** Sun et al., *Advanced Science* (2025), DOI: 10.1002/advs.202504278.

## 1. End-to-end workflow and actual execution

| Step | Intended/published approach | What was actually done |
|---|---|---|
| Parent and antigen | huJ3 VHH against C1086 gp120 | Used the supplied huJ3 sequence and mapped gp120 from PDB 7RI1; the 7RI1 antibody was not substituted for huJ3 |
| Frozen design backbone | Structure-matched huJ3 framework | Predicted the huJ3 monomer with Boltz-2 and held its backbone fixed for sequence design |
| Separate design masks | CDR1 positions 26–33; CDR3 positions 97, 101, 103–106 | Kept the unmasked sequence fixed, including CDR3 positions 98–100 |
| CDR1 sequence generation | AntiBMPNN | AntiBMPNN structure-conditioned sequence design |
| CDR3 sequence generation | AntiBMPNN in the paper | ProteinMPNN structure-conditioned sequence design |
| Design validity and deduplication | Protect framework, check length and unique variants | Checked full sequence lengths and masked-position changes; preserved parent outside the masks |
| Sequence frequency | Group identical generated sequences | Counted CDR1 sequence occurrences and identified unique CDR3 samples |
| Three physicochemical properties | PD1_volume, PD2_hydro, PD3_charge at pH 7.4 | Ran `peptides==0.5.0` on the parent and every saved CDR1/CDR3 sequence, separately for CDR1 (26–33) and full CDR3 (94–110) |
| Candidate selection | Select eligible designs before structural testing | Existing structural shortlist was carried forward from the historical run; it was not reselected using the newly computed PD values |
| Monomer structure assessment | AF3 pLDDT in the paper | Boltz-2 monomer confidence for the parent and available shortlisted candidates |
| Antibody–gp120 complex assessment | AF3 `ranking_score` in the paper | Boltz-2 complex `ipTM` and `pTM` on assessed candidates |

The parent CDR1 segment is `GSIFNQYA`; the parent full CDR3 segment is `ARSKSTYISYNSNGYDY`. The new PD values are peptide-sequence descriptors. Their scale differs from the original run's Bondi-volume and negative Kyte–Doolittle calculations; the original charge fields also had an identified implementation error. The original structural shortlist is historical and must not be described as selected with the new PD values.

## 2. Generated sequences and published design comparison

| Case | Published example | Our result |
|---|---|---|
| CDR1 | Lead 1-V1 changes I28R, N30D and Q31G | Four unique AntiBMPNN CDR1 sequences; top-frequency segment `GFTFSDYA` (83.5%) |
| CDR3 | Top cluster `ARSKSTYLSRDSSGYDY` (94–110), 6,495/32,768 occurrences | ProteinMPNN CDR3 sequences were unique in the saved pool; assessed `s044` has `ARSKSTYISYDQSGYDY`, a different sequence |

| Our CDR1 candidate | CDR1 segment | Sampling frequency |
|---|---|---:|
| `cdr1_antibmpnn_u01` | `GFTFSDYA` | 83.5% |
| `cdr1_antibmpnn_u02` | `GFTFSNYA` | 11.5% |
| `cdr1_antibmpnn_u04` | `GFTFSSYA` | 4.5% |
| `cdr1_antibmpnn_u03` | `GFTFSTYA` | 0.5% |

Full-length sequences for the frequency leader and the highest-ipTM assessed variants:

| Candidate | Selection basis | Full-length VHH sequence |
|---|---|---|
| `cdr1_antibmpnn_u01` | CDR1 frequency leader | `EVQLVESGGGLVQPGGSLRLSCAASGFTFSDYAMAWFRQAPGKEREFVAGMGAVPHYGEFVKGRFTISRDNSKNTVYLQMNSLRAEDTAVYYCARSKSTYISYNSNGYDYWGQGTLVTVSS` |
| `cdr1_antibmpnn_u03` | Highest CDR1 ipTM among assessed candidates | `EVQLVESGGGLVQPGGSLRLSCAASGFTFSTYAMAWFRQAPGKEREFVAGMGAVPHYGEFVKGRFTISRDNSKNTVYLQMNSLRAEDTAVYYCARSKSTYISYNSNGYDYWGQGTLVTVSS` |
| `cdr3_pmnn_s044` | Highest CDR3 ipTM among assessed candidates | `EVQLVESGGGLVQPGGSLRLSCAASGSIFNQYAMAWFRQAPGKEREFVAGMGAVPHYGEFVKGRFTISRDNSKNTVYLQMNSLRAEDTAVYYCARSKSTYISYDQSGYDYWGQGTLVTVSS` |

## 3. Physicochemical descriptors: our candidate versus our parent

PD1_volume and PD2_hydro are the `peptides` physical-descriptor components. PD3_charge is the calculated peptide-segment charge at pH 7.4 (elementary-charge units). Each parent-versus-candidate difference uses the same method and segment boundary. Δ denotes candidate minus parent, computed from displayed four-decimal values.

| CDR1 (26–33) | PD1 (Δ) | PD2 (Δ) | PD3, pH 7.4 (Δ) |
|---|---:|---:|---:|
| Parent `GSIFNQYA` | −0.5175 | −0.2162 | −0.0072 |
| `GFTFSDYA` / `u01` | −0.5275 (−0.0100) | −0.2812 (−0.0650) | −1.0070 (−0.9998) |
| `GFTFSNYA` / `u02` | −0.4975 (+0.0200) | −0.3362 (−0.1200) | −0.0072 (+0.0000) |
| `GFTFSSYA` / `u04` | −0.7075 (−0.1900) | −0.3875 (−0.1713) | −0.0072 (+0.0000) |
| `GFTFSTYA` / `u03` | −0.5612 (−0.0437) | −0.4000 (−0.1838) | −0.0072 (+0.0000) |

| Full CDR3 (94–110) | PD1 (Δ) | PD2 (Δ) | PD3, pH 7.4 (Δ) |
|---|---:|---:|---:|
| Parent `ARSKSTYISYNSNGYDY` | −0.2947 | +0.2406 | +0.9858 |
| `ARSRSTYISKTDTGYDY` / `s021` | −0.2900 (+0.0047) | +0.3182 (+0.0776) | +0.9881 (+0.0023) |
| `ARSKSTYISYDQSGYDY` / `s044` | −0.2476 (+0.0471) | +0.2841 (+0.0435) | −0.0140 (−0.9998) |
| `ARSSSTYISNYMDGYDY` / `s056` | −0.3088 (−0.0141) | +0.1106 (−0.1300) | −1.0133 (−1.9991) |
| `ARSYSTYISKEDSGYDY` / `s059` | −0.2594 (+0.0353) | +0.2953 (+0.0547) | −1.0133 (−1.9991) |

The paper's Figure 2c reports −0.4271, +0.3253, +0.9881 for its top CDR3 segment `ARSKSTYLSRDSSGYDY`.

## 4. Structure assessment and published comparison

| Comparison | Published AF3 candidate | Published pLDDT | Published AF3 complex `ranking_score` | Our Boltz-2 candidate | Our mean pLDDT | Our complex `ipTM`; `pTM` |
|---|---|---:|---:|---|---:|---|
| Parent | huJ3 | 91.75 | 0.9187 | huJ3 | 94.38 |  |
| CDR1 | 1-V1 | 92.41 | 0.9216 | `cdr1_u03` (`GFTFSTYA`) | 96.80 | 0.9564; 0.9407 |
| CDR3 | 3-V1 | 90.87 | 0.9257 | `cdr3_s044` (`ARSKSTYISYDQSGYDY`) | 93.69 | 0.9569; 0.9373 |

| Other assessed candidate | Boltz-2 mean pLDDT | Complex ipTM | Complex pTM |
|---|---:|---:|---:|
| `cdr1_u01` | 96.55 | 0.9559 | 0.9405 |
| `cdr1_u02` | 96.26 | 0.9480 | 0.9288 |
| `cdr1_u04` | 96.52 | 0.9549 | 0.9409 |
| `cdr3_s021` | 94.92 | 0.5398 | 0.8340 |
| `cdr3_s056` | 94.27 | 0.9502 | 0.9422 |
| `cdr3_s059` | 93.60 | 0.9442 | 0.9304 |

## 5. Conclusion

We generated the CDR1 variants with AntiBMPNN and the CDR3 variants with ProteinMPNN, then calculated PD1_volume, PD2_hydro and PD3_charge for the parent and our candidates. `GFTFSDYA` is the CDR1 frequency leader; `GFTFSTYA` and `ARSKSTYISYDQSGYDY` have the highest complex ipTM among their assessed CDR1 and CDR3 groups.
