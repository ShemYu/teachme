# Per-sentence focus targets; see references/authoring.md → Focus cues.

def ln(*ns, p=".code"):
    return ", ".join(f"{p} pre .ln:nth-child({n})" for n in ns)

def lnr(a, b, p=".code"):
    return f"{p} pre .ln:nth-child(n+{a}):nth-child(-n+{b})"

def tr(n):  # data rows start at 2 (row 1 is the header)
    return f"table.tbl tr:nth-child({n})"

def card(n):
    return f".stack>.card:nth-child({n})"

def li(p, n):
    return f"{p} li:nth-child({n})"

def cells(*ij):
    return ", ".join(f".c{i}{j}" for i, j in ij)

def node(n):  # nth step box in the .loop flow (arrows sit between nodes)
    return f".loop>:nth-child({2 * n - 1})"

T_L = ".grid2>div:first-child>.trow:nth-child"   # trace rows in the left column
T_S = ".s1>.trow:nth-child"                       # trace rows inside a revealed block
COL4 = cells((0, 4), (1, 4), (2, 4), (3, 4))
ROW0 = cells((0, 1), (0, 2), (0, 3))
P1, P2 = ".grid2>.panel:nth-child(1)", ".grid2>.panel:nth-child(2)"
IV = ".grid2>div:first-child>.ivrow:nth-child"
RIGHT = ".grid2>div:nth-child(2)>:nth-child"

CUES = {
    "0.0": ["h1.big", ".kicker"],
    "0.1": [".lede", "^", "^", ".agenda"],

    "1.0": [".loop", node(1), node(2), node(3), node(4), node(5), node(6), node(7), ".loop"],
    "1.1": [node(4) + ", " + node(6), ".grid2.s1>.thesis:nth-child(1)", ".grid2.s1>.thesis:nth-child(2)", "^"],

    "2.0": ["table.tbl", tr(2), tr(3)],
    "2.1": [tr(4), tr(5)],
    "2.2": [tr(6), tr(7), "table.tbl td:nth-child(3)", "^", "table.tbl"],

    "3.0": ["h2", ln(1), ln(4), ln(5, 6), lnr(3, 7)],
    "3.1": [".s1", f"{T_S}(1)", f"{T_S}(2)", "^"],
    "3.2": [".card.s2:nth-of-type(2)", ln(11), ".card.s2:nth-of-type(3)"],

    "4.0": ["table.tbl", tr(2), tr(3), tr(4), tr(5), tr(6), tr(7)],
    "4.1": [ln(6, p="div.s1>.code"), "^", "^", tr(4), ln(6, p="div.s1>.code")],
    "4.2": [lnr(1, 8, p="div.s2>.code"), ".note", ln(6, p="div.s2>.code"), ln(2, p="div.s2>.code"), ".note"],

    "5.0": ["h2", f"{T_L}(1)", "^", f"{T_L}(2)", f"{T_L}(3)"],
    "5.1": [".s1 .code", ln(3, 4, 5, 6, 7, 8, 9, 10), ln(3)],
    "5.2": [".card.s2", "^", ".card.s2"],

    "6.0": [".pg", ".axis", ".c04"],
    "6.1": [".c04", card(1), COL4],
    "6.2": [".c03", card(2), ROW0],
    "6.3": [".c13", ".thesis", "^"],

    "7.0": [card(1), ln(4, p=".grid2>div:first-child>.code"), ln(5, 6, p=".grid2>div:first-child>.code"), card(1)],
    "7.1": [card(2), lnr(1, 7, p=".s1>.code"), ln(2, p=".s1>.code"), card(2)],
    "7.2": [card(3), "^", card(4)],

    "8.0": [".code", lnr(7, 13), card(1)],
    "8.1": [card(2) + ", " + card(3), ln(5, 6), lnr(15, 19), card(3)],
    "8.2": [ln(22), card(4)],

    "9.0": ["h2", ".code", f"{IV}(2), {IV}(3), {IV}(4), {IV}(5)", ln(4)],
    "9.1": [f"{IV}(2), {IV}(3), {IV}(4), {IV}(5)", f"{IV}(3)", ln(7), f"{IV}(4)", f"{IV}(5)"],
    "9.2": ["div.s2>.ivrow", f"{RIGHT}(3)", f"{RIGHT}(2)", ln(4), f"{RIGHT}(3)"],

    "10.0": ["h2", tr(2), ln(3, 4, 5), tr(2) + " code", ln(5)],
    "10.1": [tr(3), lnr(9, 11), ln(12, 13), ln(14), tr(3)],
    "10.2": [tr(4) + ", " + tr(5), tr(4), tr(5)],

    "11.0": ["h2", ln(1, 2, 3), lnr(4, 9)],
    "11.1": [".s1", f"{T_S}(2)", f"{T_S}(3)", ln(5, 6, 7), f"{T_S}(4)"],
    "11.2": [".card.s2", "^", "^", f"{T_S}(4)"],

    "12.0": [".grid2", ln(8, 13, p=".pa"), lnr(3, 14, p=".pa"), ln(7, 9, 10, 11, p=".pa")],
    "12.1": [ln(6, 7, p=".s1 .code"), ln(12, p=".s1 .code"), ln(1, p=".s1 .code")],
    "12.2": [".thesis", "^", ".thesis em", "^"],

    "13.0": ["table.tbl", tr(2) + ", " + tr(3) + ", " + tr(4), tr(5) + ", " + tr(6), tr(5), tr(6)],
    "13.1": [tr(7), "^", "^"],

    "14.0": ["h2", ln(3, 5, 6), lnr(10, 11), "^"],
    "14.1": [".s1", f"{T_S}(1), {T_S}(2)", f"{T_S}(3)", ".card.s1", ln(12, 16)],
    "14.2": [".card.s2"],

    "15.0": ["h2", ln(3), ln(5, 6)],
    "15.1": [".s1", f"{T_S}(1), {T_S}(2)", f"{T_S}(3)", f"{T_S}(4)", f"{T_S}(5)"],
    "15.2": [ln(5, 6, 7), ".card.s2", "^", "^"],

    "16.0": ["h2", ".note", "^", "^", "^"],
    "16.1": [ln(6, 7), lnr(9, 13), ".row.s1 .ev:nth-child(1)", ".row.s1 .ev:nth-child(2)", ".row.s1 .ev:nth-child(3)"],
    "16.2": [".grid2>div:first-child>.card", f"{RIGHT}(4)", "^", "^", f"{RIGHT}(5)"],

    "17.0": [".code", lnr(1, 3), card(1), lnr(5, 8), card(2)],
    "17.1": [card(3), ln(11), ln(12), ln(13), card(3), lnr(15, 19)],

    "18.0": [P1, li(P1, 1), li(P1, 2), li(P1, 3)],
    "18.1": [li(P2, 1), li(P2, 2), li(P2, 3), "^", li(P2, 4)],

    "19.0": ["h2", li("ol.qa", 1), li("ol.qa", 2), li("ol.qa", 3), li("ol.qa", 4), li("ol.qa", 5), li("ol.qa", 6)],
    "19.1": ["ol.qa", li("ol.qa", 1) + " .ans", li("ol.qa", 2) + " .ans", li("ol.qa", 3) + " .ans",
             li("ol.qa", 4) + " .ans", li("ol.qa", 5) + " .ans", li("ol.qa", 6) + " .ans"],

    "20.0": ["ol.recap", li("ol.recap", 1), li("ol.recap", 2), li("ol.recap", 3), li("ol.recap", 4), li("ol.recap", 5)],
    "20.1": [".exercise", "^", ""],
}
