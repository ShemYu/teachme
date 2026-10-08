import visuals as v


def test_arr_marks_and_pointers():
    html = v.arr([1, 2], {0: "L"}, {0: "L"}, idx=False)
    assert html.count('class="cw"') == 2 and 'class="cell L"' in html and 'class="ptr L"' in html


def test_pgrid_has_one_cell_per_pair_and_reveals_ops():
    html = v.pgrid([1, 2, 4], [(1, "kill", v.col(2, range(2)), ""), (2, "probe", [(0, 2)], "1")])
    assert html.count('class="pc c') == 3          # C(3, 2) pairs
    assert html.count('ov kill s1') == 2 and 'probe s2' in html


def test_code_highlights_and_marks_lines():
    pre = v.code(["def f(x):", "    return x  # done"], mark=(2,))
    assert '<span class="k">def</span> <span class="f">f</span>' in pre
    assert '<span class="mk">' in pre and '<span class="c"># done</span>' in pre


def test_solutions_extracts_defs_classes_and_asserts(tmp_path):
    (tmp_path / "solutions.py").write_text(
        'def add(a, b):\n    """Doc."""\n    return a + b\n\nclass Box:\n    x = 1\n\n'
        'def snippet():\n    y = 2\n\nassert add(1, 2) == 3\nassert add(0, 0) == 0\n')
    S = v.Solutions(tmp_path / "lesson.py")
    assert S.src("add") == ["def add(a, b):", "    return a + b"]
    assert S.src("Box") == ["class Box:", "    x = 1"] and S.body("snippet") == ["y = 2"]
    assert S.asserts("add", [1]) == ["assert add(0, 0) == 0"]


def test_cluster_frames_stack_and_state_carries_over():
    svg = v.cluster(["S1", "S2", "S3"], [
        {"nodes": {"S1": {"role": "leader", "term": 1}, "S2": {"term": 1}, "S3": {"term": 1}}},
        {"nodes": {"S1": {"role": "crashed"}}, "msgs": [("S2", "S3", "RequestVote t2", "req")]},
    ])
    assert svg.count('class="cf cf-') == 2 and 'class="cf cf-1 s1"' in svg      # frame k is revealed at step k
    assert svg.count('class="nodim"') == 2                                     # backdrop never dims (no bleed-through)
    frame1 = svg.split('class="cf cf-1 s1"')[1]
    assert "CRASHED" in frame1 and "term 1" in frame1                           # S1's term carried over
    assert 'class="cm cm-0"' in frame1 and "RequestVote t2" in frame1


# ---------------------------------------------------------------- lanes
import re
import pytest


def frame_markup(svg, k):
    """The markup of frame k of a lanes()/cluster() svg."""
    parts = re.split(r'(?=<g class="(?:lf|cf) (?:lf|cf)-\d+)', svg)
    return next(p for p in parts if re.match(rf'<g class="(?:lf|cf) (?:lf|cf)-{k}[" ]', p))


def test_lanes_one_row_per_name_and_frames_stack():
    svg = v.lanes(["S2", "S3"], [{"bars": {"S2": (0, 100, "hot")}}, {"marks": [("S3", 200, "ok", "S2")]}])
    assert svg.count('class="lf lf-') == 2 and 'class="lf lf-1 s1"' in svg          # frame k is revealed at step k
    assert svg.count('class="lr lr-S2"') == 2 and svg.count('class="lr lr-S3"') == 2
    assert svg.count('class="nodim"') == 2 and svg.count('class="lax"') == 2         # opaque backdrop per frame; one axis each


def test_lanes_bar_length_is_to_scale():
    svg = v.lanes(["S2"], [{"bars": {"S2": (0, 180, "hot"), }}], tmax=300, w=1700, label_w=130)
    k = (1700 - 44 - (130 + 24)) / 300                                                 # pixels per time unit
    assert f'class="lb lb-S2" x="154.0" y="' in svg and f'width="{180 * k:.1f}"' in svg


def test_lanes_state_carries_over_and_reset_clears_it():
    svg = v.lanes(["S2", "S3"], [
        {"bars": {"S2": (0, 100, "run")}, "targets": {"S2": 200}, "marks": [("S2", 50, "dot", "x")], "rules": [(0, "beat")]},
        {"bars": {"S2": (0, 150, "hot")}, "marks": [("S2", 150, "ask", "")]},
        {"reset": True, "bars": {"S3": (0, 90, "ok")}},
    ])
    f1 = frame_markup(svg, 1)
    assert f1.count('class="lm lm-') == 2 and 'class="lt lt-S2"' in f1 and 'class="lu lu-0"' in f1   # earlier mark, target, rule kept
    assert f1.count('class="lb lb-S2"') == 1                                                          # a lane has one bar: replaced
    f2 = frame_markup(svg, 2)
    assert 'class="lm ' not in f2 and 'class="lt ' not in f2 and 'class="lu ' not in f2 and 'lb-S2' not in f2 and 'lb-S3' in f2


def test_lanes_marks_sit_inside_their_lane_so_a_lane_cue_keeps_them_lit():
    svg = v.lanes(["S2", "S3"], [{"marks": [("S2", 10, "ok", "S3")]}])
    assert svg.index('lr lr-S2') < svg.index('lm lm-0') < svg.index('lr lr-S3')


def test_lanes_a_target_before_the_bar_end_is_not_drawn_and_none_removes_it():
    svg = v.lanes(["S2"], [{"bars": {"S2": (0, 100, "run")}, "targets": {"S2": 200}},
                           {"targets": {"S2": None}}, {"bars": {"S2": (0, 250, "run")}, "targets": {"S2": 200}}])
    assert 'class="lt lt-S2"' in frame_markup(svg, 0)
    assert 'class="lt ' not in frame_markup(svg, 1) and 'class="lt ' not in frame_markup(svg, 2)


def test_lanes_escapes_text_and_rejects_authoring_mistakes():
    svg = v.lanes(["S2"], [{"axis": "a < b", "marks": [("S2", 10, "dot", "<b>")], "rules": [(5, "&")]}])
    assert "a &lt; b" in svg and "&lt;b&gt;" in svg and ">&amp;<" in svg
    for bad in ({"bars": {"S9": (0, 1, "hot")}}, {"bars": {"S2": (0, 999, "hot")}}, {"bars": {"S2": (0, 1, "blue")}},
                {"marks": [("S2", 1, "star", "")]}, {"rules": [(999, "x")]}):
        with pytest.raises(ValueError, match="lanes"):
            v.lanes(["S2"], [bad])
