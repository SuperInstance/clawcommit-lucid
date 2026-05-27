"""Tests for the template module."""

from clawcommit_lucid.template import TemplateEngine, Template, CONVENTIONAL, EMOJI
from clawcommit_lucid.analyzer import AnalysisResult, ChangeCategory
from clawcommit_lucid.change import Change, ChangeType, FileChange


def _analysis(cat=ChangeCategory.FEAT, scope=None):
    return AnalysisResult(category=cat, scope=scope, confidence=0.9)


def _change():
    return Change(files=[FileChange("x.py", ChangeType.MODIFIED, ["a"])])


class TestTemplate:
    def test_format_basic(self):
        t = Template(name="test", pattern="{type}: {subject}")
        result = t.format(type="feat", subject="add x")
        assert result == "feat: add x"

    def test_format_with_body(self):
        t = Template(name="test", pattern="{type}: {subject}", body_template="{body}")
        result = t.format(type="feat", subject="add x", body="details")
        assert "details" in result


class TestTemplateEngine:
    def test_default_active_is_conventional(self):
        engine = TemplateEngine()
        assert engine.active == "conventional"

    def test_list_templates(self):
        engine = TemplateEngine()
        names = engine.list_templates()
        assert "conventional" in names
        assert "emoji" in names

    def test_switch_template(self):
        engine = TemplateEngine()
        engine.use("emoji")
        assert engine.active == "emoji"

    def test_unknown_template_raises(self):
        engine = TemplateEngine()
        try:
            engine.use("nonexistent")
            assert False, "Should have raised"
        except KeyError:
            pass

    def test_register_custom(self):
        engine = TemplateEngine()
        custom = Template(name="custom", pattern="[{type}] {subject}")
        engine.register(custom)
        engine.use("custom")
        result = engine.render(_change(), _analysis(), "test subject")
        assert result == "[feat] test subject"

    def test_conventional_render(self):
        engine = TemplateEngine()
        result = engine.render(
            _change(), _analysis(scope="core"), "add feature", body="details"
        )
        assert result.startswith("feat(core): add feature")

    def test_emoji_render(self):
        engine = TemplateEngine()
        engine.use("emoji")
        result = engine.render(_change(), _analysis(), "add feature")
        assert "✨" in result

    def test_fix_emoji(self):
        engine = TemplateEngine()
        engine.use("emoji")
        result = engine.render(_change(), _analysis(ChangeCategory.FIX), "fix bug")
        assert "🐛" in result
