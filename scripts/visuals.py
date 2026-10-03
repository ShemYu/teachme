"""Reusable visual-proof components for lesson.py (styles live in assets/theme.css → "visual-proof components").

The style (3Blue1Brown-inspired, static): show the mechanism instead of describing it, reuse one picture across
problems, reveal state step by step so a sequence of frames stands in for motion, and keep colours meaningful:
  L / blue = left pointer · R / amber = right pointer · I / teal = current element or window
  ok / green = hit or accepted · bad / red = conflict · gone = eliminated (dimmed)

    from visuals import Solutions, arr, trow, pgrid, col, row, ticks, ivrow, card, panel_code
    S = Solutions(__file__)                 # code on slides comes from the lesson's tested solutions.py
    panel_code(S.src("two_sum") + [""] + S.asserts("two_sum"), mark=(5, 7))

Every helper returns an HTML string; reveal it per step by wrapping it in an element with class sN.
"""
import html as _html, os, re

# ---------------------------------------------------------------- tested code → highlighted <pre>
KW = {"def", "return", "for", "in", "if", "elif", "else", "while", "and", "or", "not", "is", "None", "True", "False",
      "from", "import", "assert", "continue", "break", "class", "lambda", "del", "self", "yield", "with", "as",
      "try", "except", "raise", "pass", "async", "await"}
BUILTIN = {"enumerate", "len", "range", "sorted", "abs", "sum", "min", "max", "Counter", "defaultdict", "deque",
           "set", "list", "dict", "tuple", "float", "int", "str", "all", "any", "zip", "map", "ValueError", "print"}
_TOK = re.compile(r"(#.*$)|(\"[^\"]*\"|'[^']*')|(\b\d+\b)|([A-Za-z_]\w*)|(.)")


def hl_line(line):
    """Syntax-highlight one line of Python with the theme's .k/.s/.n/.c/.f spans."""
    out, after_def = [], False
    for m in _TOK.finditer(line):
        com, s, num, word, ch = m.groups()
        if com:
            out.append(f'<span class="c">{_html.escape(com)}</span>')
        elif s:
            out.append(f'<span class="s">{_html.escape(s)}</span>')
        elif num:
            out.append(f'<span class="n">{num}</span>')
        elif word:
            if after_def:
                out.append(f'<span class="f">{word}</span>'); after_def = False
            elif word in KW:
                out.append(f'<span class="k">{word}</span>'); after_def = word in ("def", "class")
            elif word in BUILTIN:
                out.append(f'<span class="f">{word}</span>')
            else:
                out.append(word)
        else:
            out.append(_html.escape(ch))
    return "".join(out)


def code(lines, mark=()):
    """<pre> of highlighted lines; 1-based line numbers in `mark` get a teal band (the line being discussed)."""
    return "<pre>" + "\n".join(f'<span class="mk">{hl_line(l)}</span>' if i in mark else hl_line(l)
                               for i, l in enumerate(lines, 1)) + "</pre>"


def panel_code(lines, mark=(), cls="tight-code"):
    return f'<div class="panel code {cls}">{code(lines, mark)}</div>'


class Solutions:
    """Read code for slides from solutions.py next to the lesson, so the screen never drifts from tested code.
    Keep asserts for on-screen examples in solutions.py as top-level `assert fn(...)` lines."""

    def __init__(self, lesson_file, name="solutions.py"):
        self.text = open(os.path.join(os.path.dirname(os.path.abspath(lesson_file)), name), encoding="utf-8").read()
        self.lines = self.text.splitlines()

    def src(self, name, drop_docstring=True):
        """Lines of top-level `def name(` / `class name` up to the next top-level statement."""
        start = next(i for i, l in enumerate(self.lines) if l.startswith((f"def {name}(", f"class {name}:", f"class {name}(")))
        out = [self.lines[start]]
        for l in self.lines[start + 1:]:
            if l and not l.startswith(" "):
                break
            out.append(l)
        while out and not out[-1].strip():
            out.pop()
        return [l for l in out if '"""' not in l] if drop_docstring else out

    def body(self, name):
        """Dedented body of `def name():` — for snippets that are statements rather than a function."""
        return [l[4:] for l in self.src(name)[1:]]

    def asserts(self, name, picks=None):
        rows = [l for l in self.lines if l.startswith(f"assert {name}(")]
        return [rows[i] for i in picks] if picks is not None else rows


# ---------------------------------------------------------------- arrays, pointers, trace frames
def arr(vals, cls=None, ptr=None, idx=True):
    """Array as boxes. cls: {i: 'L'|'R'|'I'|'ok'|'bad'|'gone'}; ptr: {i: 'L'|'R'|'i'|'L R'|any label above the box}."""
    cls, ptr = cls or {}, ptr or {}
    out = []
    for i, v in enumerate(vals):
        p = ptr.get(i, "")
        pc = {"L": "L", "R": "R", "i": "I"}.get(p.split()[0] if p else "", "")
        out.append(f'<div class="cw"><div class="ptr {pc}">{p}</div><div class="cell {cls.get(i, "")}">{v}</div>'
                   + (f'<div class="idx">{i}</div>' if idx else "") + "</div>")
    return '<div class="arr">' + "".join(out) + "</div>"


