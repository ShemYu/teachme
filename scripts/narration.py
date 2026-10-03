"""Narration: per-sentence TTS with a shared on-disk cache, used by both the player and the MP4.

Backends: "say" (macOS, free, default) and "elevenlabs" (billed per character). The cache key covers backend, voice,
model, settings and text, so switching voices never mixes audio and editing one sentence re-synthesizes (and, on a
paid backend, re-bills) only that sentence.
"""
import hashlib, json, os, re, subprocess, time, wave
from concurrent.futures import ThreadPoolExecutor
from common import LessonError, readable

HZ = 24000                                   # every backend renders 16-bit mono PCM at this rate
GAP_SENT, GAP_STEP, GAP_SLIDE, LEAD, TAIL = 0.28, 0.55, 1.0, 0.4, 1.5

# ElevenLabs pay-as-you-go list prices, USD per 1,000 characters (elevenlabs.io/pricing/api, checked 2026-10-03).
# Only used for the pre-flight estimate; subscription plans bill the same characters against monthly credits.
ELEVEN_USD_PER_1K = {"eleven_v4": 0.08, "eleven_v4_turbo": 0.04, "eleven_v3": 0.08, "eleven_multilingual_v2": 0.08,
                     "eleven_flash_v2_5": 0.04, "eleven_flash_v2": 0.04, "eleven_turbo_v2_5": 0.04}
ELEVEN_DEFAULTS = {"voice_id": "XrExE9yKIg1WjnnlVkGX",  # "Matilda" (premade, educational); see scripts/tts_voices.py
                   "model": "eleven_multilingual_v2",
                   "settings": {"stability": 0.5, "similarity_boost": 0.75, "style": 0.0, "speed": 1.0}}


