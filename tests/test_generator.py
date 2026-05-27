"""Tests for the generator module."""

from clawcommit_lucid.change import Change, ChangeType, FileChange
from clawcommit_lucid.analyzer import AnalysisResult, ChangeCategory
from clawcommit_lucid.generator import MessageGenerator, CommitMessage


def _simple_change():
    return Change(files=[
        FileChange("src/main.py", ChangeType.MODIFIED, ["x = 1"], ["y = 2"])
    ])


def _simple_analysis(cat=ChangeCategory.FEAT, scope=None):
    return AnalysisResult(category=cat, scope=scope, confidence=0.9)


class TestCommitMessage:
    def test_str_no_body(self):
        msg = CommitMessage(header="feat: add feature")
        assert str(msg) == "feat: add feature"

    def test_str_with_body(self):
        msg = CommitMessage(header="feat: add feature", body="details here")
        assert "details here" in str(msg)

    def test_type_property(self):
        msg = CommitMessage(header="feat(core): add feature")
        assert msg.type == "feat"

    def test_scope_property(self):
        msg = CommitMessage(header="feat(core): add feature")
        assert msg.scope == "core"

    def test_subject_property(self):
        msg = CommitMessage(header="feat: add feature")
        assert msg.subject == "add feature"


class TestMessageGenerator:
    def test_basic_generation(self):
        gen = MessageGenerator()
        msg = gen.generate(_simple_change(), _simple_analysis())
        assert msg.header.startswith("feat:")
        assert "main.py" in msg.header

    def test_scoped_header(self):
        gen = MessageGenerator()
        analysis = _simple_analysis(scope="api")
        msg = gen.generate(_simple_change(), analysis)
        assert msg.header.startswith("feat(api):")

    def test_fix_message(self):
        gen = MessageGenerator()
        msg = gen.generate(_simple_change(), _simple_analysis(ChangeCategory.FIX))
        assert msg.header.startswith("fix:")

    def test_body_contains_stats(self):
        gen = MessageGenerator()
        msg = gen.generate(_simple_change(), _simple_analysis())
        assert "+1" in msg.body
        assert "-1" in msg.body

    def test_body_disabled(self):
        gen = MessageGenerator(body_enabled=False)
        msg = gen.generate(_simple_change(), _simple_analysis())
        assert msg.body == ""

    def test_multiple_files(self):
        change = Change(files=[
            FileChange("a.py", ChangeType.ADDED, ["x"]),
            FileChange("b.py", ChangeType.ADDED, ["y"]),
            FileChange("c.py", ChangeType.ADDED, ["z"]),
        ])
        gen = MessageGenerator()
        msg = gen.generate(change, _simple_analysis())
        assert "3 new files" in msg.header

    def test_hint_used_as_subject(self):
        change = Change(
            files=[FileChange("src/app.py", ChangeType.MODIFIED, ["x"])],
            message_hint="Add user authentication flow",
        )
        gen = MessageGenerator()
        msg = gen.generate(change, _simple_analysis())
        assert "add user authentication flow" in msg.header

    def test_subject_truncation(self):
        change = Change(
            files=[FileChange("x.py", ChangeType.MODIFIED)],
            message_hint="x" * 100,
        )
        gen = MessageGenerator(max_subject_length=50)
        msg = gen.generate(change, _simple_analysis())
        assert len(msg.header.split(": ", 1)[1]) <= 50
