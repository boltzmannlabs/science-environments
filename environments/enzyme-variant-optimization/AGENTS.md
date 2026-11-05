# Enzyme Variant Optimization Working Instructions

Read `ENVIRONMENT_SPEC.md`, `config/workflow.json` and the selected file in `tasks/` before executing a case. These define the full scientific workflow and evidence requirements; use SCI's existing discovery, validation, tools, job tracking and saved-subagent lifecycle to perform it.

Execute initial and revised sequence generation with suitable design/search tools selected from current Boltzmann or ToolUniverse capabilities. Agent-written mutations and string edits alone do not complete generation. Keep sequence identity, chemistry and candidate lineage intact across stages.

The user's selected comparison approach governs delegation. Agent-alone runs do not use subagents. Specialist-assisted runs explicitly use the reviewed proposer and critic; the parent executes scientific tools. Do not activate or edit user profiles automatically.

Do not read `benchmark/REFERENCE_VALUES.md`, target-study winners or other-arm results during design. Research reaction chemistry using permitted primary sources. This instruction is not an OS sandbox. Preserve available results and report unresolved required evidence.

Put large/private run data in a dedicated workspace or ignored `results/local/`. Do not commit credentials, runtime caches, model weights or user results. No scientific submission is authorized merely by opening this folder.
