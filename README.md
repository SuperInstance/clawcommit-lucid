# Clawcommit Lucid — Intelligent Commit Messages

**Analyze code changes, generate clear conventional commit messages. Stop writing "fix stuff".**

## What This Gives You

- **Change analysis** — parse diffs into structured changes with type classification (added, modified, deleted, renamed, moved)
- **Smart categorization** — automatically categorize changes (feature, fix, refactor, docs, test, chore, perf)
- **Template engine** — conventional commit format with scope, type, and breaking change detection
- **History tracking** — maintain commit history patterns to match project style
- **Conventional format** — `type(scope): description` with optional body and footer

## Quick Start

```bash
pip install clawcommit-lucid
```

```python
from clawcommit_lucid import ChangeAnalyzer, MessageGenerator, CommitHistory

# Analyze a diff
analyzer = ChangeAnalyzer()
changes = analyzer.analyze_diff("""
diff --git a/src/api.py b/src/api.py
+ def new_endpoint():
+     return {"status": "ok"}
- def old_endpoint():
-     pass
""")

# Generate a commit message
generator = MessageGenerator()
message = generator.generate(changes)
print(message)
# "feat(api): add new_endpoint, remove old_endpoint"

# With history context
history = CommitHistory()
history.load(".git/commits.jsonl")
message = generator.generate(changes, history=history)
```

## API Reference

### `Change(path, change_type, additions, deletions)`
### `ChangeType` — `ADDED`, `MODIFIED`, `DELETED`, `RENAMED`, `MOVED`
### `ChangeAnalyzer` — `analyze_diff(diff_text) → list[FileChange]`
### `ChangeCategory` — `FEATURE`, `FIX`, `REFACTOR`, `DOCS`, `TEST`, `CHORE`, `PERF`
### `MessageGenerator` — `generate(changes, history=None) → str`
### `TemplateEngine` — Custom conventional commit templates
### `CommitHistory` — Load and query past commit patterns

## How It Fits

The commit quality tool for the [SuperInstance fleet](https://github.com/SuperInstance). Every fleet repo uses Clawcommit Lucid for consistent, informative commit messages.

- **[cocapn-cli](https://github.com/SuperInstance/cocapn-cli)** — Terminal formatting (Rust)
- **[cicd-agent](https://github.com/SuperInstance/cicd-agent)** — CI/CD pipeline (validates commit format)
- **[co-captain-git-agent](https://github.com/SuperInstance/co-captain-git-agent)** — Human liaison (generates commits)

## Testing

```bash
pytest tests/
```

## Installation

```bash
pip install clawcommit-lucid
```

Python 3.10+. MIT license.