class Narrator:
    """Per-sentence TTS with a shared on-disk cache (build/tts), used by both the player and the MP4.

    Backends: "say" (macOS, free, default) and "elevenlabs" (billed per character; key resolved through the
    secret registry in secret_store.py: env ELEVENLABS_API_KEY, then the OS keychain).
    The cache key includes backend + voice + model + settings + text, so switching voices never mixes audio,
    and editing one sentence re-synthesizes (and re-bills) only that sentence."""

    def __init__(self, lesson, backend=None):
        self.L = lesson
        self.backend = backend or os.environ.get("TEACHME_TTS") or lesson.tts
        self.dir = os.path.join(lesson.build, "tts"); os.makedirs(self.dir, exist_ok=True)
        if self.backend == "say":
            self.ident, self.jobs = f"{lesson.voice}|{lesson.rate}", 6       # same key as v0.3 caches
        elif self.backend == "elevenlabs":
            if any("key" in k.lower() for k in lesson.eleven):
                raise LessonError("lesson.py must not contain an API key (it would end up in git). "
                         "Run scripts/keys.py set to store it with a secret backend.")
            cfg = {**ELEVEN_DEFAULTS, **lesson.eleven}
            from secret_store import ELEVENLABS, get_secret
            self.key, self.key_source = get_secret(ELEVENLABS)
            if not self.key:
                raise LessonError("ElevenLabs selected but no API key found. Run `.venv/bin/python scripts/keys.py set` "
                         "(hidden prompt or dialog → secret backend), or export ELEVENLABS_API_KEY. Or build with --tts say.")
            self.voice_id = os.environ.get("ELEVENLABS_VOICE_ID") or cfg["voice_id"]
            self.model = os.environ.get("ELEVENLABS_MODEL") or cfg["model"]
            self.settings = {**ELEVEN_DEFAULTS["settings"], **cfg.get("settings", {})}
            self.ident = "11|" + "|".join([self.voice_id, self.model, json.dumps(self.settings, sort_keys=True)])
            self.jobs = int(os.environ.get("ELEVENLABS_CONCURRENCY", "2"))  # free/starter tiers allow few parallel requests
        else:
            raise LessonError(f"unknown TTS backend {self.backend!r}: use 'say' or 'elevenlabs'")

    def path(self, text):
        h = hashlib.sha1(f"{self.ident}|{text}".encode()).hexdigest()[:10]
        return os.path.join(self.dir, re.sub(r"[^a-z0-9]+", "-", text.lower())[:60] + "-" + h + ".wav")

    def spoken(self, text):
        # Spelled acronyms ("A I", "O C R") help `say`; neural voices read "AI", "OCR" correctly as written.
        return readable(text) if self.backend == "elevenlabs" else text

    def estimate(self, texts):
        """(new sentences, new characters, est. USD) for sentences not in the cache."""
        new = sorted({t for t in texts if not os.path.exists(self.path(t))})
        chars = sum(len(self.spoken(t)) for t in new)
        usd = chars / 1000 * ELEVEN_USD_PER_1K.get(getattr(self, "model", ""), 0.08) if self.backend == "elevenlabs" else 0.0
        return len(new), chars, usd

    def preflight(self, texts, max_chars, estimate_only=False):
        """Print what this build will synthesize; refuse to spend past max_chars. Returns False if estimate_only."""
        n, chars, usd = self.estimate(texts)
        total = sum(len(self.spoken(t)) for t in set(texts))
        if self.backend == "elevenlabs":
            print(f"TTS elevenlabs · model {self.model} · voice {self.voice_id}\n"
                  f"  {n} new sentences, {chars:,} characters to synthesize (lesson total {total:,}); "
                  f"≈ ${usd:.2f} at pay-as-you-go list price, or {chars:,} plan credits")
            from elevenlabs_api import subscription, voice_name
            name = voice_name(self.key, self.voice_id)
            if name is None:
                raise LessonError(f"  voice {self.voice_id} is not available to this key: pick one from scripts/tts_voices.py "
                         "and set ELEVENLABS['voice_id'] in lesson.py (or ELEVENLABS_VOICE_ID)")
            print(f"  voice: {name}")
            try:
                sub = subscription(self.key)
            except ValueError as e:
                raise LessonError(f"  {e} (key from {self.key_source})")
            if sub and sub.get("limit") is not None:
                left = sub["limit"] - sub["used"]
                print(f"  plan {sub['tier']}: {left:,} of {sub['limit']:,} characters left this period")
                if chars > left and not estimate_only:
                    raise LessonError("  not enough plan characters left for this build")
            if chars > max_chars and not estimate_only:
                raise LessonError(f"  over the budget cap of {max_chars:,} characters: raise --max-chars to proceed")
        else:
            print(f"TTS say · voice {self.L.voice} · {n} new sentences ({chars:,} characters), free")
        return not estimate_only

    def synth_all(self, texts):
        todo = sorted({t for t in texts if not os.path.exists(self.path(t))})
        with ThreadPoolExecutor(self.jobs) as ex:
            list(ex.map(self._synth, todo))

    def pcm(self, text):
        if not os.path.exists(self.path(text)):
            self._synth(text)
        with wave.open(self.path(text)) as w:
            return w.readframes(w.getnframes())

    def _synth(self, text):
        out = self.path(text); tmp = out + ".part"
        if self.backend == "say":
            subprocess.run(["say", "-v", self.L.voice, "-r", str(self.L.rate), "-o", tmp, f"--data-format=LEI16@{HZ}",
                            "--file-format=WAVE", text], check=True)
        else:
            pcm = self._eleven(self.spoken(text))
            with wave.open(tmp, "wb") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(HZ); w.writeframes(pcm)
        os.replace(tmp, out)   # only complete files enter the cache, so an aborted run never leaves half-billed junk

    def _eleven(self, text):
        import urllib.request, urllib.error
        body = json.dumps({"text": text, "model_id": self.model, "voice_settings": self.settings,
                           "seed": 7}).encode()
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}?output_format=pcm_{HZ}"
        for attempt in range(6):
            req = urllib.request.Request(url, body, {"xi-api-key": self.key, "Content-Type": "application/json",
                                                     "Accept": "audio/pcm"})
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    return r.read()
            except urllib.error.HTTPError as e:
                msg = e.read().decode("utf-8", "replace")[:300]
                if e.code in (429, 500, 502, 503) and attempt < 5:
                    time.sleep(2 ** attempt); continue
                raise LessonError(f"ElevenLabs error {e.code} for {text[:50]!r}: {msg}")
            except urllib.error.URLError as e:
                if attempt < 5:
                    time.sleep(2 ** attempt); continue
                raise LessonError(f"ElevenLabs unreachable: {e}")


def add_tts_args(ap):
    ap.add_argument("--tts", choices=["say", "elevenlabs"], help="TTS backend (default: lesson TTS setting, else say)")
    ap.add_argument("--max-chars", type=int, default=30000,
                    help="refuse to send more than this many new characters to a paid TTS backend (default 30000)")
    ap.add_argument("--estimate", action="store_true", help="print what TTS would synthesize and cost, then exit")