def trow(content, note="", label="", cls="", mono=True):
    """One frame of a state trace: optional left label, the picture, and a note. Stack frames to show motion;
    give later frames class sN to reveal them in step."""
    lab = f'<div class="tlabel">{label}</div>' if label else ""
    return (f'<div class="trow {cls}">{lab}{content}'
            f'<div class="tnote{" mono" if mono else ""}">{note}</div></div>')


# ---------------------------------------------------------------- pair grid: the "search space" picture
def col(j, rows):
    return [(i, j) for i in rows]


def row(i, cols):
    return [(i, j) for j in cols]


def pgrid(a, ops=(), cell=80):
    """Triangle of pair sums: row = a[i], column = a[j], cell = a[i] + a[j] for i < j. Cells have classes cIJ.
    ops: (step, kind, cells, label) with kind in kill (eliminated, red) · acc (counted, green) · hit (answer) · probe
    (numbered badge = the comparison made). step 0 = always visible, N = revealed at step N."""
    n, over = len(a), {}
    for step, kind, cells, label in ops:
        for (i, j) in cells:
            s = f" s{step}" if step else ""
            over.setdefault((i, j), []).append(f'<span class="probe{s}">{label}</span>' if kind == "probe"
                                               else f'<span class="ov {kind}{s}"></span>')
    cells = ['<div class="pc h"></div>'] + [f'<div class="pc h">{v}</div>' for v in a]
    for i in range(n):
        cells.append(f'<div class="pc h">{a[i]}</div>')
        cells += [f'<div class="pc c{i}{j}">{a[i] + a[j]}{"".join(over.get((i, j), []))}</div>' if i < j
                  else '<div class="pc na"></div>' for j in range(n)]
    return (f'<div class="pg" style="grid-template-columns:repeat({n + 1},{cell}px);--pc:{cell}px">'
            + "".join(cells) + "</div>")


# ---------------------------------------------------------------- intervals on a number line
def ticks(n=10, unit=42):
    return ('<div class="ivrow" style="height:28px"><div class="tlabel"></div>'
            f'<div class="ticks" style="width:{n * unit + 20}px">'
            + "".join(f'<span style="left:{x * unit}px">{x}</span>' for x in range(n + 1)) + "</div></div>")


def ivrow(label, bars, tag="", n=10, unit=42, cls=""):
    """bars: [(start, end, '' | 'o')] — 'o' draws the output/merged colour."""
    b = "".join(f'<div class="ibar {c}" style="left:{s * unit}px;width:{(e - s) * unit}px"></div>' for s, e, c in bars)
    return (f'<div class="ivrow {cls}"><div class="tlabel">{label}</div>'
            f'<div class="track" style="width:{n * unit + 20}px">{b}</div><div class="ivtag">{tag}</div></div>')


# ---------------------------------------------------------------- small cards
def card(icon, title, text, cls="", red=False):
    return (f'<div class="card {cls}"><div class="ic{" red" if red else ""}">{icon}</div>'
            f'<div><b>{title}</b><br><span class="muted">{text}</span></div></div>')


# ---------------------------------------------------------------- cluster diagram: servers + messages, frame by frame
_ROLE = {  # fill, stroke, label colour
    "follower": ("#1b2747", "#7c9cff", "#c9d4ff"), "candidate": ("#3a2e10", "#fbbf24", "#fde68a"),
    "leader": ("#0f3b33", "#5eead4", "#b8fff1"), "crashed": ("#161b26", "#4b5568", "#6b7280"),
}
_MSG = {"req": "#7c9cff", "grant": "#4ade80", "reject": "#f87171", "beat": "#5eead4"}


def _ring_positions(names, w, h, r):
    import math
    n = len(names)
    return {s: (w / 2 + r * math.sin(2 * math.pi * i / n), h / 2 - r * math.cos(2 * math.pi * i / n) + 10)
            for i, s in enumerate(names)}


