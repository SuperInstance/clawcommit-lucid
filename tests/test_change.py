"""Tests for the change module."""

from clawcommit_lucid.change import Change, ChangeType, FileChange


class TestFileChange:
    def test_extension(self):
        fc = FileChange(path="src/main.py", change_type=ChangeType.MODIFIED)
        assert fc.extension == "py"

    def test_extension_no_dot(self):
        fc = FileChange(path="Makefile", change_type=ChangeType.MODIFIED)
        assert fc.extension == ""  # no dot means no extension

    def test_filename(self):
        fc = FileChange(path="src/utils/helpers.py", change_type=ChangeType.MODIFIED)
        assert fc.filename == "helpers.py"

    def test_lines_count(self):
        fc = FileChange(
            path="a.py",
            change_type=ChangeType.MODIFIED,
            added_lines=["x = 1", "y = 2"],
            removed_lines=["z = 3"],
        )
        assert fc.lines_added == 2
        assert fc.lines_removed == 1

    def test_is_test(self):
        assert FileChange(path="tests/test_foo.py", change_type=ChangeType.MODIFIED).is_test
        assert FileChange(path="test_bar.py", change_type=ChangeType.MODIFIED).is_test
        assert not FileChange(path="src/foo.py", change_type=ChangeType.MODIFIED).is_test

    def test_is_docs(self):
        assert FileChange(path="README.md", change_type=ChangeType.MODIFIED).is_docs
        assert not FileChange(path="src/main.py", change_type=ChangeType.MODIFIED).is_docs

    def test_is_config(self):
        assert FileChange(path="pyproject.toml", change_type=ChangeType.MODIFIED).is_config
        assert FileChange(path=".github/workflows/ci.yml", change_type=ChangeType.MODIFIED).is_config
        assert not FileChange(path="src/main.py", change_type=ChangeType.MODIFIED).is_config

    def test_old_path_for_rename(self):
        fc = FileChange(path="new_name.py", change_type=ChangeType.RENAMED, old_path="old_name.py")
        assert fc.old_path == "old_name.py"


class TestChange:
    def test_totals(self):
        change = Change(files=[
            FileChange("a.py", ChangeType.MODIFIED, ["x"], ["y"]),
            FileChange("b.py", ChangeType.ADDED, ["a", "b"]),
        ])
        assert change.total_added == 3
        assert change.total_removed == 1

    def test_file_filters(self):
        change = Change(files=[
            FileChange("a.py", ChangeType.ADDED),
            FileChange("b.py", ChangeType.REMOVED),
            FileChange("c.py", ChangeType.MODIFIED),
            FileChange("d.py", ChangeType.RENAMED),
        ])
        assert len(change.added_files) == 1
        assert len(change.removed_files) == 1
        assert len(change.modified_files) == 1
        assert len(change.renamed_files) == 1

    def test_from_diff_simple(self):
        diff = """diff --git a/hello.py b/hello.py
index 1234567..abcdefg 100644
--- a/hello.py
+++ b/hello.py
@@ -1,3 +1,4 @@
 import os
+import sys

 def main():
"""
        change = Change.from_diff(diff)
        assert len(change.files) == 1
        assert change.files[0].path == "hello.py"
        assert change.files[0].lines_added == 1
        assert change.files[0].lines_removed == 0

    def test_from_diff_multiple_files(self):
        diff = """diff --git a/a.py b/a.py
--- a/a.py
+++ b/a.py
@@ -1 +1 @@
-old
+new
diff --git a/b.py b/b.py
new file mode 100644
--- /dev/null
+++ b/b.py
@@ -0,0 +1,3 @@
+line1
+line2
+line3
"""
        change = Change.from_diff(diff)
        assert len(change.files) == 2
        assert change.files[0].path == "a.py"
        assert change.files[0].change_type == ChangeType.MODIFIED
        assert change.files[1].path == "b.py"
        assert change.files[1].change_type == ChangeType.ADDED
        assert change.files[1].lines_added == 3

    def test_from_diff_deleted_file(self):
        diff = """diff --git a/old.py b/old.py
deleted file mode 100644
--- a/old.py
+++ /dev/null
@@ -1,2 +0,0 @@
-removed line 1
-removed line 2
"""
        change = Change.from_diff(diff)
        assert len(change.files) == 1
        assert change.files[0].change_type == ChangeType.REMOVED
        assert change.files[0].lines_removed == 2

    def test_from_diff_empty(self):
        change = Change.from_diff("")
        assert len(change.files) == 0
