---
name: teachme
description: Narrated study lessons for learning a technical topic yourself — slides with step-by-step visual proofs, macOS or ElevenLabs narration, a 1080p MP4 with subtitles, and a focus-guided player whose spotlight follows each spoken sentence. Use ONLY when the person wants to learn, study, or rehearse something through a lesson video ("teach me X with a video", "make me a lesson on X", "explain X at senior level as a video", "help me prepare for an interview on X"), or wants an existing lesson in lessons/ revised or rebuilt. Do NOT use for any other video, including release or launch videos, trailers, product demos, promos, ads, social clips, announcements, screen recordings, or a generic "make a video" with no learning goal. Those need a different tool.
---

# teachme

Study material for one learner. The goal is understanding, not reach — so favor depth, precise mechanisms, real numbers, and honest tradeoffs over hooks, brevity, or polish for an audience. If the request is really a video for an audience — a release or launch video, trailer, demo, promo, or social clip — this skill is the wrong tool: say so and don't use it, even though it can render video.

Turns a topic into two deliverables from one source of truth:

1. **MP4** — 1080p slides, narrated, soft English subtitles. Plays anywhere, including on a phone for review.
2. **Focus player** — `index.html` + `narration.m4a`. Same content; as each sentence is spoken, a teal ring glides to the exact element being discussed and everything else dims. Sentence-level seeking, speed, chapters, captions. It also has a **presenter mode** (no audio): the user advances point by point with arrows or a clicker while a separate notes window shows their script, the next step, a timer, and pace against the narrated version — for rehearsing and then giving a talk, such as presenting your own project in an interview.

A lesson is a folder with `lesson.py` (slides + narration) and `focus_cues.py` (what to spotlight per sentence).

**Where lessons live:** create new lessons in `~/teachme-lessons/<name>/` (or `$TEACHME_LESSONS/<name>/` if set), never inside the skill folder. The skill may be a git clone that the user updates, and builds are 100–300 MB. Every script accepts a lesson's path or just its name, and looks up names in the lessons home first. `<skill>/lessons/` holds read-only examples: read one before writing a new lesson (`agentic-video-understanding` is the reference, and `coding-interview-patterns` shows the visual-proof components). Building an example writes its output to `~/teachme-lessons/examples/<name>/build/`, not into the skill.

## Setup (once per machine)

```bash
<skill>/scripts/setup.sh          # creates <skill>/.venv with ffmpeg + Pillow
```
Needs macOS (`say`) and Google Chrome. Run every script by full path with the skill's Python: `<skill>/.venv/bin/python <skill>/scripts/<script>.py <name>`. The commands below abbreviate that as `py scripts/…`.

## Voice: `say` (free, default) or ElevenLabs (paid)

Narration defaults to macOS `say`. ElevenLabs is an opt-in upgrade billed per character, so never use it unless the user asks for it, and always show the cost first:
```bash
py scripts/keys.py set                   # no TTY → native password dialog → verified → secret backend
py scripts/build_player.py <name> --tts elevenlabs --estimate   # characters + ≈ USD, spends nothing
py scripts/build_player.py <name> --tts elevenlabs --validate   # synthesizes, capped by --max-chars (default 30000)
py scripts/build_video.py  <name> --tts elevenlabs              # reuses the same audio: billed once
```
- Never ask the user to paste the key into chat, and never write it into any file or command line. If no key is found, tell the user a dialog is about to appear, then run `scripts/keys.py set` yourself (Bash, timeout ≥ 200 s): with no terminal attached it opens a hidden-input macOS dialog, and you only see the masked result ("saved sk_…abcd"). If they cancel, don't retry unasked. `ELEVENLABS_API_KEY` in the environment also works (it wins over stored copies). Storage is a backend registry (`scripts/secret_store.py`); `keys.py backends` shows what this machine supports.
- Report the `--estimate` line (characters, ≈ USD, plan characters left) to the user and get a yes before the first paid build of a lesson. Rebuilds only bill sentences whose text changed. Builds refuse to start if the plan doesn't have enough characters left.
- Per-lesson settings in `lesson.py`: `TTS = "elevenlabs"` and `ELEVENLABS = {"voice_id": ..., "model": ..., "settings": {"stability": ..., "speed": ...}}`. Env vars `ELEVENLABS_VOICE_ID`, `ELEVENLABS_MODEL`, `TEACHME_TTS` override them. `scripts/tts_voices.py` lists the voices on the key.
- Default model `eleven_multilingual_v2` (stable long-form); `eleven_flash_v2_5` is half the price. Spelled acronyms ("A I") are joined back ("AI") for ElevenLabs automatically, so write narration for `say` as usual.

## Workflow

### 1. Design the lesson before writing slides

Decide the audience level, then the **one thesis** the lesson argues — the sentence a viewer should repeat afterwards. Every slide should serve it. For a senior audience this matters more than coverage: seniors want the mechanism, the numbers, the tradeoffs, and the failure modes, not a tour of definitions.

