import os, textwrap
import pytest

from common import Lesson, LessonError
from narration import Narrator


@pytest.fixture
def lesson(tmp_path):
    (tmp_path / "lesson.py").write_text('SLIDES = [("", "<h2>x</h2>", ["Hello A I world."])]\n')
    return Lesson(tmp_path)


def test_say_cache_key_is_stable_across_versions(lesson):
    # v0.3 caches were keyed by sha1("Samantha|182|text"); changing this re-synthesizes every lesson
    n = Narrator(lesson, "say")
    assert os.path.basename(n.path("Hi.")).startswith("hi-") and n.path("Hi.") == Narrator(lesson, "say").path("Hi.")
    assert n.path("Hi.") != n.path("Hi!")


def test_elevenlabs_needs_a_key(lesson, monkeypatch):
    monkeypatch.setenv("TEACHME_SECRET_BACKENDS", "env")
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    with pytest.raises(LessonError, match="no API key"):
        Narrator(lesson, "elevenlabs")


def test_elevenlabs_text_and_cache_identity(lesson, monkeypatch):
    monkeypatch.setenv("TEACHME_SECRET_BACKENDS", "env")
    monkeypatch.setenv("ELEVENLABS_API_KEY", "sk_" + "x" * 30)
    n = Narrator(lesson, "elevenlabs")
    assert n.spoken("Hello A I world.") == "Hello AI world."
    assert n.path("Hi.") != Narrator(lesson, "say").path("Hi.")       # voices never share audio
    new, chars, usd = n.estimate(["Hello A I world."])
    assert (new, chars) == (1, len("Hello AI world.")) and usd > 0


def test_key_in_lesson_file_is_refused(tmp_path, monkeypatch):
    (tmp_path / "lesson.py").write_text('SLIDES = [("", "<h2>x</h2>", ["Hi."])]\nELEVENLABS = {"api_key": "sk_123"}\n')
    with pytest.raises(LessonError, match="must not contain an API key"):
        Narrator(Lesson(tmp_path), "elevenlabs")


def test_unknown_backend(lesson):
    with pytest.raises(LessonError, match="unknown TTS backend"):
        Narrator(lesson, "festival")


def test_lesson_without_slides(tmp_path):
    (tmp_path / "lesson.py").write_text("SLIDES = []\n")
    with pytest.raises(LessonError, match="defines no SLIDES"):
        Lesson(tmp_path)
