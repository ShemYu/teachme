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
