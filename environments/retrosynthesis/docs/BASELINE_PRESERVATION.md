# SRG-01 baseline preservation

Baseline ID: `srg-01-mvp-v0.1.0`. Owner: Codex `/root`, acting as the local
environment maintainer under the user's implementation request.

The original 152 package files were inventoried and hashed before SRG-01 edits.
The local bundle contains 1,567 files and 1,017,638,000 payload bytes, including
the original source, tests, task inputs, role prompts, results and failures;
condition model; LocalRetro checkpoint and inference templates; impurity model
and tokenizer; AiZynthFinder checkpoint/templates; Doyle development records;
Agent Scientist integration source; and dependency version inventories for all
four runtimes. External repository commit pins accompany the copied source.

The bundle is at `artifacts/baselines/srg-01-mvp-v0.1.0/`. Its
[manifest](../artifacts/baselines/srg-01-mvp-v0.1.0/manifest.json) has SHA-256:

```text
0ae6a2034650aff0421f72ee9fe92dcdb77f9b3530a46a6949dd6f7247e4b291
```

From the package root, independently verify every preserved file:

```sh
.venv/bin/python -m synthesis_route_gym.snapshot verify \
  --snapshot artifacts/baselines/srg-01-mvp-v0.1.0 \
  --expected-sha256 0ae6a2034650aff0421f72ee9fe92dcdb77f9b3530a46a6949dd6f7247e4b291
```

The hash must come from this recorded anchor or the separate acceptance receipt,
not from a newly computed hash of a potentially changed manifest. The verifier
checks manifest bytes before parsing the same buffer, validates paths, requires
exact root entries, rejects symlinks and special files, and detects missing,
extra or modified payload files. This is local integrity verification, not a
security boundary against a concurrently malicious file owner.

The creator accepts an explicit file list and refuses an existing output path.
It verifies captured source hashes and applies owner-readable, non-writable
permissions. An owner can still change those permissions: this is protection
against accidental overwrite, not immutable storage or a digital signature.
Creation failures remove only the newly claimed partial output.

Creation specification: [snapshot_spec.json](../artifacts/steps/srg-01/snapshot_spec.json).
Runtime versions: [environment_versions.json](../artifacts/steps/srg-01/environment_versions.json).
The large payload remains local and is excluded from Git. Existing user changes
elsewhere in REBOLT were not modified. Credentials and profile configuration
files were not copied. Filename screening is a guardrail; a caller must still
review the selected inputs and metadata for secrets.

This is not a fully self-contained offline installation: dependency binaries,
the full REBOLT/Agent Scientist repositories, unused training tables and unrelated
user files are excluded. Dependency versions identify the current runtimes but
are not a resolved cross-platform lock. The manifest states these limits.

The SRG-01 utility and protocol are new work, so they are versioned separately
from the pre-change baseline. Every later experiment must record this baseline
ID/hash, the applicable protocol ID/hash, task/split hashes, configuration and
scientific-model hashes. Step 2 supplies the dataset manifests; later benchmark
runners must enforce these fields. Existing historical results remain unchanged.
