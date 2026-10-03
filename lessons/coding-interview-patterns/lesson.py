TITLE = "Coding interview · five patterns"

# Example lesson: the five patterns behind most easy-to-medium coding-interview problems (hash map, two pointers,
# sort + scan, sliding window, stack and queue), each with its family of variants. Every code block is pulled from
# solutions.py, which asserts each on-screen example and checks every function against brute force on random inputs.

# Narration voice: free macOS `say` by default. ElevenLabs: run `scripts/keys.py set` once, then build with
# --tts elevenlabs (or set TTS = "elevenlabs"); add --estimate first to see the character count and cost.
TTS = "say"
ELEVENLABS = {"voice_id": "XrExE9yKIg1WjnnlVkGX",  # Matilda: knowledgeable, professional (premade)
              "model": "eleven_multilingual_v2", "settings": {"stability": 0.55, "speed": 1.0}}

from visuals import Solutions, arr, pgrid, ticks, ivrow, card, panel_code   # skill's visual-proof components

S = Solutions(__file__)
src, body, asserts = S.src, S.body, S.asserts

# lesson-specific tweaks on top of the theme
STYLE = """<style>
.tbl{width:100%;border-collapse:collapse;font-size:23px}
.tbl th{text-align:left;font-size:16px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);padding:0 14px 12px}
.tbl td{padding:12px 14px;border-top:1px solid var(--line);vertical-align:top;line-height:1.35}
.tbl code,.card code{font-size:.9em}
.loop .node{font-size:22px;padding:18px 6px}
.ev{flex:1;background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px 18px;font-size:22px;line-height:1.4}
.ev b{font-family:"SF Mono",Menlo,monospace}
.qa li{font-size:24px !important;margin:9px 0 !important}
.qa .ans{color:var(--teal)}
.big-list li{font-size:24px !important;margin:9px 0 !important}
</style>"""

SLIDES = []

def slide(section, html, *steps):
    SLIDES.append((section, STYLE + html, list(steps)))


# ================================================================== 0 Title
slide("", """
<div class="title-wrap">
  <div class="kicker">Coding interview · Python · Senior level</div>
  <h1 class="big">Five patterns,<br>and their families</h1>
  <p class="lede s1">For every problem, say <em>what the container holds</em>, <em>why one pass keeps that true</em>,
  and <em>what changes when the contract changes</em>.</p>
  <div class="agenda s1">
    <div><b>01</b> Method and signal map</div>
    <div><b>05</b> Sliding window: contiguous runs</div>
    <div><b>02</b> Hash map: seen it before?</div>
    <div><b>06</b> Stack and queue</div>
    <div><b>03</b> Two pointers: safe elimination</div>
    <div><b>07</b> Python traps, the last 60 seconds</div>
    <div><b>04</b> Sort, then scan: intervals</div>
    <div><b>08</b> Closed-book recall and drill</div>
  </div>
</div>
""",
"This lesson covers the five patterns behind most easy to medium coding interview problems, plus the variants an interviewer is likely to build on top of each one. Everything is in Python, and every piece of code on screen was tested before it was rendered.",
"Here's the thesis. Each pattern is a container plus an invariant. For every problem, say what the container holds, why one pass keeps that true, and what changes when the contract changes. We'll do the method first, then five patterns, each with its core problem and its family, then Python traps, and a closed-book recall at the end.",
)

# ================================================================== 1 Method
slide("01 · Method", """
<h2>Seven steps, each one said out loud</h2>
<div class="loop">
  <div class="node q">Clarify<br><span class="muted sm">inputs · outputs</span></div><div class="arrow">→</div>
  <div class="node">Brute force<br><span class="muted sm">works + Big-O</span></div><div class="arrow">→</div>
  <div class="node">Structure<br><span class="muted sm">pick container</span></div><div class="arrow">→</div>
  <div class="node dec">Invariant<br><span class="muted sm">one sentence</span></div><div class="arrow">→</div>
  <div class="node">Code<br><span class="muted sm">minimal</span></div><div class="arrow">→</div>
  <div class="node dec">Hand-run<br><span class="muted sm">edges</span></div><div class="arrow">→</div>
  <div class="node a">Complexity<br><span class="muted sm">time · space</span></div>
</div>
<div class="grid2 mt s1">
  <div class="thesis" style="margin-top:0">The <b>invariant</b> is your correctness proof in one sentence: “Before each iteration, this container holds ___.”</div>
  <div class="thesis" style="margin-top:0">The <b>hand-run</b> catches the bug before the interviewer does. Stuck? Trace 3–5 elements and write the container's state.</div>
</div>
""",
"The method has seven steps. Clarify the inputs and outputs. Say a brute force that works, with its cost. Choose a data structure. State the invariant. Write the minimal code. Hand-run the edge cases. Report time and space. Each step is something the interviewer can see and check.",
"Two steps are where senior candidates stand out. The invariant, because it's your correctness proof in one sentence: before each iteration, this container holds something specific. And the hand-run, because it catches the bug before the interviewer does. When you're stuck, go back to a three to five element example and write down how the container changes.",
)

