from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALLOWED_GROUPS = {
    "spe-core",
    "spe-method",
    "spe-chemistry",
    "spe-drug-discovery",
    "spe-quality-control",
}
ALLOWED_STATUSES = {"unverified", "prototype", "validated", "blocked"}


class SPEConfigurationError(ValueError):
    """Raised when an SPE environment contract is incomplete or inconsistent."""


def _string_list(data: dict[str, Any], key: str, *, allow_empty: bool = False) -> tuple[str, ...]:
    value = data.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise SPEConfigurationError(f"{key!r} must be a list of non-empty strings")
    if not value and not allow_empty:
        raise SPEConfigurationError(f"{key!r} must not be empty")
    return tuple(value)


@dataclass(frozen=True)
class SPEEnvironment:
    id: str
    slug: str
    name: str
    group: str
    integration_status: str
    description: str
    capabilities: tuple[str, ...]
    required_inputs: tuple[str, ...]
    optional_inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    tool_adapters: tuple[str, ...]
    routing_keywords: tuple[str, ...]
    validation_checks: tuple[str, ...]
    scientific_constraints: tuple[str, ...]
    acceptance_criteria: tuple[str, ...]
    capability_boundaries: tuple[str, ...]
    recovery_actions: tuple[str, ...]
    human_review_when: tuple[str, ...]
    max_retries: int
    source: Path

    @classmethod
    def from_dict(cls, data: dict[str, Any], source: Path) -> "SPEEnvironment":
        for key in ("id", "slug", "name", "group", "integration_status", "description"):
            if not isinstance(data.get(key), str) or not data[key].strip():
                raise SPEConfigurationError(f"{source}: {key!r} must be a non-empty string")

        agent_id = data["id"]
        if len(agent_id) != 2 or not agent_id.isdigit() or not 1 <= int(agent_id) <= 20:
            raise SPEConfigurationError(f"{source}: id must be a zero-padded value from 01 to 20")
        if data["group"] not in ALLOWED_GROUPS:
            raise SPEConfigurationError(f"{source}: unsupported group {data['group']!r}")
        if data["integration_status"] not in ALLOWED_STATUSES:
            raise SPEConfigurationError(
                f"{source}: unsupported integration_status {data['integration_status']!r}"
            )
        max_retries = data.get("max_retries")
        if not isinstance(max_retries, int) or isinstance(max_retries, bool) or not 0 <= max_retries <= 3:
            raise SPEConfigurationError(f"{source}: max_retries must be an integer from 0 to 3")

        return cls(
            id=agent_id,
            slug=data["slug"],
            name=data["name"],
            group=data["group"],
            integration_status=data["integration_status"],
            description=data["description"],
            capabilities=_string_list(data, "capabilities"),
            required_inputs=_string_list(data, "required_inputs"),
            optional_inputs=_string_list(data, "optional_inputs", allow_empty=True),
            outputs=_string_list(data, "outputs"),
            tool_adapters=_string_list(data, "tool_adapters"),
            routing_keywords=_string_list(data, "routing_keywords"),
            validation_checks=_string_list(data, "validation_checks"),
            scientific_constraints=_string_list(data, "scientific_constraints"),
            acceptance_criteria=_string_list(data, "acceptance_criteria"),
            capability_boundaries=_string_list(data, "capability_boundaries"),
            recovery_actions=_string_list(data, "recovery_actions", allow_empty=True),
            human_review_when=_string_list(data, "human_review_when"),
            max_retries=max_retries,
            source=source,
        )

    def summary(self) -> dict[str, object]:
        return {
            "id": self.id,
            "slug": self.slug,
            "name": self.name,
            "group": self.group,
            "integration_status": self.integration_status,
            "description": self.description,
            "tool_adapters": list(self.tool_adapters),
        }
