"""SOURCES.md: lessons list every claim with its source; a missing or unedited file gets a one-line hint."""
import os, shutil

import pytest

from common import Lesson, SKILL, sources_note

TEMPLATE = os.path.join(SKILL, "references", "sources-template.md")


def make(tmp_path, sources=None):
    (tmp_path / "lesson.py").write_text('SLIDES = [("", "<h2>x</h2>", ["Hi."])]\n')
    if sources is not None:
        (tmp_path / "SOURCES.md").write_text(sources)
    return Lesson(tmp_path)


def test_lesson_finds_sources_next_to_lesson_py(tmp_path):
    assert make(tmp_path).sources is None
    assert make(tmp_path, "x").sources == str(tmp_path / "SOURCES.md")


def test_missing_sources_get_a_hint_pointing_at_the_template(tmp_path):
    note = sources_note(make(tmp_path))
    assert "no SOURCES.md" in note and "references/sources-template.md" in note and os.path.exists(TEMPLATE)


def test_an_unedited_template_is_flagged(tmp_path):
    assert "still the template" in sources_note(make(tmp_path, open(TEMPLATE).read()))


def test_a_table_without_claims_is_flagged(tmp_path):
    header_only = "# Sources: T\n\n| Claim | Source | Scope |\n|---|---|---|\n"
    assert "no claim rows" in sources_note(make(tmp_path, header_only))


def test_a_filled_file_passes(tmp_path):
    filled = open(TEMPLATE).read().replace("<lesson title>", "Raft leader election")
    assert sources_note(make(tmp_path, filled)) is None
