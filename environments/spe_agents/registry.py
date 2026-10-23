from __future__ import annotations

import json
import re
from pathlib import Path

from .models import SPEConfigurationError, SPEEnvironment


# Contracts are shipped beside the package in ``spe_agents/environments``.
DEFAULT_ENVIRONMENTS_DIR = Path(__file__).resolve().parent / "environments"
ACTIVE_ENVIRONMENT_IDS = tuple(
    f"{number:02d}" for number in range(1, 21) if number not in {13, 16}
)


class SPERegistry:
    """Load, validate, resolve, and route the 18 active SPE specialist contracts."""

    def __init__(self, environments_dir: Path | str = DEFAULT_ENVIRONMENTS_DIR):
        self.environments_dir = Path(environments_dir)
        self._agents = self._load()

    def _load(self) -> tuple[SPEEnvironment, ...]:
        if not self.environments_dir.is_dir():
            raise SPEConfigurationError(f"environment directory does not exist: {self.environments_dir}")
        agents: list[SPEEnvironment] = []
        for path in sorted(self.environments_dir.glob("*/agent.json")):
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise SPEConfigurationError(f"cannot read {path}: {exc}") from exc
            if not isinstance(raw, dict):
                raise SPEConfigurationError(f"{path}: top-level JSON value must be an object")
            agent = SPEEnvironment.from_dict(raw, path)
            if path.parent.name != f"{agent.id}-{agent.slug}":
                raise SPEConfigurationError(
                    f"{path}: directory must be named {agent.id}-{agent.slug}"
                )
            agents.append(agent)

        if len(agents) != len(ACTIVE_ENVIRONMENT_IDS):
            raise SPEConfigurationError(
                f"expected {len(ACTIVE_ENVIRONMENT_IDS)} SPE environments, found {len(agents)}"
            )
        ids = [agent.id for agent in agents]
        slugs = [agent.slug for agent in agents]
        if len(ids) != len(set(ids)) or len(slugs) != len(set(slugs)):
            raise SPEConfigurationError("SPE environment ids and slugs must be unique")
        if set(ids) != set(ACTIVE_ENVIRONMENT_IDS):
            raise SPEConfigurationError(
                f"SPE environment ids must exactly match {', '.join(ACTIVE_ENVIRONMENT_IDS)}"
            )
        return tuple(sorted(agents, key=lambda item: item.id))

    def all(self) -> tuple[SPEEnvironment, ...]:
        return self._agents

    def get(self, identifier: str) -> SPEEnvironment:
        normalized = identifier.strip().lower()
        for agent in self._agents:
            if normalized in {agent.id, agent.slug.lower(), agent.name.lower()}:
                return agent
        raise KeyError(f"unknown SPE environment: {identifier}")

    def route(self, task: str, *, limit: int = 3) -> list[tuple[SPEEnvironment, int]]:
        if limit < 1:
            raise ValueError("limit must be at least 1")
        tokens = set(re.findall(r"[a-z0-9]+", task.lower()))
        ranked: list[tuple[SPEEnvironment, int]] = []
        for agent in self._agents:
            score = 0
            for keyword in agent.routing_keywords:
                keyword_tokens = set(re.findall(r"[a-z0-9]+", keyword.lower()))
                if keyword_tokens and keyword_tokens.issubset(tokens):
                    score += max(1, len(keyword_tokens))
            if score:
                ranked.append((agent, score))
        return sorted(ranked, key=lambda item: (-item[1], item[0].id))[:limit]