# ================================================================== 2 Signal map
slide("01 · Signal → pattern", """
<h2>What the problem says → what to reach for</h2>
<table class="tbl">
  <tr><th>If the problem says…</th><th>Reach for</th><th>Container holds</th><th>Typical cost</th></tr>
  <tr><td>“seen before?”, “count”, “pair”, “group by”</td><td><b>Hash map</b> · dict / set / Counter</td><td>what's been seen so far</td><td>O(n) avg</td></tr>
  <tr><td>sorted + pair · in place · “from both ends”</td><td><b>Two pointers</b></td><td>the region still possible</td><td>O(n)</td></tr>
  <tr class="s1"><td>intervals · overlap · schedule · events</td><td><b>Sort, then scan</b></td><td>the merged result so far</td><td>O(n log n)</td></tr>
  <tr class="s1"><td>longest / shortest contiguous substring or subarray</td><td><b>Sliding window</b></td><td>a valid contiguous run</td><td>O(n)</td></tr>
  <tr class="s2"><td>matching · nearest greater · undo</td><td><b>Stack</b></td><td>unfinished items, newest on top</td><td>O(n) amortized</td></tr>
  <tr class="s2"><td>arrival order · expire old · BFS</td><td><b>Queue</b> · <code>deque</code></td><td>items in time order</td><td>O(n) amortized</td></tr>
</table>
""",
"Here's the map from what the problem says to what you reach for. If it asks whether you've seen something before, for a count, a pair, or a grouping, use a dictionary, set, or Counter. If the input is sorted and you want a pair, or you must work in place, use two pointers.",
"If it mentions intervals, overlaps, or schedules, sort first, then scan once. If it asks for the longest or shortest contiguous substring or subarray, use a sliding window.",
"Matching brackets, nearest greater element, or undo means a stack. Arrival order, expiring old items, or breadth-first search means a queue, which in Python is a deque. Notice the third column: each pattern is defined by what its container holds. That's the sentence you'll say out loud. The next five sections take these one at a time.",
)

# ================================================================== 3 Two Sum
TS = src("two_sum")
slide("02 · Hash map", f"""
<h2>Two Sum: check first, then remember</h2>
<div class="grid2" style="grid-template-columns:1.05fr 1fr;gap:40px">
  {panel_code(TS + [""] + asserts("two_sum"))}
  <div>
    <div class="s1">
      <div class="trow">{arr([2, 7, 11, 15], {0: "I"}, {0: "i"}, idx=False)}<div class="tnote mono">need 7 · miss<br>seen = {{2: 0}}</div></div>
      <div class="trow">{arr([2, 7, 11, 15], {0: "ok", 1: "I"}, {1: "i"}, idx=False)}<div class="tnote mono">need 2 · hit<br>return (0, 1)</div></div>
    </div>
    {card("⊂", "Invariant", "Before index i, <code>seen</code> holds only elements left of i, so a hit never reuses i. Insert first and <code>[3]</code>, target 6 returns (0, 0).", "mt s2")}
    {card("O", "Cost", "O(n) time on <i>average</i> (dict lookup is average-case O(1)), O(n) space. Brute force: every pair, O(n²).", "mt s2")}
  </div>
</div>
""",
"Pattern one, the hash map, starting with Two Sum. The brute force checks every pair, which is quadratic. But for each x, the partner is already decided: it must be target minus x. So the question becomes: have I already seen target minus x? Walk once, compute need, check seen, and only then store the current value with its index.",
"Trace two, seven, eleven, fifteen, with target nine. At index zero, need is seven, a miss, so store two at index zero. At index one, need is two, a hit at index zero. Return zero, one.",
"The invariant: before index i, seen holds only elements to the left of i, so a hit always pairs two different indices. Insert first, and a single three with target six would pair with itself. The cost is linear time on average, because dictionary lookups are constant on average, not guaranteed, and linear extra space.",
)

# ================================================================== 4 Hash-map family
GA, SS = src("group_anagrams"), src("subarray_sum")
slide("02 · Hash-map family", f"""
<h2>The family is one decision: what's the key, what's the value?</h2>
<div class="grid2" style="grid-template-columns:1fr 1.05fr;gap:36px">
  <table class="tbl" style="font-size:22px">
    <tr><th>Problem</th><th>Key → value</th></tr>
    <tr><td><b>Two Sum</b></td><td>value → index</td></tr>
    <tr><td><b>Count pairs</b></td><td>value → count</td></tr>
    <tr><td><b>Group anagrams</b></td><td>canonical form → list of words</td></tr>
    <tr><td><b>Subarray sum = k</b></td><td>prefix sum → count, seeded <code>{{0: 1}}</code></td></tr>
    <tr><td><b>Duplicate within k</b></td><td>value → last index</td></tr>
    <tr><td><b>First unique char</b></td><td>char → count, then a 2nd pass</td></tr>
  </table>
  <div>
    <div class="s1">{panel_code(["from collections import Counter, defaultdict", ""] + GA, mark=(6,))}</div>
    <div class="s2 mt">{panel_code(SS, mark=(2, 6))}</div>
    <div class="note s2">sum(nums[i:j]) = P[j] − P[i] = k  ⇔  look up P[j] − k. Works with negatives.</div>
  </div>
</div>
""",
"The whole hash-map family comes down to one decision: what's the key, and what's the value. Two Sum maps value to index. Counting pairs maps value to count. Group anagrams maps a canonical form to a list of words. Subarray sum maps a prefix sum to a count. Duplicate within k maps a value to its last index. And first unique character counts in one pass, then scans again in order.",
"Group anagrams is all about the key. Sorting each word gives a canonical form, so eat, tea, and ate share the key a e t. That costs m log m per word of length m. With a fixed alphabet, a tuple of twenty-six letter counts is a linear-time key instead. Either way the key must be hashable, so a string or a tuple, never a list.",
"Subarray sum equals k is Two Sum in disguise. With prefix sums, the subarray from i to j sums to P of j minus P of i. So at each prefix, count how many earlier prefixes equal the current prefix minus k. Seed the Counter with zero mapped to one, so subarrays starting at index zero are counted. Unlike a sliding window, this works with negative numbers.",
)

