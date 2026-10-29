# MD task registry

Each task card in this directory is paired with an exact JSON packet under
`inputs/MD-*/task.json` and an entry in `cases/agent_inputs.json`.

Task cards define the system, protocol, failure mode, expected evidence, and
machine-checkable acceptance rule. They are not generic prompts. When a task
uses a synthetic fixture, the fixture is explicitly labelled diagnostic and
cannot be used as a published scientific reference.

To rebuild the packet manifest:

```bash
python scripts/build_agent_input_manifest.py
```
