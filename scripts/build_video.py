"""Render a lesson to a narrated 1080p MP4 with subtitles.

usage: build_video.py LESSON_DIR [--preview] [--out FILE] [--jobs N] [--burn-subs] [--tts say|elevenlabs] [--max-chars N] [--estimate]
  --preview     only screenshot the final (fully revealed) state of every slide into contact sheets
  --burn-subs   draw the captions into the picture (no soft subtitle track; the footer makes room for them).
                Default: a soft English track in the MP4. Either way the same captions ship as <name>.srt beside it.
The narration is leveled to the lesson's LUFS (default -16, see narration.py) and the MP4 carries it as stereo.
"""
import argparse, html as _html, math, os, shutil, subprocess, wave
from concurrent.futures import ThreadPoolExecutor
from common import (Lesson, run_cli, lesson_sentences, readable, theme_css, screenshot, file_url, contact_sheet,
                    sentences, FFMPEG, VERSION)
from narration import Narrator, add_tts_args, level_filter, report_loudness, HZ, GAP_SENT

PAD = 0.6  # silence after each step

# Burned-in captions: a dark box centred at the bottom of the 1920x1080 canvas, at most two lines (see caption_chunks).
CAP_CSS = (".cap{position:absolute;left:0;top:0;width:1920px;height:1080px;display:flex;align-items:flex-end;"
           "justify-content:center;padding-bottom:34px}"
           ".cap span{max-width:1560px;padding:10px 30px 12px;border-radius:14px;background:rgba(5,7,12,.88);"
           "color:#fff;font-size:40px;font-weight:600;line-height:1.3;text-align:center;border:1px solid #26324a}"
           ".footer{display:none}")


def page(lesson, i, step, caption=None):
    section, html, steps = lesson.slides[i]
    n = len(lesson.slides)
    hide = " ".join(f".s{j}{{visibility:hidden}}" for j in range(step + 1, max(len(steps), 16)))
    footer = "" if i == 0 else (
        f'<div class="footer"><span>{lesson.title}</span><div class="bar"><i style="width:{(i + 1) / n * 100:.1f}%"></i></div>'
        f"<span>{i}/{n - 1}</span></div>")
    sec = f'<div class="section">{section}</div>' if section else ""
    cap = f'<div class="cap"><span>{_html.escape(caption)}</span></div>' if caption else ""
    return (f"<!doctype html><html><head><meta charset='utf-8'><style>{theme_css()}{hide}{CAP_CSS if caption else ''}</style></head>"
            f"<body><div class='frame'>{sec}{html}</div>{footer}{cap}</body></html>")


