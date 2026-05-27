"""Generate conventional commit messages from analyzed changes."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from .analyzer import AnalysisResult, ChangeCategory
from .change import Change, FileChange


@dataclass
class CommitMessage:
    """A generated commit message."""

    header: str
    body: str = ""
    footer: str = ""

    def __str__(self) -> str:
        parts = [self.header]
        if self.body:
            parts.append("")
            parts.append(self.body)
        if self.footer:
            parts.append("")
            parts.append(self.footer)
        return "\n".join(parts)

    @property
    def type(self) -> str:
        return self.header.split(":", 1)[0].split("(", 1)[0] if ":" in self.header else ""

    @property
    def scope(self) -> str:
        match = re.match(r"\w+\(([^)]+)\)", self.header)
        return match.group(1) if match else ""

    @property
    def subject(self) -> str:
        if ":" in self.header:
            after_colon = self.header.split(":", 1)[1].strip()
            return after_colon
        return self.header

    @property
    def first_line(self) -> str:
        return self.header


class MessageGenerator:
    """Creates conventional commit messages from analysis results."""

    # Past-tense verb suggestions per category
    _VERB_MAP = {
        ChangeCategory.FEAT: ["add", "introduce", "implement", "create"],
        ChangeCategory.FIX: ["fix", "resolve", "patch", "repair"],
        ChangeCategory.REFACTOR: ["refactor", "simplify", "reorganize", "extract"],
        ChangeCategory.DOCS: ["document", "update docs for", "add documentation for"],
        ChangeCategory.TEST: ["test", "add tests for", "cover"],
        ChangeCategory.CHORE: ["update", "configure", "maintain", "clean up"],
        ChangeCategory.STYLE: ["format", "lint", "clean style in"],
        ChangeCategory.PERF: ["optimize", "speed up", "improve performance of"],
        ChangeCategory.BUILD: ["update build for", "build"],
        ChangeCategory.CI: ["update CI for", "configure CI"],
    }

    _CATEGORY_SUBJECT_LIMIT = {
        ChangeCategory.FEAT: 72,
        ChangeCategory.FIX: 72,
    }

    def __init__(self, max_subject_length: int = 72, body_enabled: bool = True):
        self.max_subject_length = max_subject_length
        self.body_enabled = body_enabled

    def generate(self, change: Change, analysis: AnalysisResult) -> CommitMessage:
        """Generate a commit message from a change and its analysis."""
        subject = self._build_subject(change, analysis)
        subject = self._truncate_subject(subject)
        header = self._build_header(analysis, subject)

        body = self._build_body(change, analysis) if self.body_enabled else ""
        footer = self._build_footer(change, analysis)

        return CommitMessage(header=header, body=body, footer=footer)

    # ------------------------------------------------------------------
    def _build_header(self, analysis: AnalysisResult, subject: str) -> str:
        cat = analysis.category.value
        if analysis.scope:
            return f"{cat}({analysis.scope}): {subject}"
        return f"{cat}: {subject}"

    def _build_subject(self, change: Change, analysis: AnalysisResult) -> str:
        # Try hint-based subject first
        if change.message_hint:
            hint = change.message_hint.strip().rstrip(".")
            # Lowercase first char if it starts with an uppercase verb
            if hint and hint[0].isupper():
                hint = hint[0].lower() + hint[1:]
            return hint

        # Build from files
        verbs = self._VERB_MAP.get(analysis.category, ["update"])
        verb = verbs[0]

        if len(change.files) == 1:
            f = change.files[0]
            return f"{verb} {f.filename}"

        # Multiple files — summarize
        if change.added_files and not change.modified_files:
            return f"{verb} {len(change.files)} new files"
        if change.removed_files and not change.modified_files:
            return f"{verb} removal of {len(change.removed_files)} files"

        return f"{verb} {len(change.files)} files"

    def _truncate_subject(self, subject: str) -> str:
        if len(subject) <= self.max_subject_length:
            return subject
        return subject[: self.max_subject_length - 3] + "..."

    def _build_body(self, change: Change, analysis: AnalysisResult) -> str:
        lines: List[str] = []

        # File summary
        if len(change.files) <= 5:
            for f in change.files:
                symbol = {
                    "added": "+",
                    "removed": "-",
                    "modified": "~",
                    "renamed": "→",
                }.get(f.change_type.value, " ")
                lines.append(f"  {symbol} {f.path} (+{f.lines_added}/-{f.lines_removed})")
        else:
            lines.append(f"  {len(change.files)} files changed")

        lines.append(f"  +{change.total_added} -{change.total_removed} lines")

        if analysis.indicators:
            lines.append("")
            for ind in analysis.indicators[:5]:
                lines.append(f"  - {ind}")

        return "\n".join(lines)

    def _build_footer(self, change: Change, analysis: AnalysisResult) -> str:
        parts: List[str] = []
        if analysis.confidence < 0.6:
            parts.append(f"Confidence: {analysis.confidence:.0%}")
        return "\n".join(parts)
