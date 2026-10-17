"""Theme colours: text must reach WCAG AA (4.5:1) on the surface it is drawn on. No Chrome needed.

When you add a text colour to assets/theme.css, add its (name, foreground, background) row to CHECKS."""
import re

import pytest

from common import theme_css

AA = 4.5


def parse_hex(c):
    c = c.lstrip("#")
    if len(c) in (3, 4):
        c = "".join(ch * 2 for ch in c)
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))        # alpha, if any, is ignored


def luminance(rgb):
    lin = [(v / 255 / 12.92) if v / 255 <= 0.03928 else ((v / 255 + 0.055) / 1.055) ** 2.4 for v in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a, b):
    la, lb = sorted((luminance(parse_hex(a)), luminance(parse_hex(b))), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def css_var(css, name):
    return re.search(rf"--{name}:\s*(#[0-9a-fA-F]{{3,8}})", css).group(1)


def rule_color(css, selector):
    """The `color:` of a top-level `selector{...}` rule, resolving var(--x)."""
    m = re.search(rf"(?:^|[}}\s,]){re.escape(selector)}\{{([^}}]*)\}}", css)
    assert m, f"no rule for {selector} in theme.css"
    c = re.search(r"(?<![-\w])color:\s*(#[0-9a-fA-F]{3,8}|var\(--([\w-]+)\))", m.group(1))
    assert c, f"{selector} sets no color"
    return css_var(css, c.group(2)) if c.group(2) else c.group(1)


# (what, foreground, background): `--x` is a theme variable, `.x` is the colour a rule sets
CHECKS = [
    ("body text on page", "--text", "--bg"), ("body text on panel", "--text", "--panel"),
    ("muted on page", "--muted", "--bg"), ("muted on panel", "--muted", "--panel"),
    ("accent on page", "--accent", "--bg"), ("accent on panel", "--accent", "--panel"),
    ("teal on page", "--teal", "--bg"), ("teal on panel", "--teal", "--panel"),
    ("warn on page", "--warn", "--bg"), ("warn on panel", "--warn", "--panel"),
    ("red on page", "--red", "--bg"), ("red on panel", "--red", "--panel"),
    ("good on page", "--good", "--bg"), ("good on panel", "--good", "--panel"),
    ("code keyword", ".k", "--panel"), ("code string", ".s", "--panel"), ("code number", ".n", "--panel"),
    ("code comment", ".c", "--panel"), ("code function", ".f", "--panel"),
]


@pytest.mark.parametrize("what,fg,bg", CHECKS, ids=[c[0] for c in CHECKS])
def test_text_colour_reaches_wcag_aa(what, fg, bg):
    css = theme_css()
    pick = lambda ref: css_var(css, ref[2:]) if ref.startswith("--") else rule_color(css, ref)
    ratio = contrast(pick(fg), pick(bg))
    assert ratio >= AA, f"{what}: {pick(fg)} on {pick(bg)} is {ratio:.2f}:1, below {AA}:1"


def test_contrast_helper_matches_known_values():
    assert contrast("#000000", "#ffffff") == pytest.approx(21.0)
    assert contrast("#777777", "#ffffff") == pytest.approx(4.48, abs=0.02)      # the classic just-failing grey
