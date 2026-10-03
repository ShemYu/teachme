# Per-sentence focus targets; see references/authoring.md → Focus cues.

def ln(*ns):
    return ", ".join(f"pre .ln:nth-child({n})" for n in ns)

def lnr(a, b):
    return f"pre .ln:nth-child(n+{a}):nth-child(-n+{b})"

P1, P2 = ".grid2>.panel:nth-child(1)", ".grid2>.panel:nth-child(2)"
LANE1, LANE2, LANE3 = ".lane:nth-child(1)", ".lane:nth-child(2)", ".lane:nth-child(3)"
ROW1 = LANE1 + " .row>"
INJ1, INJ2 = ".grid2.mt>.panel:nth-child(1)", ".grid2.mt>.panel:nth-child(2)"
ST1, ST2 = ".grid2>.stack:nth-child(1)>.card", ".grid2>.stack:nth-child(2)>.card"
TBL = ".tbl tr"
RT = ".rate-tbl tr"
TL = ".tl-row"

CUES = {
    "0.0": ["", "h1.big", ".kicker"],
    "0.1": [".lede", ".lede em", "^", ".agenda"],

    "1.0": [P1, "h2", P1 + " ul"],
    "1.1": [P2, P2 + " li:nth-child(1)", P2 + " li:nth-child(2)", P2 + " li:nth-child(3)", P2 + " li:nth-child(4)",
            P2 + " li:nth-child(5)"],
    "1.2": [".thesis", ".thesis b", ".thesis"],

    "2.0": ["", ".grid3>.card:nth-child(1)"],
    "2.1": [".grid3>.card:nth-child(2)", "^"],
    "2.2": [".grid3>.card:nth-child(3)"],
    "2.3": [".thesis", ".grid3", ".grid3, .thesis"],
    "2.4": [".panel.s4 .label", ".chips-row", "^"],

    "3.0": ["h2", P1, "^", "^"],
    "3.1": [P2, P2 + " li:nth-child(1)", P2 + " li:nth-child(2)", P2 + " li:nth-child(3)", P2 + " li:nth-child(4)"],
    "3.2": [".thesis", ".thesis b:first-of-type", ".thesis b:last-of-type"],

    "4.0": [".arch", ROW1 + ":nth-child(1)", ROW1 + ":nth-child(3)", ROW1 + ":nth-child(5), " + ROW1 + ":nth-child(7)",
            ROW1 + ":nth-child(5)"],
    "4.1": [LANE2 + " .box:nth-child(1)", LANE2 + " .box:nth-child(2)", LANE2 + " .box:nth-child(3)"],
    "4.2": [LANE3, ".arch", "^"],

    "5.0": ["", ".loop", ".loop>:nth-child(1), .loop>:nth-child(3)", ".loop>:nth-child(3)", ".loop>:nth-child(5)"],
    "5.1": [".back", "^", ".loop, .back"],
    "5.2": [INJ1, INJ1 + " li:nth-child(1)", INJ1 + " li:nth-child(2)", INJ1 + " li:nth-child(3)", INJ1 + " li:nth-child(4)"],
    "5.3": [INJ2, INJ2 + " li:nth-child(1)", INJ2 + " li:nth-child(2)", INJ2 + " li:nth-child(3)", INJ2 + " li:nth-child(4)"],

    "6.0": ["h2", "^", ".code", ".code " + lnr(2, 4), ".code " + lnr(5, 6), ".code " + lnr(7, 8), ".code " + lnr(9, 10),
            ".code " + ln(11)],
    "6.1": [".stack", ".stack>.card:nth-child(1)", "^"],
    "6.2": [".stack>.card:nth-child(2)", "^", "^", "^", "^"],
    "6.3": [".stack>.card:nth-child(3)", "^", "^"],

    "7.0": ["", ST1 + ":nth-child(1)"],
    "7.1": [ST1 + ":nth-child(2)", "^", "^"],
    "7.2": [ST2 + ":nth-child(1)", "^", "^", "^"],
    "7.3": [ST2 + ":nth-child(2)", "^", "^", "^"],

    "8.0": ["", "h2", "^", ".code", ".code " + ln(2), ".code " + ln(3), ".code " + ln(4), ".code " + lnr(5, 6), ".code " + ln(7)],
    "8.1": ["ul.s1 li:nth-child(1)", "ul.s1 li:nth-child(2)", "ul.s1 li:nth-child(3)", "ul.s1 li:nth-child(4)"],
    "8.2": [".panel.s2", "table.math tr:nth-child(1)", "table.math tr:nth-child(2)", "table.math tr:nth-child(3)", ".panel.s2"],

    "9.0": [".tbl", TBL + ":nth-child(2) td:nth-child(2)", TBL + ":nth-child(2) td:nth-child(3)"],
    "9.1": [TBL + ":nth-child(3)", TBL + ":nth-child(3) td:nth-child(2)", TBL + ":nth-child(3) td:nth-child(3)",
            TBL + ":nth-child(4) td:nth-child(2)", TBL + ":nth-child(4) td:nth-child(3)"],
    "9.2": [TBL + ":nth-child(5), " + TBL + ":nth-child(6)", TBL + ":nth-child(5) td:nth-child(2), " + TBL + ":nth-child(6) td:nth-child(2)",
            TBL + ":nth-child(5) td:nth-child(3), " + TBL + ":nth-child(6) td:nth-child(3)"],
    "9.3": [TBL + ":nth-child(7)", TBL + ":nth-child(7) td:nth-child(3)", "^", "^", TBL + ":nth-child(7)"],

    "10.0": ["", ".grid3>.card:nth-child(1)"],
    "10.1": [".grid3>.card:nth-child(2)", "^"],
    "10.2": [".grid3>.card:nth-child(3)"],
    "10.3": [".panel.s3 .label", "ol.steps li:nth-child(1)", "ol.steps li:nth-child(2)", "ol.steps li:nth-child(3)",
             "ol.steps li:nth-child(4)"],

    "11.0": ["h2", P1],
    "11.1": [P2 + " li:nth-child(1)", "^", P2 + " li:nth-child(2)", P2 + " li:nth-child(3)"],
    "11.2": [P2 + " li:nth-child(4)", ".thesis", "^"],

    "12.0": [".rate-tbl", RT + ":nth-child(2)", "^"],
    "12.1": [RT + ":nth-child(3)"],
    "12.2": [RT + ":nth-child(4)", "^"],
    "12.3": [RT + ":nth-child(5)"],
    "12.4": [RT + ":nth-child(6)", RT + ":nth-child(7)"],
    "12.5": [".note.s5", "^"],

    "13.0": ["h2", TL + ":nth-child(1)"],
    "13.1": [TL + ":nth-child(2)"],
    "13.2": [TL + ":nth-child(3)"],
    "13.3": [TL + ":nth-child(4)", "^", "^"],
    "13.4": [TL + ":nth-child(5)"],
    "13.5": [".note.s5", "^", "^", "^"],

    "14.0": [".code", ln(2), ln(3), ln(4), ln(5), ln(6, 7), ln(8, 9), ln(10, 11), lnr(12, 16), ".code"],

    "15.0": [".recap"],
    "15.1": ["ol.recap li:nth-child(1)"] * 3,
    "15.2": ["ol.recap li:nth-child(2)"] * 3,
    "15.3": ["ol.recap li:nth-child(3)"] * 3,
    "15.4": ["ol.recap li:nth-child(4)"] * 3,
    "15.5": ["ol.recap li:nth-child(5)"] * 3,
    "15.6": [".exercise", "^", "^", ""],
}
