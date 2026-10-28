# Managed LocalRetro setup verification

Run `python3 scripts/setup_retrosynthesis.py install` from the environment
directory. The installer discovers an existing REBOLT model copy and compatible
runtime on this server, or accepts `--existing-rebolt-root` and
`--existing-rebolt-python` on a machine with those approved assets. It verifies
the checkpoint and three template SHA-256 hashes pinned in the script before
copying them into the selected Agent Scientist profile. It installs the plugin
and skill, writes private runtime settings and enables `retrosynthesis`.
Explicit bad paths or changed files fail clearly. The older
`synthesis-route-gym` plugin must be disabled because both register
`srg_action`.

The active checkpoint is `LocalRetro_boltz_USPTO_MIT.pth`, SHA-256
`0147fa71b0d1801f0c9843ce54c8a25f631f8a62cdd900583c49710211fd442c`.
It is about 75 MB; its three template tables total about 8 MB. The separate
Torch/DGL runtime on the tested server is much larger. The model cache and
runtime remain outside Git and the Python wheel.

An isolated profile completed installation and enabled the plugin. An actual
Agent Scientist tool session then reset a task, expanded through LocalRetro,
received two predictions, attested the expected checkpoint and closed. No
`SRG_*` or `REBOLT_*` shell variables were set. This checks integration; the
predicted reactions are not experimentally verified. The user's main profile
was not changed during this test.

The checkpoint and templates came from the existing local REBOLT copy and its
ignored `req_data/` directory. Their redistribution provenance and rights are
unresolved. The local source carries an Apache 2.0 license file, while current
upstream LocalRetro declares CC BY-NC-SA 4.0. The installer treats the supplied
REBOLT Python source as trusted local code; its Python files are not pinned by
this script. Template files are hash-pinned because LocalRetro evaluates fields
from them during loading.

The public repository does not bundle or serve these artifacts. A new user
without an approved LocalRetro copy still needs an authorized source and
compatible scientific runtime. Public automatic download requires a reviewed
artifact source, digest, license terms and runtime installer.
