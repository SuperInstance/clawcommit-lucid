"""Clawcommit Lucid — Lucid commit message generation from code changes."""

from .change import Change, ChangeType, FileChange
from .analyzer import ChangeAnalyzer, ChangeCategory
from .generator import MessageGenerator
from .template import TemplateEngine
from .history import CommitHistory

__all__ = [
    "Change",
    "ChangeType",
    "FileChange",
    "ChangeAnalyzer",
    "ChangeCategory",
    "MessageGenerator",
    "TemplateEngine",
    "CommitHistory",
]
__version__ = "0.1.0"
