# Per-sentence focus targets. Key "slide.step" -> list aligned with that step's sentences.
# ""  = no spotlight (show everything)   "^" = same as previous sentence
# Missing step -> default: the elements revealed at that step (".sN"), or none for step 0.
# Selectors are scoped to the slide. Code blocks: every <pre> line is wrapped in .ln

def ln(*ns):
    return ", ".join(f"pre .ln:nth-child({n})" for n in ns)

def lnr(a, b):
    return f"pre .ln:nth-child(n+{a}):nth-child(-n+{b})"

P1 = ".grid2>.panel"
C9 = ".grid2>div:first-child>.card"
E1 = ".grid2>.panel:nth-child(1)"

CUES = {
    "0.0": ["", "h1.big", "^", ".lede"],
    "0.1": [".agenda"] + [f".agenda>div:nth-child({n})" for n in (1, 2, 3, 4, 5, 6)],

    "1.0": [P1, "table.math tr:nth-child(1)", "table.math tr:nth-child(2)", "table.math tr:nth-child(3)",
            "table.math tr:nth-child(4)", P1 + " .note"],
    "1.3": [".stack .s3", "^", ".stack .s3 .muted", ".stack .s3 b.warn", ".stack .s3", "^"],

    "2.0": [".cols3", ".col:nth-child(1)", ".col:nth-child(1) li.good", ".col:nth-child(1) li.bad"],
    "2.1": [".col.s1", ".col.s1 .flow", ".col.s1 li.good", ".col.s1 li:nth-child(3)", ".col.s1 li:nth-child(4)"],
    "2.2": [".col.s2", ".col.s2 .flow", "^", ".col.s2 li:nth-child(2)", ".col.s2 li.bad"],
    "2.3": [".thesis", ".thesis b", ".thesis i:nth-of-type(1)", ".thesis i:nth-of-type(2)", ".thesis"],

    "3.0": [".loop", ".node.q"],
    "3.1": [".loop>:nth-child(3)", ".loop>:nth-child(5)"],
    "3.2": [".loop>:nth-child(7)"],
    "3.3": [".node.dec", "^", ".node.a", ".back"],
    "3.4": [".grid2.mt>.panel:nth-child(1)", ".grid2.mt>.panel:nth-child(2)",
            ".grid2.mt>.panel:nth-child(2) li:nth-child(1)", ".grid2.mt>.panel:nth-child(2) li:nth-child(2)",
            ".grid2.mt>.panel:nth-child(2) li:nth-child(3)", ".grid2.mt>.panel:nth-child(2)"],

    "4.0": [".lane:nth-child(1)", ".lane:nth-child(1) .row>.box:first-child, .lane:nth-child(1) .col-boxes", ".box.store"],
    "4.1": [".lane.s1", ".lane.s1 .col-boxes>.box:nth-child(1)", ".box.hlb", "^", ".box.store", "^", ".box.hlb"],

    "5.0": [".pyramid", "^", ".l1", ".l2", ".l3", ".l4", "^"],
    "5.1": [".code.s1"],
    "5.2": ["ul.s2", "ul.s2 li:nth-child(1)", "ul.s2 li:nth-child(2)", "ul.s2 li:nth-child(3)", "ul.s2 li:nth-child(4)", "^"],

    "6.0": [".code.wide", "^", ln(1), ln(2), ln(3), ln(4), ln(5)],
    "6.3": [".grid3>.s3", "^", ".grid3>.s3, " + ln(4)],
    "6.4": [".grid3>.s4", ".grid3>.s4:nth-child(4)", ".grid3>.s4:nth-child(5)", ".grid3>.s4:nth-child(6)", "^"],

    "7.0": [".timeline-wrap", ".tl-row:nth-child(1)", "^", "^"],
    "7.1": [".tl-row:nth-child(2)", "^", "^"],
    "7.2": [".tl-row:nth-child(3)", "^", ".tl-row:nth-child(3) .tl"],
    "7.3": [".tl-row:nth-child(4)", "^"],
    "7.4": [".tl-row:nth-child(5)", ".note.s4", ".tl-row:nth-child(4) .tl, .tl-row:nth-child(5) .tl"],

    "8.0": [".tbl", ".tbl tr:nth-child(2)"],
    "8.1": [".tbl tr:nth-child(3)", ".tbl tr:nth-child(3) td:nth-child(2)", ".thesis", ".tbl tr:nth-child(3) td:nth-child(3)"],
    "8.2": [".tbl tr:nth-child(4)", ".tbl tr:nth-child(5)", ".tbl tr:nth-child(6)", ".tbl tr:nth-child(n+2) td:first-child"],

    "9.0": ["", C9 + ":nth-child(1)", "^"],
    "9.1": [C9 + ":nth-child(2)", "^", ".code.s1 " + lnr(1, 5), ".code.s1 " + lnr(6, 9), "^"],
    "9.2": [C9 + ":nth-child(3)", "^", "^"],
    "9.3": [C9 + ":nth-child(4)", "^"],

    "10.0": ["", E1 + " li:nth-child(1)", E1 + " li:nth-child(2)", E1 + " li:nth-child(2) .muted",
             E1 + " li:nth-child(3)", E1 + " li:nth-child(4)"],
    "10.1": [".stack", ".stack>.card:nth-child(1)", "^"],
    "10.2": [".stack>.card:nth-child(2)", "^"],
    "10.3": [".stack>.card:nth-child(3)", "^", "^"],
    "10.4": [".stack>.card:nth-child(4)", "^", "^"],

    "11.0": ["", E1 + ">ul:nth-of-type(1)", "^", ""],
    "11.1": ["ul.s1", "ul.s1 li:nth-child(1)", "^", "ul.s1 li:nth-child(2)", "ul.s1 li:nth-child(3)"],
    "11.2": [".panel.s2>ul", ".panel.s2>ul li:nth-child(2)"],
    "11.3": [".pareto", ".pareto polyline, .pareto circle:not([fill='var(--red)'])", ".pareto circle[fill='var(--red)']"],

    "12.0": [".formula", "^"],
    "12.1": [".grid3>.card:nth-child(1)", "^", "^"],
    "12.2": [".grid3>.card:nth-child(2)", ".grid3>.card:nth-child(3)", "^"],
    "12.3": [".grid3>.card:nth-child(4)"],
    "12.4": ["", ".grid3>.card:nth-child(5)", ".grid3>.card:nth-child(6)", "^"],

    "13.0": [".code", ln(2), ln(3), ln(4, 5), ln(7), ln(8), lnr(9, 14), lnr(15, 19), ln(21), ".code"],

    "14.0": [".recap"],
    "14.1": ["ol.recap li:nth-child(1)"] * 4,
    "14.2": ["ol.recap li:nth-child(2)"] * 2,
    "14.3": ["ol.recap li:nth-child(3)"] * 4,
    "14.4": ["ol.recap li:nth-child(4)"] * 3,
    "14.5": ["ol.recap li:nth-child(5)"] * 2,
    "14.6": [".exercise"] * 5 + [""],
}
