# Per-sentence focus targets; see references/authoring.md → Focus cues.

def ln(*ns):
    return ", ".join(f"pre .ln:nth-child({n})" for n in ns)

def lnr(a, b):
    return f"pre .ln:nth-child(n+{a}):nth-child(-n+{b})"

P1, P2 = ".grid2>.panel:nth-child(1)", ".grid2>.panel:nth-child(2)"
SP = ".sp-item:nth-child"
W = ".lane:nth-child(1) .row>"
LP = ".loop>"
G3 = ".grid3>.card:nth-child"
ST1, ST2 = ".grid2>.stack:nth-child(1)>.card", ".grid2>.stack:nth-child(2)>.card"
RT = ".rate-tbl tr"

CUES = {
    "0.0": ["", "h1.big", "^"],
    "0.1": [".lede", ".agenda"],

    "1.0": ["h2", P1 + " li:nth-child(1)", P1 + " li:nth-child(2)", P1 + " li:nth-child(3), " + P1 + " li:nth-child(4)"],
    "1.1": [P2, P2 + " li:nth-child(1)", P2 + " li:nth-child(2)", P2 + " li:nth-child(3)", P2 + " li:nth-child(4)", "^"],

    "2.0": [P1, P1 + " tr:nth-child(1)", P1 + " tr:nth-child(2)", P1 + " .note", P1 + " tr:nth-child(3)", "^"],
    "2.1": [P2, P2 + " tr:nth-child(1)", P2 + " tr:nth-child(3)", P2 + " .note"],
    "2.2": [".thesis", ".thesis b:nth-of-type(1)", ".thesis b:nth-of-type(2)"],

    "3.0": ["h2", ".spectrum", SP + "(2)", SP + "(3)", SP + "(4)", SP + "(5)", ".sp-l, .sp-r"],
    "3.1": [G3 + "(1)", "^"],
    "3.2": [G3 + "(2)"],
    "3.3": [G3 + "(3)", "^", "^", "^"],

    "4.0": [".lane:nth-child(1)", W + ":nth-child(1)", W + ":nth-child(3)", W + ":nth-child(5)",
            W + ":nth-child(7), " + W + ":nth-child(9)"],
    "4.1": [".lane:nth-child(2)"],
    "4.2": [".note.s2", W + ":nth-child(3), " + W + ":nth-child(5)"],

    "5.0": [".loop", LP + ":nth-child(1), " + LP + ":nth-child(3)", LP + ":nth-child(5)", LP + ":nth-child(7)",
            LP + ":nth-child(9)"],
    "5.1": [".back", "^"],
    "5.2": [".grid3", G3 + "(1)", "^", "^"],
    "5.3": [G3 + "(2)", "^"],
    "5.4": [G3 + "(3)", "^", "^"],

    "6.0": ["h2", ".code", ".code " + ln(2), ".code " + lnr(3, 5), ".code " + ln(8)],
    "6.1": ["ul.s1", "ul.s1 li:nth-child(1)", "ul.s1 li:nth-child(2)", "ul.s1 li:nth-child(3)", "ul.s1 li:nth-child(4)",
            "ul.s1 li:nth-child(5)"],
    "6.2": [".thesis", ".thesis b", "^"],

    "7.0": ["h2", P1, "table.math tr:nth-child(1)", "table.math tr:nth-child(2)", "table.math tr:nth-child(3)",
            "table.math tr:nth-child(4)", "table.math tr:nth-child(5)", P1 + " .note"],
    "7.1": [".stack", ".stack>.card:nth-child(1)"],
    "7.2": [".stack>.card:nth-child(2)", "^", "^"],
    "7.3": [".stack>.card:nth-child(3)", "^", "^"],

    "8.0": ["h2", P1 + " tr:nth-child(1)", P1 + " tr:nth-child(2), " + P1 + " tr:nth-child(3)", P1 + " tr:nth-child(4)", P1],
    "8.1": [P2 + " .label", P2 + " li:nth-child(1), " + P2 + " li:nth-child(2)", P2 + " li:nth-child(3)"],
    "8.2": [".thesis b", ".thesis", "^", "^"],

    "9.0": ["h2", ST1 + ":nth-child(1)", "^"],
    "9.1": [ST1 + ":nth-child(2)"],
    "9.2": [ST2 + ":nth-child(1)", "^", "^", "^", "^"],
    "9.3": [ST2 + ":nth-child(2)", "^"],

    "10.0": [".tbl", ".tbl tr:nth-child(2)", ".tbl tr:nth-child(2) td:nth-child(4)"],
    "10.1": [".tbl tr:nth-child(3)", "^", ".tbl tr:nth-child(3) td:nth-child(4)"],
    "10.2": [".tbl tr:nth-child(4)", ".tbl tr:nth-child(4) td:nth-child(4)"],
    "10.3": [".thesis", "^", ".thesis", "^"],

    "11.0": ["h2", P1 + " li:nth-child(1)", "^", P1 + " li:nth-child(2)", P1 + " li:nth-child(3)", P1 + " li:nth-child(4)"],
    "11.1": [P2 + " ul", P2 + " li:nth-child(4)"],
    "11.2": [".thesis", ".thesis b", "^"],

    "12.0": ["h2", ".formula", "^"],
    "12.1": [G3 + "(1)", "^"],
    "12.2": [G3 + "(2)"],
    "12.3": [G3 + "(3)"],
    "12.4": [G3 + "(n+4)", G3 + "(4)", G3 + "(5)", G3 + "(6)"],

    "13.0": [".rate-tbl", RT + ":nth-child(2)"],
    "13.1": [RT + ":nth-child(3)"],
    "13.2": [RT + ":nth-child(4)", RT + ":nth-child(4) td:nth-child(6)"],
    "13.3": [RT + ":nth-child(5)"],
    "13.4": [RT + ":nth-child(6)", RT + ":nth-child(6) td:nth-child(n+5)"],
    "13.5": [".note.s5", "^"],

    "14.0": [".code", ln(2, 3), ln(4), ln(5), ln(6), ln(7), ln(8, 9), ln(10), ln(11), lnr(12, 14), ln(15, 16), ln(17, 18),
             ln(19), ".code"],

    "15.0": [".recap"],
    "15.1": ["ol.recap li:nth-child(1)"] * 2,
    "15.2": ["ol.recap li:nth-child(2)"] * 2,
    "15.3": ["ol.recap li:nth-child(3)"] * 3,
    "15.4": ["ol.recap li:nth-child(4)"] * 3,
    "15.5": ["ol.recap li:nth-child(5)"] * 3,
    "15.6": [".exercise", "^", "^", ""],
}
