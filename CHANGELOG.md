# Changelog

## 1.3.0 — 2026-10-08

Ideas borrowed from a motion-explainer prompt, after building the same 90-second Raft lesson with it and with teachme.

- Visual: `lanes()`, timers and events on one shared time axis: a lane per actor, bars that end, dashed "will end here" targets, ✓ ✗ ▶ marks, vertical rules, one frame per step like `cluster()`. It makes "which timer ends first, and do two end together" visible, where `cluster()` shows who talks to whom. SKILL.md recommends it for anything that unfolds in time; `references/authoring.md` §6 documents it
- Player: respects `prefers-reduced-motion`: no ring pulse, no crossfades, and the spotlight ring jumps to its target instead of gliding
- SKILL.md: a belief-first lesson shape (Question, Model, Proof, Turn, Payoff) for a lesson that corrects one common belief
- Tests: 89 in total; `lanes()` is covered for scale, carry-over, reset, escaping and authoring mistakes

## 1.2.0 — 2026-10-08

Fixes found by building the same lesson with teachme and with a motion-explainer prompt, then measuring both.

- Loudness: narration is leveled to -16 LUFS (`LUFS` in `lesson.py`; `None` keeps the voice's own level). One constant gain for the whole lesson, a limiter that holds peaks 2 dB under -1.5 dBTP, and stereo output so any meter agrees. The 2 dB is measured, not guessed: the AAC encode adds peaks the limiter cannot see, up to 1.7 dB with 1 dB of headroom depending on how the audio lines up with the codec's frames. Both builders print what they measured on the file they wrote and warn if a peak is over the ceiling. A narration that measured -19.5 LUFS with -0.9 dBTP peaks now lands on -16 LUFS
- Captions: `build_video.py` writes `<name>.srt` beside the MP4, and `--burn-subs` writes `<name>-captions.mp4` with the captions drawn into the picture (chunks of at most two lines, steady 30 fps, the slide footer gives way to them). The default is still a soft subtitle track
- Contrast: the code-comment color moves from `#6b7891` (3.9:1) to `#8493ad` (5.6:1), and so does the presenter-notes control text; `tests/test_theme.py` checks every theme text color against WCAG AA (4.5:1)
- Sources: lessons keep a `SOURCES.md` (template in `references/sources-template.md`) mapping every number and claim to its source. The builds copy it beside the MP4 and into the player folder, and print a note when it is missing or still the template
- Tests: 82, up from 32 (theme contrast, loudness including the encode's true peak across alignments, captions and steady frame rate, sources)

## 1.1.0 — 2026-10-03

- Visual: `cluster()`, a spatial diagram of servers exchanging messages (role colours, term/vote, election-timer ring, log strip, labelled request/grant/reject/heartbeat arrows), one full frame per step so a protocol plays out like an animation in the player. SKILL.md recommends it for distributed and networked systems. Prompted by the with/without benchmark, where the no-skill baseline's spatial diagram read faster than state tables
- Player: elements with class `nodim` are never dimmed by the spotlight (a frame's opaque backdrop no longer lets the previous frame show through)
- Fix: `--validate` could time out on some lessons because headless Chrome stopped writing `--dump-dom` output after one 64 KiB pipe buffer; the DOM now goes to a temp file

## 1.0.1 — 2026-10-03

- Lessons live outside the skill: new lessons go in `~/teachme-lessons/<name>/` (override with `TEACHME_LESSONS`), and every script accepts a lesson path or just its name (lessons home first, then the bundled examples)
- Building a bundled example writes to `~/teachme-lessons/examples/<name>/build/`, so a git-cloned skill folder never collects 100–300 MB build caches or user lessons
- SKILL.md and README updated; test for name resolution and example build location

## 1.0.0 — 2026-10-03

First public release, as **teachme** (previously developed privately as `lesson-video`).

- Engine: narration split into `scripts/narration.py`; recoverable problems raise `LessonError` (one-line message, exit 1) instead of exiting deep inside library code; clear errors for a missing `lesson.py`, empty `SLIDES`, missing Chrome, or an unknown cue id
- Fixes: SRT timestamps no longer drop a second when milliseconds round up; slides with more than 16 steps hide later steps correctly in the MP4; slide HTML containing `</script>` can't break the player; lesson paths with quotes work in the ffmpeg concat list
- `keys.py` uses argparse subcommands (`set`, `check`, `forget`, `backends`)
- Tests: 30 unit tests (`pytest -q tests`) and a GitHub Actions workflow on Python 3.9 and 3.12; `requirements.txt` / `requirements-dev.txt`
- Trigger scope: SKILL.md description now covers study lessons only and explicitly excludes release/launch videos, trailers, demos, promos, social clips, and generic "make a video" requests; evals added for both sides
- Public docs: README with install, ElevenLabs, secrets, and measured per-lesson cost; LICENSE (MIT), SECURITY.md, CONTRIBUTING.md
- Example lesson `coding-interview-patterns` (visual-proof style with a tested `solutions.py`)
- Env vars renamed: `TEACHME_TTS`, `TEACHME_SECRET_BACKENDS`; Keychain service `teachme`

## 0.5.0 — 2026-10-03

- Visual-proof style (3Blue1Brown-inspired, static) is now part of the skill: SKILL.md design guidance (one recurring picture, step-by-step visual proofs, trace frames as motion, fixed colour meanings, reframing slides, code only from a tested `solutions.py`)
- `scripts/visuals.py`: `Solutions` (code + asserts from the lesson's tested `solutions.py`), `panel_code`/`code` (highlighting with marked lines), `arr`, `trow`, `pgrid` (+ `col`/`row`), `ticks`/`ivrow`, `card`
- Theme: visual-proof component styles (`.arr .cell .ptr .trow .tlabel .pg .pc .ivrow .ibar .ticks .axis .code .mk .sm-code`); no existing class names changed
- authoring.md §6 documents the components and their focus-cue selectors

## 0.4.0 — 2026-10-03

- TTS backends: `--tts say|elevenlabs` on both builders (or `TTS` / `ELEVENLABS` in `lesson.py`, `TEACHME_TTS` env). ElevenLabs uses `ELEVENLABS_API_KEY`, renders `pcm_24000`, retries 429/5xx, joins spelled acronyms ("A I" → "AI")
- Budget guard: every build prints new sentences/characters and an ≈ USD estimate; `--estimate` stops there; `--max-chars` (default 30,000) refuses larger paid runs
- MP4 now reuses the player's per-sentence TTS cache (one synthesis, billed once) and gets exact per-sentence subtitle timing, with acronyms shown as "AI"
- Cache writes are atomic (`.part` → rename); `say` cache keys unchanged, so existing lessons rebuild without re-synthesis
- `scripts/tts_voices.py` lists ElevenLabs voices for the key
- Secrets registry (`scripts/secret_store.py`): `Secret` definitions plus pluggable `SecretBackend`s registered by name (`env` read-only, `keychain` macOS via `security -i` stdin, `secret-tool` Linux via stdin). Lookup order `TEACHME_SECRET_BACKENDS` or default; new stores are one decorated class
- `scripts/keys.py set|check|forget|backends`: input methods also registered (`tty` hidden prompt; `macos-dialog` / `zenity` native password dialogs when there's no TTY, so a coding agent can trigger it and only sees the masked result); value checked against the provider before storing; never in argv, shell history, files, or chat
- A key inside `lesson.py` is refused; preflight verifies the voice exists and shows plan characters left, stopping if a build would exceed them
- Default ElevenLabs voice is Matilda (`XrExE9yKIg1WjnnlVkGX`, premade educational); the old `21m00Tcm…` id now resolves to a different voice

## 0.3.0 — 2026-10-01

- Player: **presenter mode** (no audio). Arrow keys / clicker advance point by point (repeated targets collapse), Shift+arrows by slide, Esc exits; `N` opens a notes window (`?notes`) synced over BroadcastChannel with the script, current point highlighted, next step, timer, and pace vs the narrated version. Start screen offers Watch or Present; `?present` opens straight into presenter mode
- Player: captions and notes show readable acronyms ("AI") while TTS keeps its spelling ("A I")
- SKILL.md: guidance for first-person talk lessons built from the user's own evidence
- Theme: `.kpi`, `.h-q`

## 0.2.1 — 2026-09-30

- Theme: `.good-n` (green number in `table.math`)
- Lesson: `agent-system-design` (workflows vs agents, agent loop, tool design, context budget, multi-agent tradeoffs, durable execution, memory, evals, cost, harness code)

## 0.2.0 — 2026-09-30

- Theme: `.chips-row` (inline tag list) and `ol.steps` (two-column numbered steps)
- Lesson: `agent-security-observability` (system design interview prep: threat model, tool gateway, CaMeL-style separation, traces vs audit log, security evals, interview pacing)

## 0.1.1 — 2026-09-29

- Scope: personal study videos only. Description and SKILL.md now exclude LinkedIn, social, promo, and other audience-facing videos (handled by a separate process)
- Evals: learning-framed prompt; added a LinkedIn request as a should-not-trigger case

## 0.1.0 — 2026-09-29

First versioned release, extracted from the prototype that produced the first lesson.

- MP4 pipeline: per-step slide screenshots (headless Chrome), `say` narration, ffmpeg concat, soft subtitles, version in metadata
- Focus player: per-sentence TTS for exact timing; spotlight ring glides to each sentence's target and dims siblings; step reveals fade in; captions, speed, chapters, sentence/slide seeking, keyboard shortcuts
- Player skips dimming inline siblings inside running text (a highlighted phrase no longer leaves the rest of the sentence patchy)
- `build_player.py --validate` (machine-readable selector check via `--dump-dom`) and `--shots slide.step.sentence`
- `build_video.py --preview` contact sheets for layout review
- TTS cache keyed by voice, rate, and text
- Theme: tradeoff-matrix ratings (`.rate-tbl td.g/.m/.b`), highlighted row (`.hlrow`), spectrum bar (`.spectrum`)
- Lessons: `agentic-video-understanding`, `hybridrag-vs-wikirag`
