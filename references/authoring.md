# Authoring reference

## Contents
1. lesson.py API
2. Layout components (theme.css)
3. Narration rules
4. Focus cues
5. Pitfalls seen in practice
6. Visual-proof components (scripts/visuals.py)

## 1. lesson.py API

```python
TITLE = "HybridRAG vs WikiRAG"      # optional; footer + player title (default: first heading)
VOICE, RATE = "Samantha", 182       # optional; any `say -v '?'` voice, words per minute
TTS = "say"                         # optional; "elevenlabs" needs ELEVENLABS_API_KEY (paid, see SKILL.md)
ELEVENLABS = {"voice_id": "...", "model": "eleven_multilingual_v2", "settings": {"speed": 1.0}}  # optional

SLIDES = []
def slide(section, html, *steps):
    SLIDES.append((section, html, list(steps)))

slide("01 · The problem", """
<h2>Heading</h2>
<div class="grid2">
  <div class="panel">always visible</div>
  <div class="panel s1">appears at step 1</div>
</div>
""",
"Step 0 narration. Several sentences.",
"Step 1 narration, spoken while the s1 panel is revealed.",
)
```
- Canvas is 1920×1080, padding 110px sides, 78px top, ~90px bottom reserved for the footer.
- The first slide (index 0) has no footer; use `.title-wrap`, `.kicker`, `h1.big`, `.lede`, `.agenda`.
- `sN` classes: N is 1-based and must be ≤ number of steps − 1. `s0` means always visible.
- Other slides: `section` is the small caps label ("03 · Architecture"), `<h2>` the title.

## 2. Layout components

| Class | Use |
|---|---|
| `.grid2`, `.grid3`, `.cols3` | 2- or 3-column grids |
| `.panel` (+ `.label` heading inside) | bordered box |
| `.card` with `.ic` icon (`.ic.red` for problems); `.card.v` for vertical title+text | callouts; `.stack` wraps a vertical list of cards |
| `ul li` / `li.good` / `li.bad` / `ul.tight` | bullets (green / red dots, smaller) |
| `.thesis` | teal-bordered key statement |
| `.note` | teal footnote line |
| `table.math` + `td.num` | arithmetic walk-through; `.warn` for highlighted numbers |
| `table.tbl` (+ `tr.warnrow`) | comparison tables; header row `<th>` |
| `.loop` > `.node` (+ `.q`, `.dec`, `.a`) and `.arrow` | horizontal flow; `.back` for a loop-back note |
| `.arch` > `.lane` > `.lane-t` + `.row` > `.box` / `.col-boxes` | two-lane architecture diagram; `.box.store`, `.box.agent`, `.box.hlb` accents |
| `.pyramid` > `.lvl.l1..l4` | hierarchy |
| `.timeline-wrap` > `.tl-row` (`.tl-label`, `.tl` > `.seg`, `.tl-note`) | timelines; `.seg.c/.d/.x/.e/.v` colors |
| `.panel.code` > `pre` (`.k .s .n .c .f` spans) ; `.code.wide`, `.tight-code` | code with manual highlighting; each line becomes `.ln` in the player |
| `.formula` | centered monospace equation |
| `ol.recap` | numbered takeaways; `.exercise` box after it |
| inline `<svg>` | small charts; use `var(--accent)` etc. for colors |

For algorithm and mechanism visuals (arrays and pointers, trace frames, pair grid, intervals), use the helpers in §6 instead of hand-writing markup.

Colors: `--accent` (blue), `--teal`, `--warn` (amber), `--red`, `--good`, `--muted`. Add a new component to `assets/theme.css` only if a lesson truly needs it, and note it in CHANGELOG.

Density guide: a slide should hold ≤ ~6 bullets or ≤ 6 cards; body text ≥ 21px. If it doesn't fit, split the slide.

## 3. Narration rules

- ~180 wpm at RATE 182: 2,300–2,800 words ≈ 14–17 minutes.
- Write for the ear. Spell acronyms that TTS mangles: "V L M", "O C R", "R R F", "I o U". Say "one frame per second", not "1 fps".
- Each step's paragraph should open by naming what's appearing ("Design B is…") so the viewer's eye and ear sync even without the spotlight.
- Sentences are split on `. ! ?` followed by whitespace — so "e.g." or "v2.1 " can create accidental splits. Avoid abbreviations with periods in narration.
- Give numbers and sources. "Around three and a half percent" beats "rarely".
- Senior-level voice: claims, mechanisms, tradeoffs, when-to-use, how-it-breaks, how-to-measure.