# ================================================================== 5 Sorted two sum
A = [1, 2, 4, 7, 11]
PS = src("pair_sum_sorted")
slide("03 · Two pointers", f"""
<h2>Sorted input: walk inward from both ends</h2>
<div class="grid2" style="grid-template-columns:1fr 1.05fr;gap:40px">
  <div>
    <div class="trow">{arr(A, {0: "L", 4: "R"}, {0: "L", 4: "R"})}<div class="tnote mono">1 + 11 = 12<br><span class="warn">too big → R−−</span></div></div>
    <div class="trow">{arr(A, {0: "L", 3: "R", 4: "gone"}, {0: "L", 3: "R"})}<div class="tnote mono">1 + 7 = 8<br><span style="color:var(--accent)">too small → L++</span></div></div>
    <div class="trow">{arr(A, {0: "gone", 1: "ok", 3: "ok", 4: "gone"}, {1: "L", 3: "R"})}<div class="tnote mono">2 + 7 = 9<br><span style="color:var(--good)">return (1, 3)</span></div></div>
    {card("?", "O(n) time, O(1) space — but why is it safe?", "Each move discards candidates it never checked.", "mt s2")}
  </div>
  <div class="s1">{panel_code(PS + [""] + asserts("pair_sum_sorted"))}</div>
</div>
""",
"Pattern two, two pointers. When the array is sorted, put left at the smallest value and right at the largest. One plus eleven is twelve, too big, so move right inward. One plus seven is eight, too small, so move left. Two plus seven is nine: return one, three.",
"The code mirrors that. While left is less than right: equal returns, too small moves left up, too big moves right down. Strictly less than, because left equal to right would reuse one element.",
"That's linear time and constant extra space. But every move throws away candidates it never checked, so the interviewer will ask why that's safe. Here's the proof as a picture.",
)

# ================================================================== 6 Elimination proof
OPS6 = [(1, "kill", [(i, 4) for i in range(4)], ""), (1, "probe", [(0, 4)], "1"),
        (2, "kill", [(0, j) for j in range(1, 4)], ""), (2, "probe", [(0, 3)], "2"),
        (3, "hit", [(1, 3)], ""), (3, "probe", [(1, 3)], "3")]
slide("03 · Why it's safe", f"""
<h2>Each comparison deletes a whole row or column</h2>
<div class="grid2" style="grid-template-columns:auto 1fr;gap:60px;align-items:start">
  <div>{pgrid(A, OPS6)}<div class="axis mt">cell = a[row] + a[col] · sums grow → and ↓</div></div>
  <div class="stack">
    {card("1", "1 + 11 = 12 &gt; 9", "1 is the smallest partner left and it's still too big → <b>11's column is dead</b>.", "s1", red=True)}
    {card("2", "1 + 7 = 8 &lt; 9", "7 is the largest partner left and it's still too small → <b>1's row is dead</b>.", "s2", red=True)}
    {card("3", "2 + 7 = 9 ✓", "3 comparisons instead of 10.", "s3")}
    <div class="thesis s3" style="margin-top:6px">Invariant: any answer lies between L and R. One line deleted per step → ≤ n − 1 steps.</div>
  </div>
</div>
""",
"Put every pair in a triangle: rows are the left element, columns the right element, and each cell is the pair's sum. Because the array is sorted, sums grow to the right and downward. The pointers always sit at the top-right corner of the region not yet ruled out.",
"First comparison: one plus eleven is twelve, too big. One is the smallest value still in play, so eleven is too big with every remaining partner. The whole eleven column is gone, after one comparison.",
"Second: one plus seven is eight, too small. Seven is the largest value still in play, so one is too small with every remaining partner. The whole row for one is gone.",
"Third: two plus seven is nine, found after three checks instead of ten. Each comparison deletes a full row or column, so it takes at most n minus one steps. The invariant to say: if an answer exists, it's still between left and right.",
)

