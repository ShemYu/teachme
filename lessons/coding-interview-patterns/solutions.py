# Every snippet shown in the lesson, with the asserts used on screen,
# plus randomized checks against brute force at the bottom.
from collections import Counter, defaultdict, deque
from itertools import combinations
import heapq, random

# ---------------------------------------------------------------- A · hash map
def two_sum(nums, target):
    seen = {}                       # value -> index, only LEFT of i
    for i, x in enumerate(nums):
        need = target - x
        if need in seen:
            return seen[need], i
        seen[x] = i                 # insert AFTER the check
    return None

def group_anagrams(words):
    groups = defaultdict(list)
    for w in words:
        groups["".join(sorted(w))].append(w)   # key = canonical form
    return list(groups.values())

def subarray_sum(nums, k):
    seen = Counter({0: 1})          # the empty prefix
    prefix = count = 0
    for x in nums:
        prefix += x
        count += seen[prefix - k]   # earlier prefixes that complete k
        seen[prefix] += 1
    return count

# ---------------------------------------------------------------- B · two pointers
def pair_sum_sorted(a, target):
    left, right = 0, len(a) - 1
    while left < right:
        total = a[left] + a[right]
        if total == target:
            return left, right
        if total < target:
            left += 1               # a[left] too small for everyone
        else:
            right -= 1              # a[right] too big for everyone
    return None

def max_area(h):
    left, right, best = 0, len(h) - 1, 0
    while left < right:
        best = max(best, (right - left) * min(h[left], h[right]))
        if h[left] < h[right]:
            left += 1               # shorter wall can't do better
        else:
            right -= 1
    return best

def dedupe_sorted(a):
    write = 0                       # a[:write] = unique prefix
    for read in range(len(a)):
        if write == 0 or a[read] != a[write - 1]:
            a[write] = a[read]
            write += 1
    return write

def three_sum(nums, target=0):
    a = sorted(nums)
    out = []
    for i in range(len(a) - 2):
        if i > 0 and a[i] == a[i - 1]:
            continue                        # same anchor, same answers
        left, right = i + 1, len(a) - 1
        while left < right:
            total = a[i] + a[left] + a[right]
            if total < target:
                left += 1
            elif total > target:
                right -= 1
            else:
                out.append([a[i], a[left], a[right]])
                left += 1
                right -= 1
                while left < right and a[left] == a[left - 1]:
                    left += 1               # skip duplicate partners
    return out

# ---------------------------------------------------------------- C · sort, then scan
def merge_intervals(intervals):
    out = []
    for start, end in sorted(intervals):
        if not out or start > out[-1][1]:
            out.append([start, end])
        else:
            out[-1][1] = max(out[-1][1], end)
    return out

def can_attend(meetings):           # half-open [start, end)
    s = sorted(meetings)
    return all(s[i][1] <= s[i + 1][0] for i in range(len(s) - 1))

def min_rooms(meetings):            # half-open [start, end)
    ends = []                       # min-heap: end times of busy rooms
    for start, end in sorted(meetings):
        if ends and ends[0] <= start:
            heapq.heapreplace(ends, end)    # reuse the earliest-free room
        else:
            heapq.heappush(ends, end)       # open a new room
    return len(ends)

# ---------------------------------------------------------------- D · sliding window
def longest_unique(s):
    seen = set()
    left = best = 0
    for right, ch in enumerate(s):
        while ch in seen:
            seen.remove(s[left])
            left += 1
        seen.add(ch)
        best = max(best, right - left + 1)
    return best

def longest_k_distinct(s, k):
    count = Counter()
    left = best = 0
    for right, ch in enumerate(s):
        count[ch] += 1
        while len(count) > k:               # invalid: shrink
            count[s[left]] -= 1
            if count[s[left]] == 0:
                del count[s[left]]
            left += 1
        best = max(best, right - left + 1)  # record when valid
    return best

def shortest_at_least(nums, target):    # nums > 0, target > 0
    left = total = 0
    best = float("inf")
    for right, x in enumerate(nums):
        total += x
        while total >= target:              # valid: record, then shrink
            best = min(best, right - left + 1)
            total -= nums[left]
            left += 1
    return 0 if best == float("inf") else best

# ---------------------------------------------------------------- E · stack and queue
def brackets(s):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in s:
        if ch in "([{":
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
        else:
            raise ValueError("brackets only")
    return not stack

def next_greater(nums):
    ans = [-1] * len(nums)
    stack = []                      # indices still waiting; values decreasing
    for i, x in enumerate(nums):
        while stack and nums[stack[-1]] < x:
            ans[stack.pop()] = x    # x is the answer for everyone smaller
        stack.append(i)
    return ans

class Deduper:
    """Reject a key seen within ttl seconds of its last ACCEPTED time. Times non-decreasing."""
    def __init__(self, ttl):
        self.ttl = ttl
        self.q = deque()            # (time, key), oldest first
        self.live = set()           # keys accepted within the last ttl
    def accept(self, key, now):
        while self.q and self.q[0][0] <= now - self.ttl:
            _, old = self.q.popleft()
            self.live.discard(old)
        if key in self.live:
            return False            # rejected: no renewal
        self.q.append((now, key))
        self.live.add(key)
        return True


