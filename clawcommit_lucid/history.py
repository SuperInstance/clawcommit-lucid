"""Analyze past commit patterns for style consistency."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class CommitRecord:
    """A lightweight representation of a past commit."""

    message: str
    type: str = ""
    scope: str = ""
    subject: str = ""

    def __post_init__(self) -> None:
        if self.type or self.scope or self.subject:
            return
        # Try to parse conventional commit format
        match = re.match(r"^(\w+)(?:\(([^)]+)\))?:\s+(.+)$", self.message.split("\n")[0])
        if match:
            self.type = match.group(1)
            self.scope = match.group(2) or ""
            self.subject = match.group(3).strip()


@dataclass
class StyleProfile:
    """Statistical summary of commit style."""

    preferred_types: List[str] = field(default_factory=list)
    common_scopes: List[str] = field(default_factory=list)
    avg_subject_length: float = 0.0
    uses_scopes: bool = False
    scope_frequency: Dict[str, int] = field(default_factory=dict)
    type_frequency: Dict[str, int] = field(default_factory=dict)
    sample_count: int = 0

    @property
    def dominant_type(self) -> Optional[str]:
        return self.preferred_types[0] if self.preferred_types else None


class CommitHistory:
    """Analyzes past commit messages to derive a style profile."""

    def __init__(self, commits: Optional[List[CommitRecord]] = None):
        self._commits: List[CommitRecord] = commits or []

    @property
    def commits(self) -> List[CommitRecord]:
        return self._commits

    def add(self, message: str) -> None:
        self._commits.append(CommitRecord(message=message))

    def add_many(self, messages: List[str]) -> None:
        for msg in messages:
            self.add(msg)

    def profile(self) -> StyleProfile:
        """Derive a StyleProfile from accumulated commits."""
        if not self._commits:
            return StyleProfile()

        type_counter: Counter = Counter()
        scope_counter: Counter = Counter()
        subject_lengths: List[int] = []
        scopes_used = 0

        for c in self._commits:
            if c.type:
                type_counter[c.type] += 1
            if c.scope:
                scope_counter[c.scope] += 1
                scopes_used += 1
            if c.subject:
                subject_lengths.append(len(c.subject))

        uses_scopes = scopes_used > len(self._commits) * 0.3
        avg_len = sum(subject_lengths) / len(subject_lengths) if subject_lengths else 0.0

        return StyleProfile(
            preferred_types=[t for t, _ in type_counter.most_common(5)],
            common_scopes=[s for s, _ in scope_counter.most_common(5)],
            avg_subject_length=round(avg_len, 1),
            uses_scopes=uses_scopes,
            scope_frequency=dict(scope_counter),
            type_frequency=dict(type_counter),
            sample_count=len(self._commits),
        )

    def suggest_type(self, candidates: List[str]) -> Optional[str]:
        """From a list of candidate commit types, pick the one most consistent with history."""
        if not self._commits:
            return candidates[0] if candidates else None

        profile = self.profile()
        for preferred in profile.preferred_types:
            if preferred in candidates:
                return preferred
        return candidates[0] if candidates else None

    def suggest_scope(self, proposed: Optional[str] = None) -> Optional[str]:
        """Decide whether to use a scope and which one."""
        profile = self.profile()
        if not profile.uses_scopes:
            return None
        if proposed and proposed in profile.common_scopes:
            return proposed
        return proposed  # respect the proposed scope even if not common

    @classmethod
    def from_messages(cls, messages: List[str]) -> "CommitHistory":
        history = cls()
        history.add_many(messages)
        return history