# ================================================================== 7 Two-pointer family
MA, DD = src("max_area"), src("dedupe_sorted")
slide("03 · Two-pointer family", f"""
<h2>Same pointers, different questions</h2>
<div class="grid2" style="grid-template-columns:1.1fr 1fr;gap:36px">
  <div>
    {panel_code(MA + [""] + asserts("max_area"), mark=(5, 6))}
    <div class="s1 mt">{panel_code(DD + [""] + asserts("dedupe_sorted"), mark=(2,))}</div>
  </div>
  <div class="stack">
    {card("↔", "Container with most water", "Area = width × shorter wall. Any closer partner is narrower and no taller → the shorter wall's row is dead. Move it.")}
    {card("⇉", "Same direction: read / write", "Invariant: <code>a[:write]</code> is the unique prefix so far. O(n) time, O(1) space; return the new length.", "s1")}
    {card("3", "Three Sum", "Fix an anchor, sorted Two Sum on the rest: O(n²). Skip duplicates in two places.", "s2")}
    {card("✓", "Also in this family", "Valid palindrome (ends inward) · merge two sorted arrays (from the back) · move zeroes (read/write).", "s2")}
  </div>
</div>
""",
"Container with most water uses the same elimination argument. The area is the width times the shorter wall. If the left wall is the shorter one, pairing it with any closer right wall makes the width smaller and the height no taller, so it can never beat what you just measured. Move the shorter wall, and you've deleted its whole row.",
"Pointers don't always walk toward each other. To remove duplicates from a sorted array in place, a read pointer and a write pointer move in the same direction. The invariant: the slice up to write holds the unique values seen so far. Linear time, constant space, and you return the new length.",
"Three-sum fixes one anchor and runs sorted Two Sum on the rest, which is quadratic. The next slide shows its duplicate handling. Others in the family: a palindrome check walks inward from both ends, merging two sorted arrays in place writes from the back, and move zeroes is another read-write pair.",
)

# ================================================================== 8 Three Sum code
T3 = src("three_sum")
slide("03 · Three Sum", f"""
<h2>Three Sum: an anchor + sorted Two Sum, de-duplicated</h2>
<div class="grid2" style="grid-template-columns:1.25fr 1fr;gap:40px">
  {panel_code(T3 + [""] + asserts("three_sum"), mark=(5, 6, 18, 19))}
  <div class="stack">
    {card("≡", "Inner loop = sorted Two Sum", "On <code>a[i+1:]</code>, aiming at <code>target − a[i]</code>. n anchors × O(n) = O(n²).")}
    {card("⇥", "Skip ①: repeated anchor", "<code>a[i] == a[i − 1]</code> would rebuild the same triples.", "s1")}
    {card("⇥", "Skip ②: repeated left partner", "No right-side skip needed: a bigger left value forces the right pointer to move anyway.", "s1")}
    {card("!", "Stress test: <code>[0, 0, 0, 0]</code>", "One triple, not four. Quadratic is expected: no O(n<sup>2−ε</sup>) algorithm is believed to exist (the 3SUM conjecture).", "s2", red=True)}
  </div>
</div>
""",
"Here's three-sum. Sort, then for each anchor, run sorted Two Sum on the suffix, aiming at the target minus the anchor. That's n anchors times a linear walk, so quadratic.",
"Duplicates are skipped in exactly two places. Skip an anchor equal to the previous one, because it would rebuild the same triples. And after recording a triple, move both pointers, then move left past repeated values. There's no need to skip on the right, because a strictly larger left value makes an equal right value overshoot, and the normal loop moves it.",
"Test four zeros out loud: one triple, not four. And if asked whether you can beat quadratic: the three-sum conjecture says no algorithm runs in n to the two minus epsilon, so quadratic is the expected answer.",
)

# ================================================================== 9 Merge intervals
MI = src("merge_intervals")
slide("04 · Sort, then scan", f"""
<h2>Sort by start; only the last merged interval can change</h2>
<div class="grid2" style="grid-template-columns:1.1fr 0.9fr;gap:32px">
  <div>
    {ticks()}
    {ivrow("[1, 4]", [(1, 4, "")], '<span class="muted">first → new block</span>')}
    {ivrow("[2, 3]", [(2, 3, "")], '<span class="warn s1">inside → end stays 4 (max)</span>')}
    {ivrow("[4, 6]", [(4, 6, "")], '<span class="s1" style="color:var(--accent)">touches 4 → end = 6</span>')}
    {ivrow("[8, 9]", [(8, 9, "")], '<span class="s1" style="color:var(--good)">8 &gt; 6 → new block</span>')}
    <div class="s2" style="margin-top:14px;border-top:1px solid var(--line);padding-top:12px">
      {ivrow("out", [(1, 6, "o"), (8, 9, "o")], '<span class="mono">[[1, 6], [8, 9]]</span>')}
    </div>
  </div>
  <div>
    {panel_code(MI + [""] + asserts("merge_intervals", [1]), mark=(4, 7))}
    {card("?", "Ask first: does touching count?", "Closed intervals: yes, merge. If not, change <code>&gt;</code> to <code>&gt;=</code>.", "mt s2")}
    {card("O", "O(n log n) sort + O(n) scan", "<code>sorted()</code> returns a new list; <code>list.sort()</code> returns <code>None</code>.", "mt s2")}
  </div>
</div>
""",
"Pattern three: sort, then scan, with merge intervals. Sort by start. The invariant: out holds the correct merged result so far, sorted and non-overlapping, so a new interval can only overlap the last one. That turns a pairwise problem into a single scan.",
"Trace one to four, two to three, four to six, and eight to nine. Two to three sits inside one to four, so the end stays four. That's why the code takes the max: overwriting the end with three would shrink coverage. Four to six touches at four, and with closed intervals touching merges, so the end grows to six. Eight starts after six, so it opens a new block.",
"The result is one to six, and eight to nine. The cost is n log n for the sort, then linear. Ask the contract question up front: do touching endpoints count as overlapping? If not, change greater-than to greater-than-or-equal. And remember that sorted returns a new list, while list dot sort works in place and returns None.",
)

