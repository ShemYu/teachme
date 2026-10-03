"""Render a lesson to a narrated 1080p MP4 with soft subtitles.

usage: build_video.py LESSON_DIR [--preview] [--out FILE] [--jobs N] [--tts say|elevenlabs] [--max-chars N] [--estimate]
  --preview   only screenshot the final (fully revealed) state of every slide into contact sheets
"""
import argparse, os, subprocess, wave
from concurrent.futures import ThreadPoolExecutor
from common import (Lesson, run_cli, lesson_sentences, readable, theme_css, screenshot, file_url, contact_sheet,
                    sentences, FFMPEG, VERSION)
from narration import Narrator, add_tts_args, HZ, GAP_SENT

PAD = 0.6  # silence after each step


def page(lesson, i, step):
    section, html, steps = lesson.slides[i]
    n = len(lesson.slides)
    hide = " ".join(f".s{j}{{visibility:hidden}}" for j in range(step + 1, max(len(steps), 16)))
    footer = "" if i == 0 else (
        f'<div class="footer"><span>{lesson.title}</span><div class="bar"><i style="width:{(i + 1) / n * 100:.1f}%"></i></div>'
        f"<span>{i}/{n - 1}</span></div>")
    sec = f'<div class="section">{section}</div>' if section else ""
    return (f"<!doctype html><html><head><meta charset='utf-8'><style>{theme_css()}{hide}</style></head>"
            f"<body><div class='frame'>{sec}{html}</div>{footer}</body></html>")


def ts(t):
    """SRT timestamp. Round to whole milliseconds first, so 59.9996 s becomes 00:01:00,000, not 00:00:59,000."""
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3_600_000); m, ms = divmod(ms, 60_000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def concat_line(path):
    """ffmpeg concat-demuxer entry; single quotes in paths must be escaped as '\\''."""
    return "file '" + path.replace("'", "'\\''") + "'\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lesson"); ap.add_argument("--preview", action="store_true")
    ap.add_argument("--out"); ap.add_argument("--jobs", type=int, default=4)
    add_tts_args(ap)
    a = ap.parse_args()
    L = Lesson(a.lesson)
    work = os.path.join(L.build, "video"); os.makedirs(work, exist_ok=True)

    if a.preview:
        pngs = []
        for i, (_, _, steps) in enumerate(L.slides):
            h = os.path.join(work, f"final_{i:02d}.html"); open(h, "w").write(page(L, i, len(steps) - 1))
            png = h.replace(".html", ".png"); screenshot(file_url(h), png); pngs.append(png)
        for s in contact_sheet(pngs, os.path.join(L.build, "preview.png")):
            print(s)
        return

    nar = Narrator(L, a.tts)
    if not nar.preflight(lesson_sentences(L), a.max_chars, a.estimate):
        return
    nar.synth_all(lesson_sentences(L))     # same per-sentence cache as the player: no double billing

    def job(args):
        i, k, text = args
        base = os.path.join(work, f"{i:02d}_{k:02d}")
        open(base + ".html", "w").write(page(L, i, k))
        screenshot(file_url(base + ".html"), base + ".png")
        # step audio = its sentences joined by the player's sentence gap; keep each sentence's exact span for subtitles
        buf, spans, t = bytearray(), [], 0.0
        for n, s in enumerate(sentences(text)):
            if n:
                buf += b"\x00\x00" * int(GAP_SENT * HZ); t += GAP_SENT
            p = nar.pcm(s); d = len(p) / 2 / HZ
            spans.append((s, t, t + d)); buf += p; t += d
        with wave.open(base + ".wav", "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(HZ); w.writeframes(bytes(buf))
        dur = t + PAD
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-loop", "1", "-framerate", "30", "-i", base + ".png",
                        "-i", base + ".wav", "-af", "apad", "-t", f"{dur:.3f}", "-c:v", "libx264", "-tune", "stillimage",
                        "-crf", "20", "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "128k", "-ar", "48000",
                        "-ac", "1", base + ".mp4"], check=True)
        return base, spans, dur

    items = [(i, k, t) for i, (_, _, steps) in enumerate(L.slides) for k, t in enumerate(steps)]
    with ThreadPoolExecutor(a.jobs) as ex:
        results = list(ex.map(job, items))

    srt, t, n = [], 0.0, 1
    for _, spans, dur in results:
        for p, a0, a1 in spans:
            srt.append(f"{n}\n{ts(t + a0)} --> {ts(t + a1)}\n{readable(p)}\n"); n += 1
        t += dur
    open(os.path.join(work, "subs.srt"), "w").write("\n".join(srt))
    with open(os.path.join(work, "list.txt"), "w") as f:
        f.writelines(concat_line(b + ".mp4") for b, _, _ in results)
    out = a.out or os.path.join(L.build, os.path.basename(L.dir) + ".mp4")
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", os.path.join(work, "list.txt"),
                    "-i", os.path.join(work, "subs.srt"), "-map", "0", "-map", "1", "-c", "copy", "-c:s", "mov_text",
                    "-metadata:s:s:0", "language=eng", "-metadata", f"title={L.title}",
                    "-metadata", f"comment=teachme v{VERSION}", "-movflags", "+faststart", out], check=True)
    print(f"{out}  ({t / 60:.1f} min, skill v{VERSION})")


if __name__ == "__main__":
    run_cli(main)
