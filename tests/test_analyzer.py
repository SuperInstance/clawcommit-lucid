"""Tests for the analyzer module."""

from clawcommit_lucid.analyzer import ChangeAnalyzer, ChangeCategory
from clawcommit_lucid.change import Change, ChangeType, FileChange


def _make_change(files, hint=None):
    return Change(files=files, message_hint=hint)


class TestChangeAnalyzer:
    def test_test_files_categorized(self):
        change = _make_change([FileChange("tests/test_foo.py", ChangeType.MODIFIED, ["def test_x():"])])
        result = ChangeAnalyzer().analyze(change)
        assert result.category == ChangeCategory.TEST

    def test_docs_categorized(self):
        change = _make_change([FileChange("README.md", ChangeType.MODIFIED, ["updated docs"])])
        result = ChangeAnalyzer().analyze(change)
        assert result.category == ChangeCategory.DOCS

    def test_new_file_suggests_feat(self):
        change = _make_change([FileChange("src/feature.py", ChangeType.ADDED, ["class Feature:", "    pass"])])
        result = ChangeAnalyzer().analyze(change)
        assert result.category == ChangeCategory.FEAT

    def test_fix_keywords(self):
        change = _make_change(
            [FileChange("src/bug.py", ChangeType.MODIFIED, ["fixed crash"])],
            hint="fix null pointer crash"
        )
        result = ChangeAnalyzer().analyze(change)
        assert result.category == ChangeCategory.FIX

    def test_config_file_is_chore(self):
        change = _make_change([FileChange("pyproject.toml", ChangeType.MODIFIED, ["version = '1.1'"])])
        result = ChangeAnalyzer().analyze(change)
        assert result.category == ChangeCategory.CHORE

    def test_scope_inferred_from_common_directory(self):
        change = _make_change([
            FileChange("api/routes.py", ChangeType.MODIFIED, ["new endpoint"]),
            FileChange("api/models.py", ChangeType.MODIFIED, ["new model"]),
        ])
        result = ChangeAnalyzer().analyze(change)
        assert result.scope == "api"

    def test_empty_change_is_chore(self):
        result = ChangeAnalyzer().analyze(Change())
        assert result.category == ChangeCategory.CHORE

    def test_confidence_is_between_0_and_1(self):
        change = _make_change([FileChange("src/main.py", ChangeType.MODIFIED, ["x = 1"])])
        result = ChangeAnalyzer().analyze(change)
        assert 0.0 <= result.confidence <= 1.0

    def test_perf_keywords(self):
        change = _make_change(
            [FileChange("src/cache.py", ChangeType.MODIFIED, ["optimized lookup", "cache result"])],
            hint="optimize cache performance"
        )
        result = ChangeAnalyzer().analyze(change)
        assert result.category == ChangeCategory.PERF

    def test_refactor_keywords(self):
        change = _make_change(
            [FileChange("src/module.py", ChangeType.MODIFIED, ["refactored class"])],
            hint="refactor module structure"
        )
        result = ChangeAnalyzer().analyze(change)
        assert result.category == ChangeCategory.REFACTOR

    def test_custom_keywords(self):
        analyzer = ChangeAnalyzer(custom_keywords={
            ChangeCategory.FEAT: ["enhance", "upgrade"]
        })
        change = _make_change(
            [FileChange("src/app.py", ChangeType.MODIFIED, ["enhanced the module"])],
        )
        result = analyzer.analyze(change)
        assert ChangeCategory.FEAT in result.indicators or result.category == ChangeCategory.FEAT

    def test_indicators_populated(self):
        change = _make_change([
            FileChange("tests/test_x.py", ChangeType.MODIFIED, ["def test_new():"]),
            FileChange("src/x.py", ChangeType.ADDED, ["new function"]),
        ])
        result = ChangeAnalyzer().analyze(change)
        assert len(result.indicators) > 0