# ================================================================== 10 Interval family
MR, CA = src("min_rooms"), src("can_attend")
slide("04 · Interval family", f"""
<h2>Same sort, different scan</h2>
<div class="grid2" style="grid-template-columns:1.05fr 1fr;gap:36px">
  <div>
    {panel_code(["import heapq", ""] + CA + [""] + MR + [""] + asserts("min_rooms"), mark=(5, 10, 11, 12, 13, 14))}
  </div>
  <table class="tbl" style="font-size:22px">
    <tr><th>Variant</th><th>The scan</th></tr>
    <tr><td><b>Can attend all?</b></td><td>Sort; each meeting ends by the next start. Half-open <code>[s, e)</code>: 5 and 5 don't clash</td></tr>
    <tr class="s1"><td><b>Min meeting rooms</b></td><td>Min-heap of end times; reuse the earliest-free room. Heap size = peak overlap. O(n log n)</td></tr>
    <tr class="s2"><td><b>Insert interval</b></td><td>Already sorted: copy before, merge overlapping, copy after. O(n)</td></tr>
    <tr class="s2"><td><b>Fewest removals</b></td><td>Greedy: sort by <i>end</i>, keep whatever finishes first</td></tr>
  </table>
</div>
""",
"The interval family shares the sort, and changes the scan. Can one person attend every meeting? Sort, then check that each meeting ends by the time the next one starts. These are half-open intervals, so a meeting ending at five and one starting at five don't clash. That's the opposite of the merge contract, which is exactly why you ask.",
"Minimum meeting rooms keeps a min-heap of end times for the rooms in use. For each meeting in start order, if the earliest-ending room is free by now, reuse it with heap replace. Otherwise open a new room. The heap's final size is the peak overlap. That's n log n time and linear space.",
"Two more to recognize. Inserting an interval into an already sorted, non-overlapping list is three phases: copy what's before, merge what overlaps, copy what's after, all in linear time. And removing the fewest intervals to make the rest non-overlapping is a greedy: sort by end time, and always keep the interval that finishes first.",
)

# ================================================================== 11 Longest unique
LU = src("longest_unique")
S = "abba"
slide("05 · Sliding window", f"""
<h2>Longest substring without repeats: shrink until valid</h2>
<div class="grid2" style="grid-template-columns:1fr 1fr;gap:36px">
  <div>
    {panel_code(LU + [""] + asserts("longest_unique"), mark=(5, 6, 7))}
    {card("∑", "Why a loop in a loop is still O(n)", "Each character enters once and leaves at most once: ≤ 2n set operations (average O(1) each). Space O(min(n, alphabet)).", "mt s2")}
  </div>
  <div class="s1">
    <div class="trow">{arr(list(S), {0: "I"}, {0: "L R"}, idx=False)}<div class="tnote mono">add a · best 1</div></div>
    <div class="trow">{arr(list(S), {0: "I", 1: "I"}, {0: "L", 1: "R"}, idx=False)}<div class="tnote mono">add b · best 2</div></div>
    <div class="trow">{arr(list(S), {0: "gone", 1: "gone", 2: "R"}, {2: "L R"}, idx=False)}<div class="tnote mono">b in window: drop a,<br>drop b, add b</div></div>
    <div class="trow">{arr(list(S), {0: "gone", 1: "gone", 2: "I", 3: "I"}, {2: "L", 3: "R"}, idx=False)}<div class="tnote mono">add a · window "ba"<br>best stays 2</div></div>
  </div>
</div>
""",
"Pattern four, the sliding window, with the longest substring without repeating characters. The invariant: after shrinking, the window from left to right has no duplicates, and seen is exactly its characters. Expand right one character at a time, and if the new character is already in the window, shrink from the left until it isn't.",
"Trace a b b a. The window grows to a b. The second b conflicts, and removing a isn't enough, because the first b is still there. That's why it's a while loop, not an if: drop a, drop b, then add the new b. Finally a joins, the window is b a, and the best stays two.",
"Why is a loop inside a loop still linear? Each character enters the window once and leaves at most once, so there are at most two n set operations, each constant on average. Space is bounded by the alphabet. The alternative stores each character's last index and jumps left directly, but then left must never move backwards, which is exactly what a b b a tests.",
)

