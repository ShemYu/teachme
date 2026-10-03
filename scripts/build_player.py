"""Build the focus-guided JS player: per-sentence TTS for exact timing, one audio track, one HTML page.

usage: build_player.py LESSON_DIR [--validate] [--shots ID ...] [--out DIR] [--tts say|elevenlabs] [--max-chars N] [--estimate]
  --validate   after building, check every focus selector matches a visible element (exit 1 if not)
  --shots      screenshot the player at the given cue ids ("12" or "slide.step.sentence", e.g. "6.0.5")
"""
import argparse, json, os, re, shutil, subprocess, sys, wave
from common import (Lesson, LessonError, run_cli, theme_css, sentences, slide_title, screenshot, dump_dom, file_url,
                    contact_sheet, FFMPEG, VERSION)
from narration import Narrator, add_tts_args, HZ, GAP_SENT, GAP_STEP, GAP_SLIDE, LEAD, TAIL


def wrap_pre_lines(html):
    """Wrap each <pre> line in <span class="ln"> so cues can target single lines of code."""
    def rep(m):
        return "<pre>" + "".join(f'<span class="ln">{l or "&#8203;"}</span>' for l in m.group(1).split("\n")) + "</pre>"
    return re.sub(r"<pre>(.*?)</pre>", rep, html, flags=re.S)


def cue_list(L):
    cues, errors = [], []
    for i, (_, _, steps) in enumerate(L.slides):
        for k, text in enumerate(steps):
            sents = sentences(text)
            spec = L.cues.get(f"{i}.{k}") or [f".s{k}" if k else ""] * len(sents)
            if len(spec) != len(sents):
                errors.append(f"{i}.{k}: {len(spec)} selectors for {len(sents)} sentences: " +
                              " | ".join(s[:40] for s in sents))
                continue
            prev = ""
            for j, (s, sel) in enumerate(zip(sents, spec)):
                sel = prev if sel == "^" else sel
                prev = sel
                cues.append({"s": i, "k": k, "j": j, "text": s, "sel": sel})
    if errors:
        raise LessonError("focus_cues.py does not line up with the narration:\n  " + "\n  ".join(errors))
    return cues


def script_json(data):
    """JSON safe to inline in <script>: a literal "</script>" inside slide HTML would otherwise end the tag."""
    return json.dumps(data).replace("</", "<\\/")


def build(L, out, nar, cues):
    nar.synth_all([c["text"] for c in cues])        # cached per sentence; shared with build_video.py
    pcm = [nar.pcm(c["text"]) for c in cues]

    sil = lambda sec: b"\x00\x00" * int(sec * HZ)
    buf, t = bytearray(sil(LEAD)), LEAD
    for n, (c, p) in enumerate(zip(cues, pcm)):
        c["t0"] = round(t, 3)
        buf += p; t += len(p) / 2 / HZ
        nxt = cues[n + 1] if n + 1 < len(cues) else None
        gap = TAIL if not nxt else GAP_SLIDE if nxt["s"] != c["s"] else GAP_STEP if nxt["k"] != c["k"] else GAP_SENT
        buf += sil(gap); t += gap
        c["t1"] = round(t, 3)
    os.makedirs(out, exist_ok=True)
    wav = os.path.join(L.build, "narration.wav")
    with wave.open(wav, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(HZ); w.writeframes(bytes(buf))
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", wav, "-c:a", "aac", "-b:a", "80k",
                    os.path.join(out, "narration.m4a")], check=True)

    data = {"title": L.title, "version": VERSION, "tts": nar.backend, "duration": round(t, 3), "cues": cues,
            "slides": [{"section": sec, "title": slide_title(h), "html": wrap_pre_lines(h)} for sec, h, _ in L.slides]}
    tpl = open(os.path.join(os.path.dirname(__file__), "..", "assets", "player.html")).read()
    page = (tpl.replace("/*SLIDE_CSS*/", theme_css()).replace("/*TITLE*/", L.title)
               .replace("/*DATA*/null", script_json(data)))
    index = os.path.join(out, "index.html")
    open(index, "w").write(page)
    print(f"{index}  ({len(cues)} cues, {t / 60:.1f} min, skill v{VERSION})")
    return index, cues


def validate(index):
    html = dump_dom(file_url(index, "validate=1"))
    m = re.search(r'<div id="report">(.*?)</div>', html, re.S)
    if not m:
        raise LessonError("validation report not found in page output")
    report = m.group(1).strip()
    print(report)
    return "unmatched: 0" in report


def resolve_cue(spec, cues):
    if spec.isdigit():
        return int(spec)
    try:
        s, k, j = map(int, spec.split("."))
        return next(n for n, c in enumerate(cues) if (c["s"], c["k"], c["j"]) == (s, k, j))
    except (ValueError, StopIteration):
        raise LessonError(f"no cue {spec!r}: use an index or slide.step.sentence, e.g. 6.0.2")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lesson"); ap.add_argument("--out")
    ap.add_argument("--validate", action="store_true"); ap.add_argument("--shots", nargs="*", default=[])
    add_tts_args(ap)
    a = ap.parse_args()
    L = Lesson(a.lesson)
    cues = cue_list(L)                               # fail on misaligned cues before spending on TTS
    nar = Narrator(L, a.tts)
    if not nar.preflight([c["text"] for c in cues], a.max_chars, a.estimate):
        return
    out = a.out or os.path.join(L.build, "player")
    index, cues = build(L, out, nar, cues)
    ok = True
    if a.validate:
        ok = validate(index)
    if a.shots:
        sdir = os.path.join(L.build, "shots"); shutil.rmtree(sdir, ignore_errors=True); os.makedirs(sdir)
        pngs = []
        for spec in a.shots:
            n = resolve_cue(spec, cues)
            png = os.path.join(sdir, f"cue{n:04d}.png"); screenshot(file_url(index, f"cue={n}"), png); pngs.append(png)
        for s in contact_sheet(pngs, os.path.join(L.build, "shots.png")):
            print(s)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    run_cli(main)
