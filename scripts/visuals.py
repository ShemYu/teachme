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