# ================================================================== 12 Two window templates
KD, SA = src("longest_k_distinct"), src("shortest_at_least")
slide("05 · Two templates", f"""
<h2>Longest vs shortest: where you record the answer</h2>
<div class="grid2" style="gap:30px">
  <div>
    <div class="label">Longest · shrink while <span style="color:var(--red)">invalid</span>, then record</div>
    {panel_code(["from collections import Counter", ""] + KD + [""] + asserts("longest_k_distinct"), mark=(8, 13), cls="tight-code sm-code pa")}
  </div>
  <div class="s1">
    <div class="label">Shortest · while <span style="color:var(--good)">valid</span>: record, then shrink</div>
    {panel_code(SA + [""] + asserts("shortest_at_least"), mark=(6, 7), cls="tight-code sm-code")}
  </div>
</div>
<div class="thesis s2">Both need <b>monotonicity</b>: growing the window only moves it one way. Negative numbers break that for sums → <em>prefix sums + hash map</em>.</div>
""",
"Most window problems are one of two templates, and the difference is where you record the answer. For the longest window: expand, shrink while the window is invalid, then record. Longest substring with at most k distinct characters is the example. A Counter tracks the window, and you delete a key when its count drops to zero, so the Counter's length is the number of distinct characters.",
"For the shortest window: expand, then while the window is valid, record and shrink. Shortest subarray with sum at least target: on two, three, one, two, four, three, with target seven, the answer is two, from four plus three. The contract is that all numbers and the target are positive.",
"Both templates rely on monotonicity: growing the window only ever pushes it one way, toward invalid or toward valid. Check that before reaching for a window. With negative numbers, adding an element can lower the sum, so the shrink rule stops being trustworthy. Use prefix sums with a hash map instead, which is the hash-map family again.",
)

# ================================================================== 13 Window family
slide("05 · Window family", """
<h2>The window family on one page</h2>
<table class="tbl">
  <tr><th>Problem</th><th>Window state</th><th>Template</th></tr>
  <tr><td><b>Longest without repeating</b></td><td>set, or last index per char</td><td>longest</td></tr>
  <tr><td><b>Longest with ≤ k distinct</b></td><td>Counter; delete at 0</td><td>longest</td></tr>
  <tr><td><b>Shortest with sum ≥ target</b> (positives)</td><td>running sum</td><td>shortest</td></tr>
  <tr><td><b>Permutation / anagram of p in s</b></td><td>two Counters, size len(p)</td><td>fixed size</td></tr>
  <tr><td><b>Max sum of k consecutive</b></td><td>running sum: + entering, − leaving</td><td>fixed size</td></tr>
  <tr class="warnrow s1"><td><b>Subarray sum = k, negatives allowed</b></td><td>✗ not monotonic</td><td>prefix sum + dict</td></tr>
</table>
""",
"Here's the window family on one page. The first three use the variable templates you just saw. Fixed-size windows are simpler. To find a permutation of p inside s, slide a window of length p, add the entering character, drop the leaving one, and compare Counters. Maximum sum of k consecutive elements is the same move with a running sum.",
"The last row is the trap. Any sum condition with negative numbers isn't monotonic, so it's a prefix-sum problem, not a window. Saying why you're not using a window is as strong a signal as using one correctly.",
)

# ================================================================== 14 Brackets
BR = src("brackets")
slide("06 · Stack", f"""
<h2>A stack holds what's still unfinished</h2>
<div class="grid2" style="grid-template-columns:1.05fr 1fr;gap:36px">
  {panel_code(BR + [""] + asserts("brackets"), mark=(7, 8))}
  <div>
    <div class="label">“([)]”</div>
    <div class="s1">
      <div class="trow"><div class="tlabel">read (</div>{arr(["("], idx=False)}<div class="tnote muted">push</div></div>
      <div class="trow"><div class="tlabel">read [</div>{arr(["(", "["], {1: "I"}, idx=False)}<div class="tnote muted">push</div></div>
      <div class="trow"><div class="tlabel">read )</div>{arr(["(", "["], {1: "bad"}, idx=False)}<div class="tnote">top is <b>[</b>, needs <b>(</b> → <span style="color:var(--red)">False</span></div></div>
    </div>
    {card("#", "Counting isn't enough", "“([)]” has balanced counts. And check the stack is empty at the end: “((” must fail.", "mt s1")}
    {card("O", "O(n) time, O(n) space", "Worst case: all openers.", "mt s2")}
  </div>
</div>
""",
"Pattern five, stack and queue, starting with valid brackets. The stack holds the opening brackets that haven't been closed yet, innermost on top, and a closing bracket can only match the top. The contract here is that the input contains only brackets, and anything else raises an error. Ask the interviewer what they want instead.",
"Trace open paren, open square, close paren, close square. Push the paren, push the square. The close paren meets a square on top, so fail immediately. Counting each type wouldn't catch this, because the counts balance. And at the end the stack must be empty, or two open parens would pass.",
"It's linear time, and linear space in the worst case, when every character is an opener.",
)

