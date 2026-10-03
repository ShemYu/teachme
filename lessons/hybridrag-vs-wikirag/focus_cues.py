# Per-sentence focus targets; see references/authoring.md → Focus cues.

def ln(*ns):
    return ", ".join(f"pre .ln:nth-child({n})" for n in ns)

def lnr(a, b):
    return f"pre .ln:nth-child(n+{a}):nth-child(-n+{b})"

CARD = ".grid2>.stack>.card"
FIX = ".panel.s4 .tbl tr"
PA, PB = ".grid2>.panel:nth-child(1)", ".grid2>.panel:nth-child(2)"
L1, L2 = ".lane:nth-child(1)", ".lane:nth-child(2)"
ROW = ".rate-tbl tr"
S1, S2 = ".grid2>.stack:nth-child(1)>.card", ".grid2>.stack:nth-child(2)>.card"
Q = ".tbl tr"

CUES = {
    "0.0": ["", "h1.big", ".lede"],
    "0.1": [".agenda", ".agenda>div:nth-child(1)", ".agenda>div:nth-child(2)", ".agenda>div:nth-child(3)",
            ".agenda>div:nth-child(4), .agenda>div:nth-child(5), .agenda>div:nth-child(6)"],

    "1.0": [".grid2>.stack", CARD + ":nth-child(1)", "^", "^"],
    "1.1": [CARD + ":nth-child(2)", "^", "^"],
    "1.2": [CARD + ":nth-child(3)", "^", "^"],
    "1.3": [CARD + ":nth-child(4)", "^", "^"],
    "1.4": [".panel.s4", FIX + ":nth-child(2)", FIX + ":nth-child(3)", FIX + ":nth-child(4)", FIX + ":nth-child(5)",
            ".panel.s4"],

    "2.0": ["", PA + " .flow", PA + " li.good", PA + " li.bad"],
    "2.1": [PB + " .flow", "^", PB + " li:nth-child(2)", PB + " li.bad"],
    "2.2": [".thesis", ".thesis b", ".thesis"],

    "3.0": [".loop", ".loop>:nth-child(3), .loop>:nth-child(4)", ".loop>:nth-child(6)"],
    "3.1": [".loop>:nth-child(8)", "^"],
    "3.2": [".code.s2", ln(5), ln(5)],
    "3.3": ["ul.s3 li:nth-child(1)", "ul.s3 li:nth-child(2)", "ul.s3 li:nth-child(3)", "ul.s3 li:nth-child(4)",
            "ul.s3 li:nth-child(5)", "^"],

    "4.0": [L1, L1 + " .col-boxes>.box:nth-child(1)", ".box.hlb", ".box.store"],
    "4.1": [L2 + " .col-boxes", L2 + " .box.agent"],
    "4.2": [".grid2.mt .card:nth-child(1)", ".grid2.mt .card:nth-child(2)", ".grid2.mt"],

    "5.0": [L1, "^", L1 + " .col-boxes"],
    "5.1": [L2 + " .box.agent", L2 + " .col-boxes>.box:nth-child(1), " + L2 + " .col-boxes>.box:nth-child(2)", ".box.hlb"],
    "5.2": [".note.s2", "^", "^", "h2"],

    "6.0": ["", "", ".code " + lnr(1, 6), ".code " + lnr(7, 9), ".code " + ln(10)],
    "6.1": [".stack>.card.s1", "^", "^"],
    "6.2": [".stack>.card.s2", "^"],
    "6.3": [".stack>.card.s3", "^", ".stack>.card.s3, .code " + ln(8, 9), ".code " + lnr(8, 10)],

    "7.0": ["", ".grid2>.panel .label", "table.math tr:nth-child(-n+3)", "table.math td .warn, table.math tr:nth-child(4)",
            ".grid2>.panel .note"],
    "7.1": [".stack>.card.s1"],
    "7.2": [".stack>.card.s2", "^", "^", "^", "^"],

    "8.0": [".rate-tbl", ROW + ":nth-child(2)", "^"],
    "8.1": [ROW + ":nth-child(3)"],
    "8.2": [ROW + ":nth-child(4)", ROW + ":nth-child(4) td:nth-child(5)", ROW + ":nth-child(4) td:nth-child(n+6):nth-child(-n+7)"],
    "8.3": [ROW + ":nth-child(5), " + ROW + ":nth-child(6)", ROW + ":nth-child(5)", ROW + ":nth-child(6)"],
    "8.4": [ROW + ":nth-child(7)", ROW + ":nth-child(7) td:nth-child(n+2):nth-child(-n+3)",
            ROW + ":nth-child(7) td:nth-child(n+5):nth-child(-n+7)",
            ROW + ":nth-child(7) td:nth-child(4), " + ROW + ":nth-child(7) td:nth-child(8)"],
    "8.5": [".note.s5", "^"],

    "9.0": [".spectrum", "h2", ".sp-item:nth-child(2)", ".sp-item:nth-child(3)", ".sp-item:nth-child(4)",
            ".sp-item:nth-child(5)"],
    "9.1": [".formula", "^"],
    "9.2": [".grid3>.card:nth-child(1)", "^"],
    "9.3": [".grid3>.card:nth-child(2)", "^"],
    "9.4": [".grid3>.card:nth-child(3)", "^"],

    "10.0": ["", S1 + ":nth-child(1)", "^", "^", "^"],
    "10.1": [S1 + ":nth-child(2)", "^", "^"],
    "10.2": [S2 + ":nth-child(1)"],
    "10.3": [S2 + ":nth-child(2)"],
    "10.4": [".thesis", ".thesis b", "^", ".thesis"],

    "11.0": [".tbl", Q + ":nth-child(2)", Q + ":nth-child(2) td:nth-child(2)", "^"],
    "11.1": [Q + ":nth-child(3)", "^"],
    "11.2": [Q + ":nth-child(4)", "^"],
    "11.3": [Q + ":nth-child(5)", "^", "^"],
    "11.4": [Q + ":nth-child(6)", "^"],
    "11.5": [".thesis", "^"],

    "12.0": [".pyramid", "^", ".l1"],
    "12.1": [".l2"],
    "12.2": [".l3"],
    "12.3": [".l4"],
    "12.4": [".thesis", ".thesis i", "^"],

    "13.0": ["", ".grid2>.panel:nth-child(1) ul", "^"],
    "13.1": [".panel.s1 li:nth-child(-n+3)", ".panel.s1 li:nth-child(4)", "^", ".panel.s1 li:nth-child(5)"],
    "13.2": [".thesis", "^", "^"],

    "14.0": [".recap"],
    "14.1": ["ol.recap li:nth-child(1)"] * 4,
    "14.2": ["ol.recap li:nth-child(2)"] * 3,
    "14.3": ["ol.recap li:nth-child(3)"] * 3,
    "14.4": ["ol.recap li:nth-child(4)"] * 3,
    "14.5": ["ol.recap li:nth-child(5)"] * 3,
    "14.6": [".exercise"] * 4 + [""],
}
