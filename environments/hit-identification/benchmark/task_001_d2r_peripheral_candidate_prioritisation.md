# D2R task source metadata

Owner-only provenance. Do not supply this file to the execution agent.

**Task Format:** goal_oriented
**Grading Mode:** manual_review_required

## Publication

Kim S, Jo WH, Cha JO, Kim MS. Identification of novel peripherally restricted risperidone-like dopamine D2 receptor antagonists for prolactin-mediated neuroprotection through a multi-stage in silico screening. PLOS One, 2026. [DOI](https://doi.org/10.1371/journal.pone.0355997). [PMC13524263](https://pmc.ncbi.nlm.nih.gov/articles/PMC13524263/).

## Input provenance

The library is the complete set of 400 `SMILES CODE` records and corresponding compound/ZINC identifiers in [S1 Table](https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0355997.s003&type=supplementary). The CSV/SDF library was exported from those inputs with full chemical-identity round-trip checks. It is not a substitute library. There are 398 unique full InChIKeys; retain all 400 source records.

The original PDB 6CM4 crystal complex and source mmCIF are supplied, with supporting structures 6A93, 3RZE and 7B6W from RCSB. Canonical human DRD2 sequence P14416 is supplied separately from the deposited fusion construct sequence. Native bound controls preserve experimental coordinates and have explicit atom-name mappings. Domperidone is PubChem CID 3151; risperidone is CCD 8NU.

The authors' prepared receptor model was not located in inspected public sources. No independently rebuilt receptor is presented as that model or supplied as a replacement input in this task.

## Source discrepancies and adaptation

Figure 2 contains molecular-identity/annotation conflicts. Chemical inputs are established from the deposited input SMILES and identifiers. Four supplementary ADME payloads duplicate the preceding compound and one additional row has incomplete descriptor data; those predictions are not supplied as fresh agent results. One published docking score is missing. Source residue-numbering and an off-target pocket definition require scrutiny during any historical comparison.

Eight shortlisted compounds and two final priorities are output counts adapted from the source. Their identities and scores are intentionally omitted from the execution task. The agent is not required to reproduce the publication's exact sequence of methods or its dynamics stage. No formal numerical scientific rubric is defined for this task version, and file presence must not be treated as scientific success.