# ================================================================== 15 Monotonic stack
NG = src("next_greater")
slide("06 · Monotonic stack", f"""
<h2>Next greater element: the stack waits, in decreasing order</h2>
<div class="grid2" style="grid-template-columns:1fr 1.05fr;gap:36px">
  <div>
    {panel_code(NG + [""] + asserts("next_greater"), mark=(5, 6))}
    {card("⇵", "Variants", "Daily temperatures: store <code>i − j</code> instead of the value · previous smaller: flip <code>&lt;</code> · min-stack: push (value, running min).", "mt s2")}
  </div>
  <div class="s1">
    <div class="trow"><div class="tlabel">x = 2</div>{arr([2], idx=False)}<div class="tnote muted">push</div></div>
    <div class="trow"><div class="tlabel">x = 1</div>{arr([2, 1], idx=False)}<div class="tnote muted">push</div></div>
    <div class="trow"><div class="tlabel">x = 2</div>{arr([2, 2], {1: "I"}, idx=False)}<div class="tnote">pops 1 → ans[1] = 2</div></div>
    <div class="trow"><div class="tlabel">x = 4</div>{arr([4], {0: "I"}, idx=False)}<div class="tnote">pops 2, 2 → ans[2] = ans[0] = 4</div></div>
    <div class="trow"><div class="tlabel">x = 3</div>{arr([4, 3], idx=False)}<div class="tnote muted">push · 4, 3 never answered → −1</div></div>
  </div>
</div>
""",
"The stack family's most common medium problem is next greater element, or its twin, daily temperatures. Keep a stack of indices still waiting for a greater value. Their values decrease from bottom to top, which is why it's called a monotonic stack.",
"Trace two, one, two, four, three. Push two, push one. The next two is greater than one, so it answers one and pops it, then waits on top of the first two. Four is greater than both twos, so it answers both. Three waits on top of four, and neither ever gets an answer, so they keep minus one.",
"Again a loop inside a loop, and again linear, because each index is pushed once and popped at most once. Variants: daily temperatures stores the distance, i minus the popped index, instead of the value. Previous smaller element flips the comparison. And a min-stack pushes each value together with the running minimum.",
)

# ================================================================== 16 Queue: TTL dedupe
DQ = src("Deduper")
slide("06 · Queue", f"""
<h2>A queue holds events in time order: TTL de-duplication</h2>
<div class="grid2" style="grid-template-columns:1.05fr 1fr;gap:36px">
  <div>
    {panel_code(["from collections import deque", ""] + DQ, mark=(9, 10, 11, 12, 13))}
    {card("⇤", "deque, not list", "<code>popleft()</code> is O(1); <code>list.pop(0)</code> shifts everything: O(n).", "mt s2")}
  </div>
  <div>
    <div class="label">Spec (say it first)</div>
    <div class="note" style="margin-top:0">Reject a key for 10 s after it's <b>accepted</b> · rejections don't renew · time never goes backwards</div>
    <div class="row mt s1" style="gap:12px">
      <div class="ev"><b>t=0</b> A<br><span style="color:var(--good)">accept</span></div>
      <div class="ev"><b>t=9</b> A<br><span style="color:var(--red)">reject</span></div>
      <div class="ev"><b>t=10</b> A<br><span style="color:var(--good)">0 ≤ 10 − 10: expired → accept</span></div>
    </div>
    {card("!", "Where the design breaks", "Renew on every sighting → stale queue entries; store latest expiry per key. Out-of-order events → queue no longer sorted.", "mt s2", red=True)}
    {card("≡", "Same shape: rate limiter", "≤ N requests per window: deque of timestamps; pop expired, allow if fewer than N remain.", "mt s2")}
  </div>
</div>
""",
"The queue example: de-duplicate events with a time to live. Here the spec matters more than the code, so say it first. After a key is accepted, reject the same key for ten seconds. Rejections don't renew the timer. And timestamps never go backwards.",
"The queue holds accepted events in time order, and the set holds keys that are still live. On each event, first pop everything that has expired, then check the set. Trace it: A at time zero is accepted. A at nine is rejected. At ten, the entry from time zero expires, so A is accepted again.",
"Use a deque, because popleft is constant time, while list pop of zero shifts every remaining element. And know where the spec breaks the design. If every sighting renewed the timer, an old queue entry could delete a renewed key, so you'd store each key's latest expiry and skip stale entries. Out-of-order events break the assumption that the queue is sorted by time. A rate limiter is the same shape: a deque of timestamps, pop the expired ones, and allow the request if fewer than n remain.",
)

# ================================================================== 17 Python traps
slide("07 · Python traps", f"""
<h2>Python traps that cost points live</h2>
<div class="grid2" style="grid-template-columns:1.25fr 1fr;gap:36px">
  {panel_code(body("python_traps"))}
  <div class="stack">
    {card("1", "<code>x = x.sort()</code> → None", "In place, returns None. Use <code>sorted()</code> for a copy.")}
    {card("2", "<code>[[]] * n</code> aliases", "One inner list, n references. Use a comprehension.")}
    {card("3", "Hidden O(n) inside a loop", "<code>list.pop(0)</code>, slicing, <code>x in list</code> → accidental O(n²).", "s1")}
    {card("4", "Mutable default argument", "<code>acc=[]</code> is created once and shared across calls.", "s1")}
  </div>
</div>
""",
"Python traps that cost points in a live session. List dot sort sorts in place and returns None, so writing x equals x dot sort leaves you holding None. Use sorted when you want a new list. And multiplying a list of lists creates one inner list referenced n times. Appending to one row appends to all of them, so build grids with a comprehension.",
"Then the hidden linear costs. List pop of zero shifts every element. Slicing copies. Membership in a list scans it, while a set is constant on average. Any of these inside a loop quietly makes it quadratic. Finally, never use a mutable default argument, because it's created once and shared across calls.",
)

