# teachme

A [Claude Code](https://claude.com/claude-code) skill that turns a technical topic into a **narrated study lesson**. Ask Claude to teach you something and you get:

- **An MP4**: 1080p slides with step-by-step reveals, narration, and soft subtitles. It plays anywhere, including on your phone.
- **A focus player** (`index.html` + `narration.m4a`): the same lesson, but as each sentence is spoken a ring glides to the exact table row, code line, or card being discussed and everything else dims. It has sentence-level seeking, speed control, chapters, and captions, plus a **presenter mode** with a separate notes window for rehearsing a talk.

Lessons are written in a **visual-proof style** inspired by 3Blue1Brown. The slides show the mechanism rather than describe it: one picture reused across problems, proofs revealed one change of state at a time, and fixed colour meanings. Code on slides is pulled from a `solutions.py` that is tested against brute force, so what's on screen is code that ran.

> **Scope:** study lessons only. For release videos, demos, promos, or social clips, use a different tool. The skill is written to stay out of those requests.

## Requirements

- macOS (the default voice is the built-in `say`) and Google Chrome (used headless to render slides)
- Python 3.9+
- Optional: an [ElevenLabs](https://elevenlabs.io) API key for a neural voice

## Install

```bash
git clone https://github.com/ShemYu/teachme ~/.claude/skills/teachme
~/.claude/skills/teachme/scripts/setup.sh        # .venv with ffmpeg + Pillow
```

Then, in Claude Code: *"Teach me how Raft leader election works, as a video."* Claude designs the lesson, writes `lesson.py` and `focus_cues.py`, checks the layout and spotlight placement, and renders both outputs.

## Build a lesson by hand

```bash
.venv/bin/python scripts/build_video.py  lessons/<name> --preview      # layout contact sheets
.venv/bin/python scripts/build_player.py lessons/<name> --validate     # focus player + selector check
.venv/bin/python scripts/build_video.py  lessons/<name>                # MP4
```
Outputs go to `lessons/<name>/build/` (git-ignored). Lessons are Python files, so only build lessons you trust.

## Optional: ElevenLabs voice

```bash
.venv/bin/python scripts/keys.py set                                       # hidden prompt, or a native dialog when an agent runs it
.venv/bin/python scripts/build_player.py lessons/<name> --tts elevenlabs --estimate    # characters, ≈ USD, plan left; spends nothing
.venv/bin/python scripts/build_player.py lessons/<name> --tts elevenlabs               # synthesizes once into a per-sentence cache
.venv/bin/python scripts/build_video.py  lessons/<name> --tts elevenlabs               # the MP4 reuses that cache: billed once
```

Paid builds stop at `--max-chars` (default 30,000), when your plan is out of characters, or when the voice isn't available to your key. Rebuilds only bill sentences whose text changed.

### Keys stay out of the repo and the chat

Secrets resolve through a small registry (`scripts/secret_store.py`): `env` (`ELEVENLABS_API_KEY`, read-only) → `keychain` (macOS) → `secret-tool` (Linux Secret Service). `keys.py set` asks for the key with a hidden terminal prompt. When a coding agent such as Claude Code runs it, there's no terminal to type into, so it opens a native password dialog instead and the agent only sees `saved sk_…abcd`. Keys are never written to files, passed on a command line, or printed in full, and a key placed in `lesson.py` is refused.

To add a store (1Password, Vault, a cloud secret manager…), subclass `SecretBackend`, decorate it with `@register`, and add its name to the lookup order (`TEACHME_SECRET_BACKENDS=env,keychain,…`). The module docstring has a complete example. Input methods are registered the same way in `scripts/keys.py`.

## What a lesson costs

Measured on one real lesson: *Coding interview patterns*, 21 slides, 241 narrated sentences, 19 minutes of video.

| Stage | Time | Cost |
|---|---|---|
| Claude authoring (design, slides, narration, focus cues, layout checks) | ~15–20 min | ≈ $2.50 at API rates for Claude Opus 5.5¹ |
| Narration with macOS `say` | 1.5 min | free |
| Narration with ElevenLabs (`eleven_multilingual_v2`, 17,210 characters) | 2.6 min | ≈ $1.38 at pay-as-you-go list price² |
| Render MP4 (57 clips) and build the focus player | ~3 min | free |

¹ Token usage from the Claude Code session transcript for a comparable 16-slide lesson: 22 model calls, 56k output, 123k cache-write, and 1.8M cache-read tokens, priced at $20 / $8 / $0.20 per million (Opus 5.5 with a 1-hour cache). On a Claude Pro or Max plan this counts against your usage limits instead of being billed per token.
² `--estimate` prints the exact figure for your lesson before anything is billed.

## Layout

| Path | What |
|---|---|
| `SKILL.md` | Instructions Claude follows, including when not to trigger |
| `references/authoring.md` | Slide API, theme and visual-proof components, narration and focus-cue rules |
| `scripts/build_video.py`, `scripts/build_player.py` | MP4 and focus-player builders |
| `scripts/common.py`, `scripts/narration.py` | Lesson loading, Chrome/ffmpeg helpers; TTS backends and cache |
| `scripts/visuals.py` | Visual-proof components: tested code panels, arrays with pointers, trace frames, pair grid, intervals |
| `scripts/secret_store.py`, `scripts/keys.py`, `scripts/elevenlabs_api.py`, `scripts/tts_voices.py` | Secrets registry and CLI, ElevenLabs helpers |
| `assets/theme.css`, `assets/player.html` | Slide theme and the player template |
| `lessons/<name>/` | Example lessons (`lesson.py`, `focus_cues.py`, optional `solutions.py`) |
| `tests/` | Unit tests (`pytest -q tests`; no Chrome, `say`, or network needed) |
| `evals/evals.json` | Trigger and quality prompts for iterating on the skill |

## Example lessons

| Lesson | Runtime | Shows |
|---|---|---|
| `agentic-video-understanding` | ~16.5 min | Reference example |
| `coding-interview-patterns` | ~18 min | Visual-proof style: pair grid, trace frames, interval bars, tested `solutions.py` |
| `hybridrag-vs-wikirag` | ~16 min | Tradeoff matrix and decision framework |
| `agent-security-observability` | ~17 min | Interview-prep format: one prompt worked end to end |
| `agent-system-design` | ~15.5 min | Agent architecture around a ticket-to-PR coding agent |

## Contributing and versioning

See [CONTRIBUTING.md](CONTRIBUTING.md). `VERSION` is semver for the skill (scripts, theme, player, SKILL.md). Built MP4s carry it in their `comment` metadata, and the player carries it in its data. Security issues: see [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE)