# ---------------------------------------------------------------- Python traps (body shown on screen)
def python_traps():
    a = [3, 1, 2]
    assert a.sort() is None                 # sorts in place, returns None
    assert sorted([3, 1, 2]) == [1, 2, 3]   # returns a new list

    grid = [[]] * 3
    grid[0].append(1)
    assert grid == [[1], [1], [1]]          # ONE inner list, 3 references
    grid = [[] for _ in range(3)]           # 3 separate lists

    q = deque([1, 2, 3])
    q.popleft()                             # O(1); list.pop(0) shifts: O(n)
    b = a[1:]                               # slicing copies: O(k) time + memory
    assert 3 in {1, 2, 3}                   # set: O(1) average; list: O(n)

    def add(x, acc=None):                   # never acc=[]: shared across calls
        acc = [] if acc is None else acc
        acc.append(x)
        return acc
    assert add(1) == [1] and add(2) == [2]

# ---------------------------------------------------------------- asserts shown on screen
python_traps()
assert two_sum([2, 7, 11, 15], 9) == (0, 1)
assert two_sum([3, 3], 6) == (0, 1)
assert two_sum([3], 6) is None
assert group_anagrams(["eat", "tea", "tan", "ate", "nat"]) == [["eat", "tea", "ate"], ["tan", "nat"]]
assert subarray_sum([1, 1, 1], 2) == 2
assert subarray_sum([3, 4, -7, 3], 3) == 3
assert pair_sum_sorted([1, 2, 4, 7, 11], 9) == (1, 3)
assert max_area([1, 8, 6, 2, 5, 4, 8, 3, 7]) == 49
assert dedupe_sorted([1, 1, 2, 3, 3]) == 3
assert three_sum([-1, 0, 1, 2, -1, -4]) == [[-1, -1, 2], [-1, 0, 1]]
assert three_sum([0, 0, 0, 0]) == [[0, 0, 0]]
assert merge_intervals([[1, 4], [2, 3], [4, 6], [8, 9]]) == [[1, 6], [8, 9]]
assert merge_intervals([]) == []
assert can_attend([[0, 30], [5, 10]]) is False
assert min_rooms([[0, 30], [5, 10], [15, 20]]) == 2
assert min_rooms([[1, 5], [5, 8]]) == 1
assert longest_unique("abba") == 2
assert longest_unique("") == 0
assert longest_k_distinct("eceba", 2) == 3
assert shortest_at_least([2, 3, 1, 2, 4, 3], 7) == 2
assert brackets("([]{})") is True
assert brackets("([)]") is False
assert brackets("((") is False
assert next_greater([2, 1, 2, 4, 3]) == [4, 2, 4, -1, -1]
d = Deduper(10)
assert [d.accept("A", t) for t in (0, 9, 10)] == [True, False, True]

# ---------------------------------------------------------------- randomized checks vs brute force
def overlap_closed(a, b):
    return a[0] <= b[1] and b[0] <= a[1]

for _ in range(3000):
    n = random.randint(0, 9)
    nums = [random.randint(-5, 5) for _ in range(n)]
    t = random.randint(-8, 8)
    r = two_sum(nums, t)
    brute = [(i, j) for i, j in combinations(range(n), 2) if nums[i] + nums[j] == t]
    assert (r is None) == (not brute)
    assert subarray_sum(nums, t) == sum(sum(nums[i:j]) == t for i in range(n) for j in range(i + 1, n + 1))
    a = sorted(nums)
    assert (pair_sum_sorted(a, t) is None) == (not any(a[i] + a[j] == t for i, j in combinations(range(n), 2)))
    exp3 = sorted({tuple(sorted(c)) for c in combinations(nums, 3) if sum(c) == t})
    assert sorted(map(tuple, three_sum(nums, t))) == exp3 and len(three_sum(nums, t)) == len(exp3)
    b = a[:]; k = dedupe_sorted(b); assert b[:k] == sorted(set(a))
    h = [random.randint(0, 9) for _ in range(n)]
    assert max_area(h) == max([(j - i) * min(h[i], h[j]) for i, j in combinations(range(n), 2)], default=0)
    pos = [random.randint(1, 6) for _ in range(n)]
    t = abs(t) + 1
    sl = [j - i for i in range(n) for j in range(i + 1, n + 1) if sum(pos[i:j]) >= t]
    assert shortest_at_least(pos, t) == min(sl, default=0)
    s = "".join(random.choice("abc") for _ in range(n))
    assert longest_unique(s) == max([j - i for i in range(n) for j in range(i + 1, n + 1) if len(set(s[i:j])) == j - i], default=0)
    kk = random.randint(1, 3)
    assert longest_k_distinct(s, kk) == max([j - i for i in range(n) for j in range(i + 1, n + 1) if len(set(s[i:j])) <= kk], default=0)
    assert next_greater(nums) == [next((y for y in nums[i + 1:] if y > x), -1) for i, x in enumerate(nums)]
    br = "".join(random.choice("()[]{}") for _ in range(n))
    def ok(x):
        while any(p in x for p in ("()", "[]", "{}")):
            for p in ("()", "[]", "{}"):
                x = x.replace(p, "")
        return x == ""
    assert brackets(br) == ok(br)
    iv = [sorted(random.sample(range(12), 2)) for _ in range(n)]
    m = merge_intervals(iv)
    covered = lambda pts: {p for s0, e0 in pts for p in range(2 * s0, 2 * e0 + 1)}   # half-steps
    assert covered(m) == covered(iv) and all(m[i][1] < m[i + 1][0] for i in range(len(m) - 1))
    peak = max([sum(s0 <= x < e0 for s0, e0 in iv) for x in range(13)], default=0)
    assert min_rooms(iv) == peak and can_attend(iv) == (peak <= 1)
    d = Deduper(3); last = {}; tt = 0
    for _ in range(n):
        tt += random.randint(0, 2); key = random.choice("xy")
        exp = key not in last or tt - last[key] >= 3
        if exp: last[key] = tt
        assert d.accept(key, tt) == exp
print("all ok")
