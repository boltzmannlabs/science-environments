# enzyme-recovery intermediate receipt (ESM load failure)

Root cause: torch 2.9 torch.load weights_only=True default rejects argparse.Namespace in the trusted official fair-esm checkpoint. Correction: wrap load_model_and_alphabet_local in `torch.serialization.safe_globals([argparse.Namespace])` (call-scoped, checkpoint bytes and digest unchanged, no weights_only=False). Re-freeze ESM runner hashes to 133577b01f4c9a7353daf9d4b90d0c6ce5c18ecdffce8e446ff96d8484756579. esm_full_004 must not be reused.
