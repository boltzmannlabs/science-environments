# Portable installation and operating boundary

## What transfers

Transfer this skill directory, its protocol references, JSON templates and standard-library helper scripts. They guide Agent Scientist and provide technical checks; they are not a newly registered SCI tool or an unattended scientific execution engine. Installing them does not install OligoFormer, RNA-FM, siRNA-Bench, model weights, transcript indices, seed tables or a deployed Ridge model.

Do not redistribute third-party code, checkpoints, source datasets, credentials or another profile's configuration with this skill. The original documentation/helpers are MIT; third-party scientific components retain their own terms. Obtain authorization for OligoFormer's conflicting README/LICENSE terms before installation/use; a public repository is not a license grant.

## Install on another system

1. Install/configure that system's maintained Agent Scientist build using its local README and `sci --help`. Do not assume upstream product instructions describe the customized build. Authenticate the conversational provider through SCI, never through this package's JSON files.
2. Unpack the received archive into a reviewed local directory. Inspect `SKILL.md`, scripts and references. Verify the archive SHA-256 against the separately received value; local checksum agreement is integrity, not publisher identity.
3. Run `python3 scripts/transfer_skill.py check --source /absolute/path/to/sirna-harness`. These helpers require Python3.10+ and no pip packages.
4. Resolve the intended active profile's skills directory from that SCI installation. Do not assume `~/.sci/skills` belongs to the intended profile. Supply an explicit destination ending in `skills/science/sirna-harness`.
5. Preview: `python3 scripts/transfer_skill.py install --source /absolute/path/to/sirna-harness --destination /absolute/active-profile/skills/science/sirna-harness`.
6. Apply the same command with `--apply` only after review. The installer refuses an existing destination and symlinks; it never overwrites an existing skill/profile. Use a separate versioned backup and a deliberate agent-reviewed update when replacing an existing installation.
7. Start a fresh SCI session. The current locally inspected CLI supports `sci --skills sirna-harness`; check the destination build's help before using it. `/Add_skill` with a local path can be an agent task, not an automatic backend installer. Do not assume `sci skills install LOCAL_PATH` is supported: the inspected command advertises registry identifiers/HTTP URLs.
8. Copy `templates/environment.example.json` and `templates/objective.example.json` into a NEW project directory; fill only reviewed local paths, source identities and biological choices. Do not modify the templates or add secret values.
9. Run `python3 scripts/sirna_portable.py preflight --config /absolute/project/environment.json`. Missing assets are expected on a new machine. File presence is AVAILABLE_UNVERIFIED, not real inference verification. Discover the live SCI tools separately.
10. Install/authorize each chosen backend independently. Use isolated scientific environments, verify official weights/source identity and licensing, then exercise a publisher example through the actual integration. Preserve that new machine's receipts. Historical receipts from another machine are not current readiness.

An installer failure must leave the existing destination untouched. No command here downloads a model or sends a target sequence anywhere. Do not use `--yolo`, unreviewed shell hooks or one-shot auto-approval modes merely to install this package.

## Required scientific backends

Generation: a matching authorized scientific tool; inspect Boltzmann contracts before provider selection unless explicitly directed to local execution. For the explicit local workflow, OligoFormer plus verified RNA-FM features/checkpoints.
Assessment: actual native siRNA-Bench interfaces, RN.Ai-Predict and RNAiSpline checkpoints, an independently verified transparent Ridge asset if used, ViennaRNA, and species-matched transcript/seed references. These are separate integrations, not files supplied by this package. Reinspect schemas; no hardcoded old installation paths are dependencies.

Local scientific tools with installed assets need no remote inference token. SCI model authentication is separate. A remote scientific provider may require its own entitlement and masked credential setup, plus explicit sequence-transfer approval. Never put token values into objectives, skills, reports or archives.

## Verification tiers

PACKAGE_INTEGRITY: checked file bytes and path safety.
HELPER_SOFTWARE: objective/candidate/gate checks exercised.
BACKEND_READINESS: discover actual tools/environment/assets.
REAL_INFERENCE: execute and verify actual native scientific output.
SCIENTIFIC_QUALIFICATION: assess applicability, specificity, context and measured evidence.

Never promote success at a lower tier into a higher one. This package was designed for portability; installation/helper tests on one host are not validation of GPU support, Windows/macOS execution or scientific inference on another host.
