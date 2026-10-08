"""Narration leveling: one gain for the whole lesson lands on the LUFS target without breaking the peak ceiling.
Uses synthetic speech-like audio and the bundled ffmpeg: no Chrome, `say`, or network."""
import array, math, random, subprocess, wave

import pytest

from common import Lesson, LessonError, FFMPEG, TP_CEIL
from narration import Narrator, HZ, level_filter, measure_loudness, report_loudness, fit_gain, DUAL_MONO


def speech_like(seconds, level, seed, spikes=0):
    """16-bit PCM of noise bursts (two per second) with silence between, `level` = peak amplitude of the bursts (0-1).
    `spikes` adds that many isolated 5x peaks, like the plosives some voices render."""
    rnd = random.Random(seed)
    out = array.array("h")
    for i in range(int(seconds * HZ)):
        env = max(0.0, math.sin(2 * math.pi * 2 * i / HZ))
        out.append(int(max(-1, min(1, rnd.gauss(0, 0.25))) * env * level * 32767))
    for k in range(spikes):
        out[int((k + 0.5) * len(out) / max(spikes, 1))] = int(0.9 * 32767)
    return out.tobytes()


def voiced(seconds, f0=110, seed=1):
    """16-bit PCM of a vowel-like voice: pitched pulses through three formant resonators, with a syllable envelope.
    Unlike noise, it makes the AAC encoder add inter-sample peaks the way real speech does."""
    rnd = random.Random(seed)
    res = []
    for fc, bw in ((700, 90), (1200, 110), (2600, 160)):
        r = math.exp(-math.pi * bw / HZ)
        res.append((2 * r * math.cos(2 * math.pi * fc / HZ), -r * r))
    state, sig = [[0.0, 0.0] for _ in res], []
    for i in range(int(seconds * HZ)):
        x, acc = (1.0 if i % int(HZ / f0) == 0 else 0.0) + rnd.gauss(0, 0.002), 0.0
        for k, (a1, a2) in enumerate(res):
            v = x + a1 * state[k][0] + a2 * state[k][1]
            state[k][1], state[k][0] = state[k][0], v
            acc += v
        sig.append(acc * max(0.0, math.sin(2 * math.pi * 2.2 * i / HZ)) ** 0.7)
    top = max(abs(v) for v in sig)
    return array.array("h", [int(v / top * 0.9 * 32767) for v in sig]).tobytes()


def write_wav(path, pcm):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(HZ); w.writeframes(pcm)


@pytest.fixture
def lesson(tmp_path):
    (tmp_path / "lesson.py").write_text('SLIDES = [("", "<h2>x</h2>", ["One. Two."])]\n')
    return Lesson(tmp_path)


def cached_narrator(lesson, clips):
    """A Narrator whose per-sentence cache already holds `clips` {text: pcm}, so no TTS backend is needed."""
    n = Narrator(lesson, "say")
    for text, pcm in clips.items():
        write_wav(n.path(text), pcm)
    return n


def through_filter(lesson, n, texts, gain):
    """Loudness of the narration as the builders ship it: concatenated, then level_filter(gain)."""
    wav = lesson.build + "/all.wav"
    write_wav(wav, b"".join(n.pcm(t) for t in texts))
    return measure_loudness(wav, level_filter(gain))


def test_level_filter_applies_gain_then_limiter_then_dual_mono():
    f = level_filter(3.5)
    assert f.startswith("volume=3.50dB,alimiter=limit=") and f.endswith(DUAL_MONO)
    ceiling = float(f.split("limit=")[1].split(":")[0])
    assert 20 * math.log10(ceiling) == pytest.approx(TP_CEIL - 2.0, abs=0.01)   # 2 dB of headroom for the peaks AAC adds


@pytest.mark.parametrize("level,spikes", [(0.02, 0), (0.9, 0), (0.1, 6)], ids=["quiet", "hot", "plosives"])
def test_leveling_lands_on_target_and_keeps_peaks_under_ceiling(lesson, level, spikes):
    texts = ["One.", "Two."]
    n = cached_narrator(lesson, {t: speech_like(4, level, seed=i, spikes=spikes) for i, t in enumerate(texts)})
    gain, loud, peak = n.leveling(texts)
    assert abs(loud - lesson.lufs) <= 0.5 and peak <= TP_CEIL
    loud2, peak2 = through_filter(lesson, n, texts, gain)           # measured again from the audio, not from the report
    assert (loud2, peak2) == pytest.approx((loud, peak), abs=0.05)


