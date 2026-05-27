"""Customizable commit message templates."""

from __future__ import annotations

import re
import string
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .analyzer import AnalysisResult, ChangeCategory
from .change import Change


@dataclass
class Template:
    """A commit message template with placeholder fields."""

    name: str
    pattern: str  # e.g. "{type}({scope}): {subject}"
    body_template: str = "{body}"
    footer_template: str = "{footer}"

    def format(
        self,
        type: str = "",
        scope: str = "",
        subject: str = "",
        body: str = "",
        footer: str = "",
        **extra: str,
    ) -> str:
        """Render the template with provided values."""
        mapping = {
            "type": type,
            "scope": scope,
            "subject": subject,
            "body": body,
            "footer": footer,
            **extra,
        }
        header = self.pattern.format_map(mapping)
        parts = [header]
        if body and self.body_template:
            parts.append("")
            parts.append(self.body_template.format_map(mapping))
        if footer and self.footer_template:
            parts.append("")
            parts.append(self.footer_template.format_map(mapping))
        return "\n".join(parts)


# Built-in templates
CONVENTIONAL = Template(
    name="conventional",
    pattern="{type}: {subject}",
    body_template="{body}",
    footer_template="{footer}",
)

CONVENTIONAL_SCOPED = Template(
    name="conventional-scoped",
    pattern="{type}({scope}): {subject}",
    body_template="{body}",
    footer_template="{footer}",
)

EMOJI = Template(
    name="emoji",
    pattern="{emoji} {subject}",
    body_template="{body}",
)

SEMVER = Template(
    name="semver",
    pattern="{type}({scope}): {subject}",
    body_template="{body}\n\nSemver: {bump}",
)


_EMOJI_MAP = {
    ChangeCategory.FEAT: "✨",
    ChangeCategory.FIX: "🐛",
    ChangeCategory.REFACTOR: "♻️",
    ChangeCategory.DOCS: "📝",
    ChangeCategory.TEST: "✅",
    ChangeCategory.CHORE: "🔧",
    ChangeCategory.STYLE: "🎨",
    ChangeCategory.PERF: "⚡",
    ChangeCategory.BUILD: "📦",
    ChangeCategory.CI: "👷",
}

_SEMVER_BUMP = {
    ChangeCategory.FEAT: "minor",
    ChangeCategory.FIX: "patch",
    ChangeCategory.REFACTOR: "patch",
    ChangeCategory.DOCS: "none",
    ChangeCategory.TEST: "none",
    ChangeCategory.CHORE: "none",
    ChangeCategory.STYLE: "none",
    ChangeCategory.PERF: "patch",
    ChangeCategory.BUILD: "none",
    ChangeCategory.CI: "none",
}


class TemplateEngine:
    """Manages and renders commit message templates."""

    def __init__(self) -> None:
        self._templates: Dict[str, Template] = {
            t.name: t
            for t in [CONVENTIONAL, CONVENTIONAL_SCOPED, EMOJI, SEMVER]
        }
        self._active: str = "conventional"

    @property
    def active(self) -> str:
        return self._active

    def use(self, name: str) -> None:
        if name not in self._templates:
            raise KeyError(f"Unknown template: {name!r}. Available: {list(self._templates)}")
        self._active = name

    def register(self, template: Template) -> None:
        self._templates[template.name] = template

    def list_templates(self) -> List[str]:
        return list(self._templates)

    def render(
        self,
        change: Change,
        analysis: AnalysisResult,
        subject: str,
        body: str = "",
        footer: str = "",
    ) -> str:
        """Render the active template for a given analysis."""
        tpl = self._templates[self._active]
        cat = analysis.category

        # If scope exists and we're on the default conventional template, use scoped version
        if analysis.scope and self._active == "conventional" and "conventional-scoped" in self._templates:
            tpl = self._templates["conventional-scoped"]

        extra: Dict[str, str] = {}
        if tpl.name == "emoji":
            extra["emoji"] = _EMOJI_MAP.get(cat, "🔧")
        if tpl.name == "semver":
            extra["bump"] = _SEMVER_BUMP.get(cat, "none")

        return tpl.format(
            type=cat.value,
            scope=analysis.scope or "",
            subject=subject,
            body=body,
            footer=footer,
            **extra,
        )