## 4. Focus cues

`focus_cues.py`:
```python
CUES = {
  "1.0": [".grid2>.panel", "table.math tr:nth-child(1)", "^", ""],
  "6.0": [".code.wide", "pre .ln:nth-child(4)"],
}
```
- Key `"slide.step"`; list length must equal the number of sentences in that step.
- Selectors are scoped to the slide's `.frame`; comma lists are allowed (the ring wraps their union).
- `"^"` = same as previous sentence; `""` = no spotlight (full slide visible).
- Missing key → default `.sN` for step N>0, none for step 0. Fine for simple steps; write explicit cues whenever a step has several elements or one sentence per bullet.
- Code: every `<pre>` line is wrapped as `.ln`, so `pre .ln:nth-child(n+9):nth-child(-n+14)` targets lines 9–14.
- Tables get an implicit `<tbody>`: `table.tbl tr:nth-child(2)` is the first data row when row 1 is the header.
- Only visible (already revealed) elements count; a selector pointing at an element revealed in a later step fails validation.
- Helpers used in the example: `ln(*ns)` and `lnr(a, b)` for code lines.

Presenter mode advances by *point*: consecutive sentences with the same selector collapse into one click, so vary targets where you want the speaker to pause and emphasize.

Aim: the ring should move roughly every sentence or two. A ring parked on a whole slide for a minute tells the viewer nothing.

## 5. Pitfalls seen in practice

- Headless Chrome on macOS doesn't exit after `--screenshot`; `common.py` polls for the file and kills it. Don't "fix" this with a plain subprocess call.
- A table row class like `s3` on a slide with only 3 steps (0–2) never appears. Preview catches it.
- Code blocks overflow the footer at ~21 lines at 23px; use `.tight-code`.
- Narration that says "the survivor" when two survive: re-read narration against the final visual.
- Section labels must use the theme font; shorthand `font:` with `-apple-system` fails in Chrome and falls back to serif.

## 6. Visual-proof components (scripts/visuals.py)

Python helpers that return HTML using theme classes; `lesson.py` can `from visuals import ...` directly (the build runs from `scripts/`). Wrap any piece in an element with class `sN` to reveal it at step N.

| Helper | Draws | Notes |
|---|---|---|
| `Solutions(__file__)` → `.src(name)`, `.body(name)`, `.asserts(name, picks)` | code lines from `solutions.py` next to the lesson | `src` takes a top-level `def`/`class` (docstring dropped); `body` dedents a statements-only `def`; `asserts` takes top-level `assert name(...)` lines |
| `panel_code(lines, mark=(…), cls=)` / `code(lines, mark)` | highlighted `<pre>`; `mark` = 1-based lines with a teal band | add `sm-code` to `cls` for 18.5px when two panels sit side by side |
| `arr(vals, cls={i: 'L'/'R'/'I'/'ok'/'bad'/'gone'}, ptr={i: 'L'/'R'/'i'/'L R'/label}, idx=True)` | array as boxes with pointer labels above and indices below | `.cell` 62px; ≤ 8 cells per row in a half-width column |
| `trow(content, note, label, cls)` | one frame of a state trace (`.trow` > `.tlabel` + picture + `.tnote`) | stack 3–5 frames; reveal with `cls="s2"` … |
| `pgrid(a, ops, cell=80)` | triangle of pair sums `a[i] + a[j]`; cells have classes `cIJ` | ops `(step, kind, cells, label)`: `kill` (red), `acc` (green), `hit`, `probe` (numbered badge). `col(j, rows)` / `row(i, cols)` build cell lists |
| `ticks(n, unit)` + `ivrow(label, [(s, e, ''/'o')], tag, n, unit)` | intervals on a number line; `'o'` = output colour | keep `n·unit ≤ 460px` in a half-width column |
| `card(icon, title, text, cls, red)` | the standard `.card` with an icon | |

Focus-cue targets: grid cells `.c04` (unions like `.c04, .c14, .c24` for a column), frames `.s1>.trow:nth-child(2)`, array cells `.trow:nth-child(1) .cw:nth-child(3)`, interval rows `.ivrow:nth-child(n)` (the ticks row is child 1).

Colour meanings are fixed across lessons: blue `L` = left pointer, amber `R` = right, teal `I` = current element or window, green `ok` = hit or accepted, red `bad`/`kill` = conflict or eliminated, `gone` = dimmed.