def _cluster_frame(names, pos, state, msgs, w, h, node_r):
    import math
    out = [f'<rect class="nodim" x="1" y="1" width="{w - 2}" height="{h - 2}" rx="18" fill="#0e1420" stroke="#26324a"/>']
    for k, (src, dst, label, kind) in enumerate(msgs):                 # messages under the nodes
        (x1, y1), (x2, y2) = pos[src], pos[dst]
        dx, dy = x2 - x1, y2 - y1; d = math.hypot(dx, dy) or 1; ux, uy = dx / d, dy / d
        off = 9 if src < dst else -9                                     # opposite directions don't overlap
        px, py = -uy * off, ux * off
        sx, sy = x1 + ux * (node_r + 6) + px, y1 + uy * (node_r + 6) + py
        ex, ey = x2 - ux * (node_r + 12) + px, y2 - uy * (node_r + 12) + py
        col = _MSG.get(kind, "#8d97ab"); dash = ' stroke-dasharray="8 7"' if kind == "beat" else ""
        mx, my = (sx + ex) / 2 + px * 1.6, (sy + ey) / 2 + py * 1.6
        tw = 11.5 * len(label) + 18
        out.append(f'<g class="cm cm-{k}"><line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{col}" '
                   f'stroke-width="3"{dash} marker-end="url(#ah-{kind})"/>'
                   + (f'<rect x="{mx - tw / 2:.1f}" y="{my - 15:.1f}" width="{tw:.1f}" height="30" rx="8" fill="#0e1420" '
                      f'stroke="{col}" stroke-width="1.5"/><text x="{mx:.1f}" y="{my + 6:.1f}" text-anchor="middle" '
                      f'font-size="19" font-weight="600" fill="{col}">{_html.escape(label)}</text>' if label else "")
                   + "</g>")
    for s in names:
        x, y = pos[s]; st = state.get(s, {}); role = st.get("role", "follower")
        fill, stroke, lab = _ROLE[role]; dash = ' stroke-dasharray="6 6"' if role == "crashed" else ""
        g = [f'<g class="cn cn-{s}">', f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{node_r}" fill="{fill}" stroke="{stroke}" stroke-width="3"{dash}/>']
        if st.get("timer") is not None and role != "crashed":            # remaining election timeout, 0..1
            f = max(0.0, min(1.0, st["timer"])); rr = node_r + 9; circ = 2 * math.pi * rr
            g.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr}" fill="none" stroke="#26324a" stroke-width="5"/>'
                     f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr}" fill="none" stroke="{"#f87171" if f < 0.2 else "#8d97ab"}" '
                     f'stroke-width="5" stroke-dasharray="{circ * f:.1f} {circ:.1f}" transform="rotate(-90 {x:.1f} {y:.1f})"/>')
        g.append(f'<text x="{x:.1f}" y="{y - 4:.1f}" text-anchor="middle" font-size="30" font-weight="800" fill="{lab}">{s}</text>'
                 f'<text x="{x:.1f}" y="{y + 22:.1f}" text-anchor="middle" font-size="13" font-weight="700" letter-spacing="1" '
                 f'fill="{stroke}">{"CRASHED" if role == "crashed" else role.upper()}</text>')
        sub = " · ".join(p for p in (f"term {st['term']}" if "term" in st else "",
                                     f"voted {st['vote']}" if st.get("vote") else "") if p)
        if sub:
            g.append(f'<text x="{x:.1f}" y="{y + node_r + 30:.1f}" text-anchor="middle" font-size="19" '
                     f'font-family="SF Mono, Menlo, monospace" fill="#c3cadb" stroke="#0e1420" stroke-width="6" paint-order="stroke">{sub}</text>')
        if st.get("log"):                                                 # entry terms, oldest first
            bw = 26; x0 = x - len(st["log"]) * bw / 2
            for i, t in enumerate(st["log"]):
                g.append(f'<rect x="{x0 + i * bw:.1f}" y="{y + node_r + 42:.1f}" width="{bw - 3}" height="24" rx="4" fill="#131a28" '
                         f'stroke="#26324a"/><text x="{x0 + i * bw + (bw - 3) / 2:.1f}" y="{y + node_r + 60:.1f}" text-anchor="middle" '
                         f'font-size="15" font-family="SF Mono, Menlo, monospace" fill="#8d97ab">{t}</text>')
        g.append("</g>"); out.append("".join(g))
    return "".join(out)


def cluster(names, frames, w=880, h=660, ring=230, node_r=54):
    """Spatial diagram of servers exchanging messages, one full frame per step (a frame covers the one before it,
    so in the player each step crossfades into the next, like animation). frames[k] is shown from step k:
      {"nodes": {"S1": {"role": "leader"|"follower"|"candidate"|"crashed", "term": 2, "vote": "S1",
                        "timer": 0.0-1.0 (remaining election timeout), "log": [1, 1, 3]}},
       "msgs":  [("S3", "S1", "RequestVote t3", "req"|"grant"|"reject"|"beat"), ...]}
    Node state carries over from the previous frame; only list what changed. Focus-cue targets:
    `.cf-K .cn-S3` (a server in frame K), `.cf-K .cm-0` (the first message in frame K), `.cf-K` (the whole frame)."""
    pos = _ring_positions(names, w, h, ring)
    defs = "".join(f'<marker id="ah-{k}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
                   f'<path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>' for k, c in _MSG.items())
    state, layers = {}, []
    for k, fr in enumerate(frames):
        for s, st in fr.get("nodes", {}).items():
            state[s] = {**state.get(s, {}), **st}
        cls = f"cf cf-{k}" + (f" s{k}" if k else "")
        layers.append(f'<g class="{cls}">{_cluster_frame(names, pos, state, fr.get("msgs", []), w, h, node_r)}</g>')
    return (f'<svg class="cluster" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'style="font-family:-apple-system,Helvetica Neue,Arial,sans-serif"><defs>{defs}</defs>{"".join(layers)}</svg>')
