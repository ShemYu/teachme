"""Pure-Python tests: no Chrome, no `say`, no network. Run with `pytest -q`."""
import json, os, textwrap
import pytest

from common import Lesson, LessonError, sentences, readable
from build_video import ts, concat_line, page
from build_player import cue_list, script_json, resolve_cue, wrap_pre_lines


def write_lesson(tmp_path, steps, cues=None):
    (tmp_path / "lesson.py").write_text(textwrap.dedent(f'''
        TITLE = "T"
        SLIDES = [("", "<h2>Hi</h2><p class='s1'>x</p>", {steps!r})]
    '''))
    if cues is not None:
        (tmp_path / "focus_cues.py").write_text(f"CUES = {cues!r}\n")
    return Lesson(tmp_path)


def test_sentences_split_on_terminal_punctuation():
    assert sentences("One. Two? Three! Four") == ["One.", "Two?", "Three!", "Four"]
    assert sentences("Version 2.1 is fine.") == ["Version 2.1 is fine."]   # no space after the dot


def test_readable_joins_spelled_acronyms_only():
    assert readable("Applied A I and O C R, I think.") == "Applied AI and OCR, I think."


@pytest.mark.parametrize("t,expected", [(0, "00:00:00,000"), (59.9996, "00:01:00,000"), (3661.5, "01:01:01,500")])
def test_srt_timestamps_carry_rounding(t, expected):
    assert ts(t) == expected


def test_concat_line_escapes_quotes():
    assert concat_line("/a/it's.mp4") == "file '/a/it'\\''s.mp4'\n"


def test_script_json_cannot_close_script_tag():
    out = script_json({"html": "<b>x</b></script><script>alert(1)</script>"})
    assert "</script>" not in out and json.loads(out)["html"].endswith("</script>")


def test_page_hides_future_steps_beyond_16(tmp_path):
    L = write_lesson(tmp_path, [f"Step {i}." for i in range(20)])
    html = page(L, 0, 0)
    assert ".s19{visibility:hidden}" in html and ".s0{" not in html


def test_cue_list_default_and_alignment(tmp_path):
    L = write_lesson(tmp_path, ["First. Second.", "Third."])
    cues = cue_list(L)
    assert [c["sel"] for c in cues] == ["", "", ".s1"]
    L = write_lesson(tmp_path, ["First. Second.", "Third."], cues={"0.0": ["h2"]})
    with pytest.raises(LessonError, match="0.0: 1 selectors for 2 sentences"):
        cue_list(L)


def test_resolve_cue(tmp_path):
    cues = cue_list(write_lesson(tmp_path, ["A. B.", "C."]))
    assert resolve_cue("0.1.0", cues) == 2 and resolve_cue("1", cues) == 1
    with pytest.raises(LessonError):
        resolve_cue("9.9.9", cues)


def test_wrap_pre_lines_keeps_blank_lines_targetable():
    assert wrap_pre_lines("<pre>a\n\nb</pre>").count('class="ln"') == 3


def test_missing_lesson_is_a_clear_error(tmp_path):
    with pytest.raises(LessonError, match="no lesson.py"):
        Lesson(tmp_path / "nope")


def test_lessons_resolve_by_name_and_examples_build_outside_the_skill(tmp_path, monkeypatch):
    import common
    home = tmp_path / "home"; (home / "mine").mkdir(parents=True)
    (home / "mine" / "lesson.py").write_text('SLIDES = [("", "<h2>x</h2>", ["Hi."])]\n')
    monkeypatch.setenv("TEACHME_LESSONS", str(home))
    L = Lesson("mine")                                   # bare name → lessons home
    assert L.dir == str(home / "mine") and L.build == str(home / "mine" / "build")
    ex = Lesson("coding-interview-patterns")             # bundled example → read-only; builds go to the home
    assert ex.dir.startswith(common.SKILL)
    assert ex.build == str(home / "examples" / "coding-interview-patterns" / "build")
    assert not os.path.exists(os.path.join(ex.dir, "build"))


def test_player_respects_prefers_reduced_motion():
    css = open(os.path.join(os.path.dirname(__file__), "..", "assets", "player.html"), encoding="utf-8").read()
    block = css[css.index("@media (prefers-reduced-motion: reduce)"):].split("\n")[0]
    assert "#ring{transition:none" in block and "#ring.on{animation:none" in block and ".frame *" in block
