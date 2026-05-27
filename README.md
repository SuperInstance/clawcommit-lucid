# Clawcommit Lucid

Lucid commit messages — analyze code changes and generate clear, conventional commit messages.

## Installation

```bash
pip install clawcommit-lucid
```

## Quick Start

```python
from clawcommit_lucid import Change, ChangeType, FileChange, ChangeAnalyzer, MessageGenerator

# Describe your changes
change = Change(files=[
    FileChange("src/api/auth.py", ChangeType.ADDED, added_lines=["class Authenticator:", "    pass"]),
    FileChange("src/api/routes.py", ChangeType.MODIFIED, added_lines=["auth = Authenticator()"], removed_lines=["# TODO"]),
])

# Analyze and generate
analyzer = ChangeAnalyzer()
analysis = analyzer.analyze(change)

generator = MessageGenerator()
message = generator.generate(change, analysis)

print(message)
# feat(api): add 2 files
#
#   + src/api/auth.py (+2/-0)
#   + src/api/routes.py (+1/-1)
#   +3 -1 lines
```

## Parsing Diffs

```python
from clawcommit_lucid import Change

diff_text = """diff --git a/hello.py b/hello.py
--- a/hello.py
+++ b/hello.py
@@ -1,3 +1,4 @@
 import os
+import sys
"""

change = Change.from_diff(diff_text)
```

## Templates

```python
from clawcommit_lucid import TemplateEngine

engine = TemplateEngine()
engine.use("emoji")  # ✨ feat messages, 🐛 fix messages, etc.

result = engine.render(change, analysis, subject="add authentication")
# ✨ add authentication
```

Register your own:

```python
from clawcommit_lucid.template import Template

engine.register(Template(name="myteam", pattern="[{type}] {subject}"))
engine.use("myteam")
```

## Style Consistency

```python
from clawcommit_lucid import CommitHistory

history = CommitHistory.from_messages([
    "feat(api): add endpoint",
    "feat(api): add validation",
    "fix(ui): resolve layout issue",
])

profile = history.profile()
print(profile.preferred_types)   # ['feat', 'fix']
print(profile.uses_scopes)       # True
print(profile.common_scopes)     # ['api', 'ui']

# Suggest a type consistent with history
history.suggest_type(["feat", "fix"])  # returns "feat"
```

## API Reference

### `Change(files, message_hint=None)`

A collection of `FileChange` objects. Parse with `Change.from_diff(diff_text)`.

### `FileChange(path, change_type, added_lines, removed_lines, old_path=None)`

A single file's diff. Properties: `extension`, `filename`, `lines_added`, `lines_removed`, `is_test`, `is_docs`, `is_config`.

### `ChangeAnalyzer(custom_keywords=None)`

Categorizes changes into: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `style`, `perf`, `build`, `ci`.

### `MessageGenerator(max_subject_length=72, body_enabled=True)`

Generates `CommitMessage` objects with `header`, `body`, and `footer`.

### `TemplateEngine`

Built-in templates: `conventional`, `conventional-scoped`, `emoji`, `semver`. Add your own with `register()`.

### `CommitHistory(messages=None)`

Track past commits and derive a `StyleProfile` for consistency.

## Development

```bash
pip install -e ".[dev]"
pytest tests/ -q
```

## License

MIT
