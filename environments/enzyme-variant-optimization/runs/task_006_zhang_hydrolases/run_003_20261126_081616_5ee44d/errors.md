# Errors and recovery (task_006, v1/agent_with_specialist)

1. `pythia_cellulase_003` failed: `ValueError('Expected CPU-only Torch')` — build-time guard `torch.version.cuda is None` rejected a CUDA-enabled wheel with zero visible devices. Recovery receipt: `specialist_receipts/RECOVERY_REVIEW.md`. Corrected guard uses runtime `cuda.is_available()/device_count()`; re-frozen runner hashes; fresh runs `pythia_cellulase_004` and `pythia_beta_004` completed. Failed dir preserved; ID not reused.
2. `esm_full_004` failed: `UnpicklingError` from torch 2.9 `weights_only=True` default rejecting `argparse.Namespace` in the trusted official checkpoint. Recovery receipt: `specialist_receipts/RECOVERY_ESM_REVIEW.md`. Corrected with call-scoped `torch.serialization.safe_globals([argparse.Namespace])`; checkpoint bytes unchanged; hash re-frozen; fresh run `esm_full_005` completed. Failed dir preserved; ID not reused.
3. Verifier defects (not scientific errors): expected 21 columns/position instead of 20 standard AA; corrected before final verification passed. No scientific job resubmitted for these.

No duplicate or acceptance-unknown scientific submissions. Raw diagnostics in `errors.jsonl`.