def ts(t):
    """SRT timestamp. Round to whole milliseconds first, so 59.9996 s becomes 00:01:00,000, not 00:00:59,000."""
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3_600_000); m, ms = divmod(ms, 60_000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def concat_line(path):
    """ffmpeg concat-demuxer entry; single quotes in paths must be escaped as '\\''."""
    return "file '" + path.replace("'", "'\\''") + "'\n"


def caption_chunks(text, max_chars=96):
    """Split a sentence into the fewest chunks of at most max_chars, so a burned-in caption never grows past two
    lines of the caption box. Chunks are balanced in length, and a cut after a comma, semicolon or colon is preferred
    when it costs little. A word longer than max_chars goes on its own chunk."""
    words = text.split()
    if len(text) <= max_chars or len(words) < 2:
        return [text]
    pre = [0]
    for w in words:
        pre.append(pre[-1] + len(w) + 1)
    size = lambda a, b: pre[b] - pre[a] - 1                    # characters of words[a:b] joined by spaces
    inf = float("inf")
    for n in range(math.ceil(len(text) / max_chars), len(words) + 1):
        target = len(text) / n
        cost = [[inf] * (len(words) + 1) for _ in range(n + 1)]; back = [[0] * (len(words) + 1) for _ in range(n + 1)]
        cost[0][0] = 0.0
        for k in range(1, n + 1):
            for b in range(k, len(words) + 1):
                for a in range(k - 1, b):
                    if cost[k - 1][a] == inf or (size(a, b) > max_chars and b - a > 1):
                        continue
                    c = cost[k - 1][a] + (size(a, b) - target) ** 2 - (50 if a and words[a - 1][-1] in ",;:" else 0)
                    if c < cost[k][b]:
                        cost[k][b], back[k][b] = c, a
        if cost[n][len(words)] < inf:
            cuts, b = [], len(words)
            for k in range(n, 0, -1):
                a = back[k][b]; cuts.append((a, b)); b = a
            return [" ".join(words[a:b]) for a, b in reversed(cuts)]
    return [text]


def caption_track(spans, step_dur):
    """[(caption, start, end)] for one step: every sentence span (text, start, end) split into chunks that share its
    time by length. Each caption stays up until the next begins; the last stays until the step ends."""
    if not spans:
        return []                                                  # an empty step: nothing to caption
    starts = []
    for text, a0, a1 in spans:
        chunks = caption_chunks(readable(text))
        total = sum(len(c) for c in chunks)
        pos = 0
        for c in chunks:
            starts.append((c, a0 + (a1 - a0) * pos / total)); pos += len(c)
    starts[0] = (starts[0][0], 0.0)
    ends = [s for _, s in starts[1:]] + [step_dur]
    return [(c, s, e) for (c, s), e in zip(starts, ends)]


def srt_text(results):
    """SRT for the whole video from per-step results [(clip, spans, step_duration)]: each sentence keeps its exact span,
    and steps follow one another on the timeline."""
    cues, t, n = [], 0.0, 1
    for _, spans, dur in results:
        for p, a0, a1 in spans:
            cues.append(f"{n}\n{ts(t + a0)} --> {ts(t + a1)}\n{readable(p)}\n"); n += 1
        t += dur
    return "\n".join(cues)


def encode_step(video_in, wav, audio_filter, audio_channels, dur, out, constant_fps=False):
    """One step's clip: the picture (a looped still, or a concat list of caption pictures) plus its audio, `dur` long.
    A concat list gives pictures with their own durations, which ffmpeg would write as sparse variable-frame-rate video
    (a few frames, long gaps); `constant_fps` repeats frames to a steady 30 fps like the still-image path does."""
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", *video_in, "-i", wav, "-af", audio_filter,
                    "-t", f"{dur:.3f}", "-c:v", "libx264", "-tune", "stillimage", "-crf", "20", "-pix_fmt", "yuv420p",
                    *(["-vf", "fps=30"] if constant_fps else ["-r", "30"]), "-c:a", "aac", "-b:a", "128k", "-ar", "48000",
                    *audio_channels, out], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lesson"); ap.add_argument("--preview", action="store_true")
    ap.add_argument("--out"); ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--burn-subs", action="store_true", help="draw the captions into the picture instead of a soft track")
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
    lv = nar.leveling(lesson_sentences(L)) # one gain for the whole lesson, the same one the player uses
    if lv:
        print(f"leveling: gain {lv[0]:+.1f} dB toward {L.lufs:g} LUFS")
    audio_filter = (level_filter(lv[0]) + ",apad") if lv else "apad"
    audio_channels = [] if lv else ["-ac", "1"]            # leveled audio is already stereo (the voice in both channels)

    def job(args):
        i, k, text = args
        base = os.path.join(work, f"{i:02d}_{k:02d}")
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
        if a.burn_subs:      # one picture per caption chunk, shown for its share of the step; the audio is not cut
            shown = []
            for c, (cap, c0, c1) in enumerate(caption_track(spans, dur) or [(None, 0.0, dur)]):
                open(f"{base}_c{c:02d}.html", "w").write(page(L, i, k, caption=cap))
                screenshot(file_url(f"{base}_c{c:02d}.html"), f"{base}_c{c:02d}.png"); shown.append((f"{base}_c{c:02d}.png", c1 - c0))
            with open(base + "_frames.txt", "w") as f:        # concat demuxer: the last picture is listed twice by design
                for png, d in shown:
                    f.write(concat_line(png) + f"duration {d:.3f}\n")
                f.write(concat_line(shown[-1][0]))
            video_in = ["-f", "concat", "-safe", "0", "-i", base + "_frames.txt"]
        else:
            open(base + ".html", "w").write(page(L, i, k))
            screenshot(file_url(base + ".html"), base + ".png")
            video_in = ["-loop", "1", "-framerate", "30", "-i", base + ".png"]
        encode_step(video_in, base + ".wav", audio_filter, audio_channels, dur, base + ".mp4", constant_fps=a.burn_subs)
        return base, spans, dur

    items = [(i, k, t) for i, (_, _, steps) in enumerate(L.slides) for k, t in enumerate(steps)]
    with ThreadPoolExecutor(a.jobs) as ex:
        results = list(ex.map(job, items))

    srt = srt_text(results)
    open(os.path.join(work, "subs.srt"), "w").write(srt)
    with open(os.path.join(work, "list.txt"), "w") as f:
        f.writelines(concat_line(b + ".mp4") for b, _, _ in results)
    name = os.path.basename(L.dir)
    out = a.out or os.path.join(L.build, name + ("-captions" if a.burn_subs else "") + ".mp4")
    mux = [FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", os.path.join(work, "list.txt")]
    if not a.burn_subs:
        mux += ["-i", os.path.join(work, "subs.srt"), "-map", "0", "-map", "1"]
    mux += ["-c", "copy"]
    if not a.burn_subs:
        mux += ["-c:s", "mov_text", "-metadata:s:s:0", "language=eng"]
    subprocess.run(mux + ["-metadata", f"title={L.title}", "-metadata", f"comment=teachme v{VERSION}",
                          "-movflags", "+faststart", out], check=True)
    srt_out = os.path.splitext(out)[0] + ".srt"
    shutil.copyfile(os.path.join(work, "subs.srt"), srt_out)                       # captions for players that ignore soft tracks
    if L.sources:
        shutil.copyfile(L.sources, os.path.splitext(out)[0] + ".sources.md")       # the audit trail travels with the video
    print(f"{out}  ({sum(d for _, _, d in results) / 60:.1f} min, skill v{VERSION}, {'captions burned in' if a.burn_subs else 'soft subtitles'})")
    print(f"{srt_out}")
    if lv:
        report_loudness(out, "audio")


if __name__ == "__main__":
    run_cli(main)
