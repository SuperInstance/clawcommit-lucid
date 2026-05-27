"""Tests for the history module."""

from clawcommit_lucid.history import CommitHistory, CommitRecord, StyleProfile


class TestCommitRecord:
    def test_parse_conventional(self):
        rec = CommitRecord(message="feat(api): add endpoint")
        assert rec.type == "feat"
        assert rec.scope == "api"
        assert rec.subject == "add endpoint"

    def test_parse_no_scope(self):
        rec = CommitRecord(message="fix: resolve crash")
        assert rec.type == "fix"
        assert rec.scope == ""
        assert rec.subject == "resolve crash"

    def test_parse_non_conventional(self):
        rec = CommitRecord(message="random message")
        assert rec.type == ""

    def test_multiline_message(self):
        rec = CommitRecord(message="feat: add thing\n\nBody here")
        assert rec.type == "feat"
        assert rec.subject == "add thing"


class TestCommitHistory:
    def test_empty_profile(self):
        history = CommitHistory()
        profile = history.profile()
        assert profile.sample_count == 0
        assert profile.dominant_type is None

    def test_profile_from_commits(self):
        history = CommitHistory.from_messages([
            "feat: add x",
            "feat: add y",
            "fix: fix z",
        ])
        profile = history.profile()
        assert profile.sample_count == 3
        assert profile.preferred_types[0] == "feat"

    def test_scope_detection(self):
        history = CommitHistory.from_messages([
            "feat(api): add x",
            "feat(api): add y",
            "fix(ui): fix z",
        ])
        profile = history.profile()
        assert profile.uses_scopes is True
        assert "api" in profile.common_scopes

    def test_suggest_type(self):
        history = CommitHistory.from_messages([
            "fix: a",
            "fix: b",
            "fix: c",
        ])
        result = history.suggest_type(["feat", "fix"])
        assert result == "fix"

    def test_suggest_type_no_history(self):
        history = CommitHistory()
        result = history.suggest_type(["feat", "fix"])
        assert result == "feat"

    def test_add_single(self):
        history = CommitHistory()
        history.add("feat: test")
        assert len(history.commits) == 1

    def test_avg_subject_length(self):
        history = CommitHistory.from_messages([
            "feat: short",
            "feat: a bit longer subject",
        ])
        profile = history.profile()
        assert profile.avg_subject_length > 0
