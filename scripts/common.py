"""Shared helpers: lesson loading, sentence splitting, headless-Chrome capture, ffmpeg, contact sheets."""
import importlib.util, os, re, shutil, subprocess, sys, tempfile, time

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(SKILL, "assets")
VERSION = open(os.path.join(SKILL, "VERSION")).read().strip()
CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
DEFAULT_VOICE, DEFAULT_RATE = "Samantha", 182



class LessonError(Exception):
    """A problem the user can fix (bad lesson file, missing tool, budget exceeded). CLIs print it and exit 1."""


def run_cli(main):
    """Run a CLI entry point: LessonError → one-line message and exit code 1, no traceback."""
    try:
        main()
    except LessonError as e:
        sys.exit(f"error: {e}")
    except KeyboardInterrupt:
        sys.exit("interrupted")


try:
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    FFMPEG = shutil.which("ffmpeg") or sys.exit("ffmpeg not found: run scripts/setup.sh and use .venv/bin/python")


def theme_css():
    return open(os.path.join(ASSETS, "theme.css")).read()


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Lesson:
    """A lesson directory: lesson.py (required) + focus_cues.py (optional)."""

    def __init__(self, path):
        self.dir = os.path.abspath(path)
        if not os.path.exists(os.path.join(self.dir, "lesson.py")):
            raise LessonError(f"no lesson.py in {self.dir}")
        m = _load(os.path.join(self.dir, "lesson.py"), "lesson")
        self.slides = getattr(m, "SLIDES", None)
        if not self.slides:
            raise LessonError(f"{self.dir}/lesson.py defines no SLIDES")
        self.title = getattr(m, "TITLE", None) or re.sub(r"<[^>]+>", " ", self._first_heading()).strip()
        self.title = re.sub(r"\s+", " ", self.title)
        self.voice = getattr(m, "VOICE", DEFAULT_VOICE)
        self.rate = getattr(m, "RATE", DEFAULT_RATE)
        self.tts = getattr(m, "TTS", "say")                  # "say" or "elevenlabs"
        self.eleven = getattr(m, "ELEVENLABS", {})            # optional {voice_id, model, settings}
        cues = os.path.join(self.dir, "focus_cues.py")
        self.cues = _load(cues, "focus_cues").CUES if os.path.exists(cues) else {}
        self.build = os.path.join(self.dir, "build")
        os.makedirs(self.build, exist_ok=True)

    def _first_heading(self):
        m = re.search(r"<h[12][^>]*>(.*?)</h[12]>", self.slides[0][1], re.S)
        return m.group(1).replace("<br>", " ") if m else "Lesson"


def sentences(text):
    """Split narration into sentences on . ! ? followed by whitespace (so avoid "e.g." in narration)."""
    return [p for p in re.split(r"(?<=[.!?])\s+", text) if p]


def readable(text):
    """Display form of TTS text: spelled acronyms "A I" / "O C R" become "AI" / "OCR"."""
    return re.sub(r"\b(?:[A-Z] )+[A-Z]\b", lambda m: m.group(0).replace(" ", ""), text)


def lesson_sentences(lesson):
    return [s for _, _, steps in lesson.slides for t in steps for s in sentences(t)]


def slide_title(html):
    m = re.search(r"<h[12][^>]*>(.*?)</h[12]>", html, re.S)
    return re.sub(r"<[^>]+>", "", m.group(1).replace("<br>", " ")) if m else ""


def _chrome(url, extra, done, timeout=30):
    """Chrome headless often never exits on macOS: run it, wait for `done()`, then kill it."""
    if not os.path.exists(CHROME):
        raise LessonError(f"Google Chrome not found at {CHROME}; install it or set CHROME=/path/to/chrome")
    prof = tempfile.mkdtemp(prefix="teachme-chrome-")
    p = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
                          "--force-device-scale-factor=1", f"--user-data-dir={prof}", *extra, url],
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    try:
        return done(p, time.time() + timeout)
    finally:
        p.kill(); p.wait(); shutil.rmtree(prof, ignore_errors=True)


def screenshot(url, png, size=(1920, 1080)):
    if os.path.exists(png):
        os.remove(png)
    def done(p, deadline):
        while time.time() < deadline:
            if os.path.exists(png) and os.path.getsize(png) > 0:
                time.sleep(0.4); return
            time.sleep(0.1)
        raise RuntimeError(f"screenshot timed out: {url}")
    _chrome(url, [f"--window-size={size[0]},{size[1]}", "--virtual-time-budget=1500", f"--screenshot={png}"], done)


def dump_dom(url):
    def done(p, deadline):
        out = b""
        os.set_blocking(p.stdout.fileno(), False)
        while time.time() < deadline:
            chunk = p.stdout.read() or b""
            out += chunk
            if b"</html>" in out:
                return out.decode("utf-8", "replace")
            time.sleep(0.1)
        raise RuntimeError(f"dump-dom timed out: {url}")
    return _chrome(url, ["--window-size=1920,1080", "--virtual-time-budget=3000", "--dump-dom"], done)


def file_url(path, query=""):
    return "file://" + os.path.abspath(path) + (f"?{query}" if query else "")


def contact_sheet(pngs, out, cols=2):
    """Tile screenshots into 1920x1080 sheets (4 per sheet) for quick visual review."""
    from PIL import Image
    outs = []
    per = cols * cols
    for g in range(0, len(pngs), per):
        sheet = Image.new("RGB", (1920, 1080), "white")
        w, h = 1920 // cols - 8, 1080 // cols - 4
        for j, p in enumerate(pngs[g:g + per]):
            sheet.paste(Image.open(p).convert("RGB").resize((w, h)), ((j % cols) * (w + 8), (j // cols) * (h + 4)))
        path = out.replace(".png", f"-{g // per}.png")
        sheet.save(path); outs.append(path)
    return outs
