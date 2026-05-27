"""Analyze changes and categorize them into conventional commit types."""

from __future__ import annotations

import enum
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .change import Change, ChangeType, FileChange


class ChangeCategory(enum.Enum):
    """Conventional commit categories."""

    FEAT = "feat"
    FIX = "fix"
    REFACTOR = "refactor"
    DOCS = "docs"
    TEST = "test"
    CHORE = "chore"
    STYLE = "style"
    PERF = "perf"
    BUILD = "build"
    CI = "ci"


# Keywords that suggest a fix
_FIX_KEYWORDS = re.compile(
    r"\b(fix|bug|issue|error|crash|broken|repair|patch|hotfix|resolve)\b", re.IGNORECASE
)

# Keywords that suggest a feature
_FEAT_KEYWORDS = re.compile(
    r"\b(add|create|implement|support|introduce|new|feature|enable|allow)\b", re.IGNORECASE
)

# Keywords that suggest refactoring
_REFACTOR_KEYWORDS = re.compile(
    r"\b(refactor|rename|move|extract|simplify|clean|reorganize|restructure)\b",
    re.IGNORECASE,
)

# Keywords that suggest performance
_PERF_KEYWORDS = re.compile(
    r"\b(perf|optim|faster|speed|cache|memoize|lazy|efficient)\b", re.IGNORECASE
)

# Keywords that suggest style changes
_STYLE_KEYWORDS = re.compile(
    r"\b(format|lint|whitespace|indent|style|fmt|prettier)\b", re.IGNORECASE
)


@dataclass
class AnalysisResult:
    """The outcome of analyzing a Change."""

    category: ChangeCategory
    scope: Optional[str] = None
    confidence: float = 1.0
    indicators: List[str] = field(default_factory=list)
    affected_areas: List[str] = field(default_factory=list)


class ChangeAnalyzer:
    """Categorizes a Change into a conventional commit type."""

    def __init__(self, custom_keywords: Optional[Dict[ChangeCategory, List[str]]] = None):
        self._custom_keywords: Dict[ChangeCategory, re.Pattern] = {}
        if custom_keywords:
            for cat, words in custom_keywords.items():
                pattern = r"\b(" + "|".join(re.escape(w) for w in words) + r")"
                self._custom_keywords[cat] = re.compile(pattern, re.IGNORECASE)

    def analyze(self, change: Change) -> AnalysisResult:
        """Analyze a Change and return a categorized result."""
        if not change.files:
            return AnalysisResult(category=ChangeCategory.CHORE, confidence=0.5)

        scores: Dict[ChangeCategory, float] = {}
        indicators: List[str] = []
        areas: List[str] = []

        self._score_by_file_types(change, scores, indicators, areas)
        self._score_by_content(change, scores, indicators)
        self._score_by_structure(change, scores, indicators)
        self._apply_custom_keywords(change, scores, indicators)

        if not scores:
            scores[ChangeCategory.CHORE] = 0.5

        total = sum(scores.values())
        best_cat = max(scores, key=scores.get)
        confidence = scores[best_cat] / total if total > 0 else 0.0

        scope = self._infer_scope(change, areas)

        return AnalysisResult(
            category=best_cat,
            scope=scope,
            confidence=round(confidence, 3),
            indicators=indicators,
            affected_areas=areas,
        )

    # ------------------------------------------------------------------
    # Scoring helpers
    # ------------------------------------------------------------------

    def _score_by_file_types(
        self,
        change: Change,
        scores: Dict[ChangeCategory, float],
        indicators: List[str],
        areas: List[str],
    ) -> None:
        for f in change.files:
            if f.is_test:
                scores[ChangeCategory.TEST] = scores.get(ChangeCategory.TEST, 0) + 2.0
                indicators.append("test file modified")
            if f.is_docs:
                scores[ChangeCategory.DOCS] = scores.get(ChangeCategory.DOCS, 0) + 2.0
                indicators.append("documentation file modified")
            if f.is_config:
                scores[ChangeCategory.CHORE] = scores.get(ChangeCategory.CHORE, 0) + 1.5
                indicators.append("config file modified")
            if f.change_type == ChangeType.ADDED:
                scores[ChangeCategory.FEAT] = scores.get(ChangeCategory.FEAT, 0) + 1.0
                indicators.append(f"new file: {f.filename}")
            if f.change_type == ChangeType.REMOVED:
                scores[ChangeCategory.CHORE] = scores.get(ChangeCategory.CHORE, 0) + 0.5
                indicators.append(f"deleted file: {f.filename}")

            # Collect directory areas
            parts = f.path.split("/")
            if len(parts) > 1:
                areas.append(parts[0])

    def _score_by_content(
        self,
        change: Change,
        scores: Dict[ChangeCategory, float],
        indicators: List[str],
    ) -> None:
        all_added = " ".join(line for f in change.files for line in f.added_lines)
        all_removed = " ".join(line for f in change.files for line in f.removed_lines)
        combined = f"{all_added} {all_removed}"
        if change.message_hint:
            combined = f"{combined} {change.message_hint}"

        if not combined.strip():
            return

        for regex, cat, label in [
            (_FIX_KEYWORDS, ChangeCategory.FIX, "fix keywords"),
            (_FEAT_KEYWORDS, ChangeCategory.FEAT, "feature keywords"),
            (_REFACTOR_KEYWORDS, ChangeCategory.REFACTOR, "refactor keywords"),
            (_PERF_KEYWORDS, ChangeCategory.PERF, "performance keywords"),
            (_STYLE_KEYWORDS, ChangeCategory.STYLE, "style keywords"),
        ]:
            matches = regex.findall(combined)
            if matches:
                scores[cat] = scores.get(cat, 0) + len(matches)
                indicators.append(f"{label}: {', '.join(matches[:3])}")

    def _score_by_structure(
        self,
        change: Change,
        scores: Dict[ChangeCategory, float],
        indicators: List[str],
    ) -> None:
        added = change.total_added
        removed = change.total_removed

        if removed > added * 2 and removed > 5:
            scores[ChangeCategory.REFACTOR] = scores.get(ChangeCategory.REFACTOR, 0) + 1.0
            indicators.append("net removal of lines (cleanup)")

        if added > 20 and not any(f.is_test for f in change.files):
            scores[ChangeCategory.FEAT] = scores.get(ChangeCategory.FEAT, 0) + 0.5
            indicators.append("large addition of lines")

    def _apply_custom_keywords(
        self,
        change: Change,
        scores: Dict[ChangeCategory, float],
        indicators: List[str],
    ) -> None:
        combined = " ".join(
            line for f in change.files for line in f.added_lines + f.removed_lines
        )
        if change.message_hint:
            combined = f"{combined} {change.message_hint}"

        for cat, regex in self._custom_keywords.items():
            matches = regex.findall(combined)
            if matches:
                scores[cat] = scores.get(cat, 0) + len(matches)
                indicators.append(f"custom {cat.value} keywords: {', '.join(matches[:3])}")

    @staticmethod
    def _infer_scope(change: Change, areas: List[str]) -> Optional[str]:
        if not areas:
            return None
        counter = Counter(areas)
        most_common = counter.most_common(1)[0][0]
        # Only return scope if there's a clear dominant area
        if len(change.files) > 1 and counter[most_common] > 1:
            return most_common
        return None
