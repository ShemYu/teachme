"""Captions: burned-in chunking and timing, the caption page, and the shipped SRT. No Chrome, `say`, or ffmpeg needed."""
import math, sys, textwrap

import pytest

import build_video as bv
from common import Lesson

COMMA = ("The first candidate asks every other server for a vote in its new term, and each server grants at most one "
         "vote per term to whoever asks first.")
LONG = COMMA[:-1] + ", so two candidates can split the cluster."


def lesson(tmp_path):
    (tmp_path / "lesson.py").write_text(textwrap.dedent('''
        SLIDES = [("", "<h2>Hi</h2><p class='s1'>x</p>", ["One.", "Two."])]
    '''))
    return Lesson(tmp_path)


def test_short_sentence_is_one_caption():
    assert bv.caption_chunks("Timers decide who asks.") == ["Timers decide who asks."]


@pytest.mark.parametrize("n_words", [18, 30, 55, 90])
def test_long_sentences_split_into_chunks_that_fit_two_lines(n_words):
    text = " ".join(f"word{i % 7}x" * (1 + i % 3) for i in range(n_words)).replace("x", "ab")
    chunks = bv.caption_chunks(text, max_chars=96)
    assert all(len(c) <= 96 for c in chunks) and " ".join(chunks) == text
    assert len(chunks) <= math.ceil(len(text) / 90) + 1                       # no needless fragments


def test_chunks_prefer_a_comma_near_the_middle():
    first, second = bv.caption_chunks(COMMA)
    assert first.endswith("term,") and second.startswith("and each server")


def test_balanced_chunks_for_a_sentence_that_needs_two_lines():
    chunks = bv.caption_chunks(LONG)
    assert len(chunks) == 2 and all(len(c) <= 96 for c in chunks) and " ".join(chunks) == LONG


def test_one_endless_word_does_not_hang():
    assert bv.caption_chunks("x" * 300) == ["x" * 300]
    url = "https://example.com/" + "a" * 120
    chunks = bv.caption_chunks(f"See {url} for the details, because the long word has to stay whole on its own line.")
    assert url in chunks and " ".join(chunks).count(url) == 1 and all(len(c) <= 96 for c in chunks if c != url)


def test_caption_track_is_contiguous_covers_the_step_and_shares_time_by_length():
    spans = [("One two three.", 0.0, 1.0), (LONG, 1.28, 7.28)]
    track = bv.caption_track(spans, 8.0)
    assert track[0][1] == 0.0 and track[-1][2] == 8.0
    assert all(a[2] == b[1] for a, b in zip(track, track[1:]))                 # each caption stays up until the next
    assert " ".join(c for c, _, _ in track[1:]) == LONG
    (_, s1, _), (_, s2, e2) = track[1], track[2]
    assert s1 == pytest.approx(1.28) and 1.28 < s2 < 7.28 and e2 == pytest.approx(8.0)


def test_an_empty_step_has_nothing_to_caption():
    assert bv.caption_track([], 0.6) == []


def test_caption_track_shows_acronyms_as_written_not_as_spelled():
    assert bv.caption_track([("Applied A I today.", 0.0, 1.0)], 1.6)[0][0] == "Applied AI today."


def test_caption_page_escapes_text_and_gives_way_to_the_footer(tmp_path):
    L = lesson(tmp_path)
    burned = bv.page(L, 0, 1, caption="Use <b>HTML</b> & more")
    assert 'class="cap"' in burned and "Use &lt;b&gt;HTML&lt;/b&gt; &amp; more" in burned and ".footer{display:none}" in burned
    plain = bv.page(L, 0, 1)
    assert 'class="cap"' not in plain and ".footer{display:none}" not in plain


def test_srt_offsets_steps_joins_acronyms_and_ends_every_cue_with_a_blank_line():
    results = [("a", [("Hello A I.", 0.0, 1.2)], 2.0), ("b", [("Next.", 0.0, 0.5), ("Then.", 0.78, 1.3)], 1.9)]
    assert bv.srt_text(results) == (
        "1\n00:00:00,000 --> 00:00:01,200\nHello AI.\n\n"
        "2\n00:00:02,000 --> 00:00:02,500\nNext.\n\n"
        "3\n00:00:02,780 --> 00:00:03,300\nThen.\n")


def test_burn_subs_is_a_documented_option(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["build_video.py", "--help"])
    with pytest.raises(SystemExit):
        bv.main()
    assert "--burn-subs" in capsys.readouterr().out


def frame_count(path):
    """Frames ffmpeg decodes from the video stream of `path`."""
    import re, subprocess
    from common import FFMPEG
    err = subprocess.run([FFMPEG, "-i", str(path), "-map", "0:v", "-f", "null", "-"], capture_output=True, text=True).stderr
    return int(re.findall(r"frame=\s*(\d+)", err)[-1])


def test_caption_pictures_encode_to_a_steady_30_fps_not_sparse_frames(tmp_path):
    """A concat list of pictures with different durations must come out as steady 30 fps video. Left to itself ffmpeg
    wrote a real lesson as variable-frame-rate video (1,574 frames for 90 s, with gaps of several seconds between
    frames), which seeks and scrubs badly in some players."""
    import wave
    from PIL import Image
    shown = []
    for n, (colour, seconds) in enumerate([((200, 30, 30), 1.0), ((30, 200, 30), 0.5), ((30, 30, 200), 1.2)]):
        png = tmp_path / f"c{n}.png"; Image.new("RGB", (64, 36), colour).save(png); shown.append((png, seconds))
    with open(tmp_path / "frames.txt", "w") as f:
        for png, d in shown:
            f.write(bv.concat_line(str(png)) + f"duration {d:.3f}\n")
        f.write(bv.concat_line(str(shown[-1][0])))
    wav = tmp_path / "a.wav"
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(bytes(2 * 24000 * 3))
    video_in = ["-f", "concat", "-safe", "0", "-i", str(tmp_path / "frames.txt")]
    bv.encode_step(video_in, str(wav), "apad", ["-ac", "1"], 2.7, str(tmp_path / "steady.mp4"), constant_fps=True)
    assert 79 <= frame_count(tmp_path / "steady.mp4") <= 83                              # 2.7 s at 30 fps, every frame present
