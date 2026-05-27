"""Data structures representing file changes and diffs."""

from __future__ import annotations

import enum
import re
from dataclasses import dataclass, field
from typing import List, Optional


class ChangeType(enum.Enum):
    """Kind of modification applied to a file."""

    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    RENAMED = "renamed"


@dataclass
class FileChange:
    """A single file's change within a commit."""

    path: str
    change_type: ChangeType
    added_lines: List[str] = field(default_factory=list)
    removed_lines: List[str] = field(default_factory=list)
    old_path: Optional[str] = None  # set when change_type is RENAMED

    @property
    def extension(self) -> str:
        """Return the file extension (without dot), lowercase."""
        parts = self.path.rsplit(".", 1)
        return parts[-1].lower() if len(parts) > 1 else ""

    @property
    def filename(self) -> str:
        return self.path.rsplit("/", 1)[-1]

    @property
    def lines_added(self) -> int:
        return len(self.added_lines)

    @property
    def lines_removed(self) -> int:
        return len(self.removed_lines)

    @property
    def is_test(self) -> bool:
        lower = self.path.lower()
        return (
            "test" in lower
            or "spec" in lower
            or lower.startswith("tests/")
            or lower.startswith("test/")
        )

    @property
    def is_docs(self) -> bool:
        lower = self.path.lower()
        return lower.endswith(".md") or lower.endswith(".rst") or lower.endswith(".txt") and "readme" in lower

    @property
    def is_config(self) -> bool:
        lower = self.path.lower()
        return lower.endswith((".toml", ".yaml", ".yml", ".json", ".ini", ".cfg")) or self.filename in (
            ".gitignore",
            ".env",
            "dockerfile",
            "makefile",
        )


@dataclass
class Change:
    """A complete set of file changes (analogous to a git diff or commit)."""

    files: List[FileChange] = field(default_factory=list)
    message_hint: Optional[str] = None

    @property
    def total_added(self) -> int:
        return sum(f.lines_added for f in self.files)

    @property
    def total_removed(self) -> int:
        return sum(f.lines_removed for f in self.files)

    @property
    def added_files(self) -> List[FileChange]:
        return [f for f in self.files if f.change_type == ChangeType.ADDED]

    @property
    def removed_files(self) -> List[FileChange]:
        return [f for f in self.files if f.change_type == ChangeType.REMOVED]

    @property
    def modified_files(self) -> List[FileChange]:
        return [f for f in self.files if f.change_type == ChangeType.MODIFIED]

    @property
    def renamed_files(self) -> List[FileChange]:
        return [f for f in self.files if f.change_type == ChangeType.RENAMED]

    @classmethod
    def from_diff(cls, diff_text: str) -> "Change":
        """Parse a unified diff string into a Change object."""
        files: List[FileChange] = []
        current_file: Optional[FileChange] = None
        current_type = ChangeType.MODIFIED

        for line in diff_text.splitlines():
            # New file
            if line.startswith("diff --git"):
                if current_file is not None:
                    files.append(current_file)
                # extract path from "diff --git a/path b/path"
                match = re.match(r"diff --git a/(.*) b/(.*)", line)
                if match:
                    path_b = match.group(2)
                    current_file = FileChange(path=path_b, change_type=ChangeType.MODIFIED)
                else:
                    current_file = None
                current_type = ChangeType.MODIFIED
                continue

            if current_file is None:
                continue

            if line.startswith("new file"):
                current_file.change_type = ChangeType.ADDED
                current_type = ChangeType.ADDED
            elif line.startswith("deleted file"):
                current_file.change_type = ChangeType.REMOVED
                current_type = ChangeType.REMOVED
            elif line.startswith("rename from"):
                old = line[len("rename from "):]
                current_file.change_type = ChangeType.RENAMED
                current_file.old_path = old
            elif line.startswith("+") and not line.startswith("+++"):
                current_file.added_lines.append(line[1:])
            elif line.startswith("-") and not line.startswith("---"):
                current_file.removed_lines.append(line[1:])

        if current_file is not None:
            files.append(current_file)

        return cls(files=files)