# ================================================================== 18 60-second check
slide("07 · The last 60 seconds", """
<h2>Before you say “done”: a 60-second check</h2>
<div class="grid2">
  <div class="panel">
    <div class="label">After writing</div>
    <ul class="tight big-list">
      <li><b>Contract:</b> return type, no-answer value, original indices, may I mutate the input?</li>
      <li><b>State:</b> initialized right? When added, removed, moved? Does every iteration progress?</li>
      <li><b>Edges:</b> <code>[]</code>, one element, duplicates, touching endpoints, all equal, no answer — only the ones this problem can break</li>
    </ul>
  </div>
  <div class="panel s1">
    <div class="label">When truly stuck</div>
    <ul class="tight big-list">
      <li>Say the simplest working solution and its bottleneck</li>
      <li>Trace 3–5 elements; write the container and pointers at each step</li>
      <li>No proof of the optimization after ~2 minutes? Finish the working version first, then discuss</li>
      <li>“I see a counterexample. Let me trace the state and fix the condition.”</li>
    </ul>
  </div>
</div>
""",
"Before you say done, spend sixty seconds on three checks. The contract: return type, the no-answer value, original indices, and whether you may mutate the input. The state: is it initialized right, when is it added to, removed from, or moved, and does every iteration make progress? And the edges: empty, one element, duplicates, touching endpoints, all equal, and no answer, picking only the ones this problem can break.",
"When you're truly stuck, say the simplest working solution and its bottleneck out loud. Trace three to five elements, writing down the container and pointers at each step. If you can't prove the optimization within about two minutes, finish the working version first, then discuss the improvement. A working quadratic solution beats an unfinished linear one. And when you find a bug, narrate it: I see a counterexample, let me trace the state and fix the condition.",
)

# ================================================================== 19 Closed-book recall
slide("08 · Closed-book recall", """
<h2>Pause and answer out loud (≈20 s each)</h2>
<ol class="recap qa">
  <li>Two Sum inserts <i>before</i> checking. <code>[3]</code>, target 6 → ? <span class="ans s1">(0, 0): pairs with itself. Check, then insert.</span></li>
  <li>Merge <code>[1, 10]</code> then <code>[2, 3]</code>: why <code>max</code>? <span class="ans s1">Coverage can't shrink; the end stays 10.</span></li>
  <li>Sorted pair, sum too small: why move left? Why not <code>left &lt;= right</code>? <span class="ans s1">Too small even with the largest partner; equal reuses one element.</span></li>
  <li>“abba”: why <code>while</code>, and why still O(n)? <span class="ans s1">The old b survives one removal; each char enters and leaves once.</span></li>
  <li>Rooms for <code>[1, 5]</code>, <code>[5, 8]</code>? <span class="ans s1">1 if half-open — but ask.</span></li>
  <li>Subarray sum = k with negatives: window? <span class="ans s1">No: prefix sums + Counter seeded {0: 1}.</span></li>
</ol>
""",
"Pause the video now, and answer each one out loud in about twenty seconds. Two Sum that inserts before checking, on a single three with target six. Merging one to ten with two to three. Why the sorted pair moves left when the sum is too small. Why a b b a needs a while loop. How many rooms for one to five and five to eight. And whether subarray sum with negatives is a window problem.",
"Answers. Insert-first returns zero, zero, because the element pairs with itself. The merged end must stay ten, so take the max. Too small with the largest remaining partner means too small with all of them, and left equal to right would reuse an element. One removal leaves the old b in the window, so shrink in a loop, and each character still enters and leaves once. One room under half-open intervals, but ask. And negatives mean prefix sums with a Counter seeded with zero.",
)

# ================================================================== 20 Recap
slide("Recap", """
<h2>Five takeaways, one drill</h2>
<ol class="recap">
  <li>Before code, say the <b>container</b> and its <b>invariant</b>.</li>
  <li>Hash map: choose the <b>key and the value</b>; check, then insert.</li>
  <li>Sorting buys <b>safe elimination</b> (two pointers) and <b>one-pass merging</b> (intervals).</li>
  <li>Window: longest = shrink while invalid · shortest = shrink while valid · negatives → prefix sums.</li>
  <li>Stack for unfinished items, deque for arrival order: <b>amortized O(n)</b>.</li>
</ol>
<div class="exercise s1"><b>Closed book, AI off, blank editor:</b> pick the two you're least sure of — <code>merge_intervals</code>, <code>longest_unique</code>, <code>min_rooms</code>, <code>next_greater</code> — 10–15 min each, saying the contract and invariant out loud. Then check against <code>solutions.py</code>.</div>
""",
"Five takeaways. Before code, say the container and its invariant. For hash maps, choose the key and the value, and check before you insert. Sorting buys you safe elimination with two pointers, and one-pass merging for intervals. For windows, the longest template shrinks while invalid, the shortest shrinks while valid, and negative numbers send you to prefix sums. And stacks hold unfinished items while deques hold arrival order, both in amortized linear time.",
"Your drill: book closed, A I off, blank editor. Pick the two you're least sure of among merge intervals, longest unique, minimum rooms, and next greater. Give each ten to fifteen minutes, saying the contract and invariant out loud, then check yourself against solutions dot p y in this lesson's folder.",
)