def test_one_gain_for_all_sentences(lesson):
    """Quiet and loud sentences keep their relative level: leveling is a single gain, not per-sentence normalising."""
    quiet, loud = speech_like(3, 0.02, seed=1), speech_like(3, 0.2, seed=2)
    n = cached_narrator(lesson, {"One.": quiet, "Two.": loud})
    gain, _, _ = n.leveling(["One.", "Two."])
    for name, pcm in (("One.", quiet), ("Two.", loud)):
        write_wav(lesson.build + "/x.wav", pcm)
        before = measure_loudness(lesson.build + "/x.wav", DUAL_MONO)[0]
        after = measure_loudness(lesson.build + "/x.wav", level_filter(gain))[0]
        assert after - before == pytest.approx(gain, abs=0.6)          # same gain (the limiter only shaves peaks)


def test_lufs_none_leaves_the_voice_alone(tmp_path):
    (tmp_path / "lesson.py").write_text('SLIDES = [("", "<h2>x</h2>", ["Hi."])]\nLUFS = None\n')
    assert Narrator(Lesson(tmp_path), "say").leveling(["Hi."]) is None


def test_silent_narration_is_refused(lesson):
    n = cached_narrator(lesson, {"One.": bytes(2 * HZ)})
    with pytest.raises(LessonError, match="silent"):
        n.leveling(["One."])


def test_measure_loudness_reads_a_video_file_and_stereo(tmp_path):
    wav = tmp_path / "a.wav"; write_wav(wav, speech_like(4, 0.5, seed=3))
    mp4 = tmp_path / "a.mp4"
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-f", "lavfi", "-i", "color=c=black:s=64x64:d=4", "-i", str(wav),
                    "-af", DUAL_MONO, "-c:v", "libx264", "-c:a", "aac", "-shortest", str(mp4)], check=True)
    mono = measure_loudness(str(wav))[0]
    assert measure_loudness(str(mp4))[0] == pytest.approx(mono + 3.0, abs=0.3)     # dual mono reads 3 LU above one channel


def encoded_true_peak(tmp_path, pcm, gain, offset_samples):
    """True peak after the AAC encode that the builders use, with the audio shifted against the codec's frames."""
    wav = tmp_path / "in.wav"; write_wav(wav, pcm[2 * offset_samples:])
    m4a = tmp_path / f"out{offset_samples}.m4a"
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", str(wav), "-af", level_filter(gain), "-c:a", "aac", "-b:a", "96k", str(m4a)], check=True)
    return measure_loudness(str(m4a))[1]


def test_the_encoded_file_stays_under_the_ceiling_whatever_the_alignment(lesson, tmp_path):
    """AAC adds inter-sample peaks that depend on how the audio lines up with its 1024-sample frames. The limiter
    headroom has to cover the worst alignment, not the lucky one."""
    pcm = voiced(8)
    wav = tmp_path / "all.wav"; write_wav(wav, pcm)
    gain, _, _ = fit_gain(str(wav), lesson.lufs)
    peaks = [encoded_true_peak(tmp_path, pcm, gain, off) for off in range(0, 2048, 256)]
    assert max(peaks) <= TP_CEIL, peaks


def test_report_loudness_prints_the_measurement_and_warns_over_the_ceiling(tmp_path, capsys):
    hot = tmp_path / "hot.wav"; write_wav(hot, speech_like(3, 0.99, seed=1, spikes=4))
    loud, peak = report_loudness(str(hot), "audio")
    out = capsys.readouterr().out
    assert f"audio: {loud:.1f} LUFS, true peak {peak:.1f} dBTP" in out and "warning" in out
    quiet = tmp_path / "quiet.wav"; write_wav(quiet, speech_like(3, 0.1, seed=1))
    report_loudness(str(quiet), "audio")
    assert "warning" not in capsys.readouterr().out
