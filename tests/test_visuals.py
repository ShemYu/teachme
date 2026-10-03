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
