from __future__ import annotations

from pathlib import Path

from .models import SPEEnvironment


DEFAULT_BASE_INSTRUCTIONS = Path(__file__).resolve().parents[2] / "BASE_AGENT_INSTRUCTIONS.md"


def build_system_prompt(
    agent: SPEEnvironment,
    base_instructions_path: Path | str = DEFAULT_BASE_INSTRUCTIONS,
) -> str:
    base = Path(base_instructions_path).read_text(encoding="utf-8").strip()

    def bullets(values: tuple[str, ...]) -> str:
        return "\n".join(f"- {value}" for value in values) if values else "- None declared"

    contract = f"""
# Selected SPE Specialist Environment

- ID: {agent.id}
- Name: {agent.name}
- Group: {agent.group}
- Integration status: {agent.integration_status}
- Maximum recovery retries: {agent.max_retries}

## Mission

{agent.description}

## Capabilities

{bullets(agent.capabilities)}

## Required inputs

{bullets(agent.required_inputs)}

## Optional inputs

{bullets(agent.optional_inputs)}

## Required outputs

{bullets(agent.outputs)}

## Intended tool adapters

{bullets(agent.tool_adapters)}

Adapter names declare intended integrations; they do not prove availability.

## Validation checks

{bullets(agent.validation_checks)}

## Scientific constraints

{bullets(agent.scientific_constraints)}

## Independent acceptance criteria

{bullets(agent.acceptance_criteria)}

## Capability boundaries

{bullets(agent.capability_boundaries)}

## Permitted bounded recovery actions

{bullets(agent.recovery_actions)}

## Mandatory human-review triggers

{bullets(agent.human_review_when)}
""".strip()
    return f"{base}\n\n{contract}\n"
