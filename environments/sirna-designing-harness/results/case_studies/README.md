# Recorded technical case studies

## KRAS14: passed declared technical gates

[KRAS_14_technical_validation/bundle.json](KRAS_14_technical_validation/bundle.json) binds the actual14 supplied KRAS core pairs to recorded native siRNA-Bench results, raw filter rows, four exact reference views, selected rows from a distinct earlier job and supplemental annotations.

The source Bench job is `run-d68bc6039d8b49089c2fb7c069e1823e`; the distinct earlier assessment is `run-31cdc0e38a914bdf92b57f22153cdf99`. Both recorded14/100 candidate assessment scopes are preserved. No model was rerun for this repository update.

Source input/native result/gate files are copied byte-identically. The reference JSON preserves original DNA-letter sequences, accession/header, original FASTA hash, source URL/time and annotations. The earlier comparison CSV selects these exact14 IDs from the100-row output without changing values. Supplemental annotations are selected from the preceding filtered panel. These derivations are explicit in [source_provenance.json](KRAS_14_technical_validation/source_provenance.json).

```bash
python3 -B scripts/run.py verify-technical-case
python3 -B scripts/run.py technical-report \
  --bundle results/case_studies/KRAS_14_technical_validation/bundle.json \
  --out /absolute/path/to/NEW-report-directory
```

The new portable report checks exact pair identity, mapping/coverage, actual required-model statuses, configured properties, native failed/missing fields, earlier-job agreement and source hashes. The included result is14 technical passes. [Executed report](../technical_validation_KRAS14/technical_report.md).

The report retains nine original Ridge extrapolation flags, four low passenger-seed source annotations and all raw native gate gaps. Gene/seed search scope and source-scaffold annotations keep their original meanings. Technical validation covers the declared computational checks; biological efficacy, safety and delivery are separate evaluation stages.

The snapshot is small recorded evidence, not scientific software, a transcriptome database, a model download or an independently measured efficacy benchmark. Original external paths are provenance locators only; portable replay does not read them. The older [85-file KRAS archive](../../benchmark/KRAS/README.md) is unchanged.
