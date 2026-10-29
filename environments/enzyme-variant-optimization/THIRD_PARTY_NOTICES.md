# Source and dependency notices

The enclosing repository has not selected a license. Its `LICENSE` notice is not a license grant. This contribution does not select a different license or establish public redistribution approval.

- **DiscoveryRSI:** external source at `Gen-Verse/DiscoveryRSI`, revision `7389e0b58ae50486ab35aa3dcbfa2fa15fea1a91`. Its inspected `LICENSE` identifies Apache License 2.0 and copyright 2026 Gen-Verse. The helper fetches this source separately; it is not bundled into the distribution. Preserve its notices and review its pinned terms for release.
- **Enzyme workflow executor:** based on the company's `agent-scientist-enzyme-workflow` 0.2.4 development source, included under `enzyme_research/_support/enzyme_workflow` for replay and dependency portability. The environment adapts its catalogue references, explanatory instructions, and unavailable-tool message to the current contracts. `SOURCE_PROVENANCE.json` records original and packaged hashes so those changes are explicit. It is not Agent-Scientist core source or a separate top-level installed plugin.
- **Agent-Scientist:** an external operator-supplied runtime using its existing connector and authorization. Its code, profiles, credentials, and model weights are not bundled. Its current checkout and dependency terms must be recorded for live execution.
- **Native host support:** `enzyme_environment` and `enzyme_benchmark` are separately supplied modules for the development native transport/isolation path. Their packaging and distribution are an open release dependency, not a claimed public package installation.
- **Python dependencies:** setuptools/wheel are build tools; pytest and Biopython support tests; RDKit supports optional molecular identity checks. See `pyproject.toml` for versions. Each retains its own license and notices.

No scientific-model checkpoints, external datasets, experimental measurements, or customer inputs are included. Research citations are maintained in the matching research directory.