Sketch 12–16 slides. A shape that works:
- Title + agenda → the problem with concrete arithmetic → design space → the thesis
- Architecture → the 3–5 parts that decide quality (one slide each)
- Failure modes → evaluation (including baselines that expose cheating) → production economics
- Code or pseudocode tying it together → recap of 5 takeaways + a hands-on exercise

When the lesson is **the user's own talk** (their project, for an interview they'll give), write narration in first person as their script, and take every claim, number, and attribution from their own sources (notes, repo, claim registers, prior decks) with its stated scope. Never round up a result, merge separate evidence windows, or present in-progress work as done; ask when a needed fact is missing instead of inventing it. Put likely follow-up questions on a final backup slide.

**Show the mechanism; don't just describe it** (visual-proof style, inspired by 3Blue1Brown). It's the default for any topic with a mechanism: algorithms, data structures, protocols, model internals.
- Pick **one recurring picture** and reuse it, so later slides build on what the viewer already reads fluently. Example: a triangle of every pair sum, shown first for brute force, then as the proof that two pointers are safe, then for counting pairs under a budget.
- Prove claims **visually, step by step**. Each step reveals one change of state (a row eliminated, a pointer moved, a window shrunk), and the narration says why that change is safe.
- Use a **trace of frames** (one row per state, revealed in turn) as a stand-in for motion. Keep colour meanings fixed: blue = left pointer, amber = right, teal = current/window, green = hit, red = eliminated.
- Look for a **reframing slide** that turns a new problem into one already solved (subarray sum = k is Two Sum on prefix sums), and show the two side by side.
- Code on slides comes from a tested `solutions.py` next to the lesson (asserts for every on-screen example, plus a brute-force cross-check), pulled in with `visuals.Solutions`. Never hand-copy code onto a slide.
- For systems where things talk to each other (consensus, replication, networking, caches, queues, agents calling tools), draw the actors spatially with `cluster()`: servers on a ring, role colours, and labelled message arrows. Each step is a new frame, so a protocol plays out like an animation. A table of states is precise but slower to read, so use one only beside the diagram when exact values matter.
- Components: `scripts/visuals.py` (see `references/authoring.md` → Visual-proof components). Slides are still static frames, so there's no continuous motion (see ROADMAP for Manim).

When the topic is a choice between approaches, include an explicit **tradeoff matrix** and a **decision framework** slide; state which option you'd pick under which constraints, and why.

Research anything you're unsure of (papers, numbers, what a term currently means) before writing. If a term is ambiguous, say so on screen and pick a definition. Attribute claims to their source by name, and label qualitative judgments as such.

### 2. Write `lesson.py`

Read `references/authoring.md` for the slide API, the layout components in the theme, and narration rules. Key ideas:
- `slide(section, html, *steps)` — each step is one narration paragraph; elements with class `sN` appear at step N.
- Narration is written for the ear: short sentences, acronyms spelled for TTS ("O C R"), numbers in words when they'd be misread.
- Slides hold the structure; narration holds the argument. Don't read the slide aloud.

Then preview layout (final state of every slide, 4 per contact sheet):
```bash
py scripts/build_video.py <name> --preview
```
Look at every sheet. Fix overflow into the footer, text that's too small, empty slides, and elements that never appear because their `sN` exceeds the step count.

### 3. Write `focus_cues.py`

For each `"slide.step"` give one CSS selector per sentence of that step's narration (see `references/authoring.md` → Focus cues). Target the smallest element that matches what the sentence says — a table row, one code line (`pre .ln:nth-child(n)`), one card. `"^"` repeats the previous selector, `""` means no spotlight. Missing steps default to the elements revealed at that step.

### 4. Build, validate, inspect

```bash
py scripts/build_player.py <name> --validate --shots 3.1.0 6.0.4 9.2.1
py scripts/build_video.py <name>
```
- `--validate` fails if any selector matches nothing visible, or if a step's selector count doesn't match its sentence count (the error lists the sentences so you can realign).
- `--shots` renders the player at given cues (`slide.step.sentence`) into `build/shots-*.png`. Look at a spread of them: is the ring on the right thing, tight, and is the dimming readable?

Outputs land in `~/teachme-lessons/<name>/build/`: `<name>.mp4` and `player/` (`index.html` + `narration.m4a`, keep them together). Copy them wherever the user wants (e.g. `~/Downloads/`); never overwrite a file the user may be watching — write a new name instead.

### 5. Report

Tell the user where both outputs are, the runtime, what the lesson covers (one line per section), and what you verified vs. didn't (e.g. layout inspected via screenshots; audio not listened to).

## Iterating on a lesson

Edit `lesson.py` / `focus_cues.py` and rebuild. The player caches TTS per sentence, so small narration edits rebuild fast. When a change to the scripts, theme, or player alters output for all lessons, bump `VERSION`, add a `CHANGELOG.md` entry, and rebuild the example lesson to confirm nothing regressed.
