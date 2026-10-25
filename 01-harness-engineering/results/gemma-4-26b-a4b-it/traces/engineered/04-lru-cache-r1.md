# 04-lru-cache / engineered / run 1
solved=True end=finished steps=14 tokens=103460+1429

## SYSTEM
```
You are a careful software engineer working in a small Python repository. Resolve the issue by changing the code.

How to work:
1. Orient: look at the repository tree, then use `search` to find the code the issue is about. The root cause may be in a different file from the one the issue mentions.
2. Reproduce: run the tests and read what fails.
3. Make a checklist of every requirement in the issue, including each edge case and example it mentions. Write that checklist into your notes with `update_notes` and tick items off as you go.
4. Fix the root cause with small, targeted changes. Keep everything that already works working.
5. Verify: run the tests again. The existing tests do not cover every requirement, so for anything they miss, add a small test file of your own at the repository root (for example `test_issue_checks.py`) and run it.
6. When every checklist item is handled and all tests pass, call `finish` with a one-line summary.

Rules:
- Never edit the existing files in tests/. They define correct behaviour; change the code under test instead.
- Keep public function names and signatures unless the issue says otherwise.
- Standard library only.
- Act through tool calls. Do not describe a change you intend to make; make it.
```
## USER
```
<issue>
`LRUCache` in `cache.py` is supposed to evict the least recently *used* key, but it evicts the oldest *inserted* key.

Expected behaviour:
- `get(key)` counts as a use and makes the key most recent.
- `put(key, value)` on an existing key updates the value and makes it most recent.
- `key in cache` must work, and must NOT count as a use.
- `capacity=0` is allowed; the cache then stores nothing.
- A negative capacity raises `ValueError`.
</issue>

Repository (path, size):
cache.py  (16 lines, 467 bytes)
tests/test_cache.py  (20 lines, 376 bytes)  [read-only]
Files marked [read-only] cannot be changed.
```
## ASSISTANT
```
<thought>Okay, I understand the issue. The `LRUCache` implementation in `cache.py` is behaving like a FIFO cache instead of an LRU cache. I need to fix it to follow the LRU rules, and also ensure it handles `capacity=0` and negative capacity correctly.

First, I'll start by exploring the repository to see the current implementation of `LRUCache`.</thought>
```
## ASSISTANT -> list_files
```json
{"directory":"."}
```
## TOOL
```
cache.py  (16 lines, 467 bytes)
tests/test_cache.py  (20 lines, 376 bytes)  [read-only]
```
## ASSISTANT
```
<thought>Okay, let's read `cache.py` to see the current implementation.</thought>
```
## ASSISTANT -> read_file
```json
{"path":"cache.py"}
```
## TOOL
```
    1  class LRUCache:
    2      def __init__(self, capacity):
    3          self.capacity = capacity
    4          self.data = {}
    5  
    6      def get(self, key, default=None):
    7          return self.data.get(key, default)
    8  
    9      def put(self, key, value):
   10          if key not in self.data and len(self.data) >= self.capacity:
   11              oldest = next(iter(self.data))
   12              del self.data[oldest]
   13          self.data[key] = value
   14  
   15      def __len__(self):
   16          return len(self.data)
[cache.py: lines 1-16 of 16]
```
## ASSISTANT
```
<thought>The current implementation of `LRUCache` is indeed a FIFO cache because it uses `next(iter(self.data))` to find the oldest key, and `self.data.get(key, default)` in `get` doesn't update the order. In Python 3.7+, dictionaries maintain insertion order.

Let's look at the requirements:
1. `get(key)` counts as a use and makes the key most recent.
2. `put(key, value)` on an existing key updates the value and makes it most recent.
3. `key in cache` must work, and must NOT count as a use.
4. `capacity=0` is allowed; the cache then stores nothing.
5. A negative capacity raises `ValueError`.

I'll start by running the existing tests to see what they cover.</thought>
```
## ASSISTANT -> run_tests
```json
{"path":"tests/test_cache.py"}
```
## TOOL
```
TESTS FAILING (1 failed, 1 passed in 0.05s)
.F                                                                       [100%]
================================== FAILURES ===================================
_____________________________ test_get_refreshes ______________________________
tests\test_cache.py:19: in test_get_refreshes
    assert c.get("a") == 1
E   AssertionError: assert None == 1
E    +  where None = get('a')
E    +    where get = <cache.LRUCache object at 0x000002EC49DE16D0>.get
1 failed, 1 passed in 0.05s
```
## ASSISTANT
```
<thought>Okay, the tests failed. Let's see what `tests/test_cache.py` contains.</thought><thought>I'll read `tests/test_cache.py` to understand the existing tests and why `test_get_refreshes` failed. Since I cannot edit it, I'll just read it.</thought>
```
## ASSISTANT -> read_file
```json
{"path":"tests/test_cache.py"}
```
## TOOL
```
    1  from cache import LRUCache
    2  
    3  
    4  def test_evicts_when_full():
    5      c = LRUCache(2)
    6      c.put("a", 1)
    7      c.put("b", 2)
    8      c.put("c", 3)
    9      assert len(c) == 2
   10      assert c.get("c") == 3
   11  
   12  
   13  def test_get_refreshes():
   14      c = LRUCache(2)
   15      c.put("a", 1)
   16      c.put("b", 2)
   17      c.get("a")
   18      c.put("c", 3)
   19      assert c.get("a") == 1
   20      assert c.get("b") is None
[tests/test_cache.py: lines 1-20 of 20]
```
## ASSISTANT
```
<thought>The test `test_get_refreshes` failed because `c.get("a")` returned `None` instead of `1`.
Wait, looking at `cache.py`:
```python
    6      def get(self, key, default=None):
    7          return self.data.get(key, default)
```
And `test_get_refreshes`:
```python
13  def test_get_refreshes():
14      c = LRUCache(2)
15      c.put("a", 1)
16      c.put("b", 2)
17      c.get("a")
18      c.put("c", 3)
19      assert c.get("a") == 1
20      assert c.get("b") is None
```
In `test_get_refreshes`:
1. `c = LRUCache(2)` -> `self.data = {}`, `self.capacity = 2`
2. `c.put("a", 1)` -> `self.data = {"a": 1}`
3. `c.put("b", 2)` -> `self.data = {"a": 1, "b": 2}`
4. `c.get("a")` -> returns `1`. `self.data` is still `{"a": 1, "b": 2}` (because it's FIFO)
5. `c.put("c", 3)` -> `len(self.data)` is 2, which is `>= self.capacity`.
   `oldest = next(iter(self.data))` -> `oldest` is `"a"`.
   `del self.data["a"]` -> `self.data = {"b": 2}`
   `self.data["c"] = 3` -> `self.data = {"b": 2, "c": 3}`
6. `assert c.get("a") == 1` -> `c.get("a")` returns `None` because `"a"` was evicted.

So the test failed as expected because the current implementation is FIFO.

Now I'll create a checklist of requirements.

Requirements:
- [ ] `get(key)` counts as a use and makes the key most recent.
- [ ] `put(key, value)` on an existing key updates the value and makes it most recent.
- [ ] `key in cache` must work, and must NOT count as a use.
- [ ] `capacity=0` is allowed; the cache then stores nothing.
- [ ] A negative capacity raises `ValueError`.

I'll also need to implement `__contains__` for `key in cache`.

Wait, `capacity=0` is allowed. Let's see how `put` handles it.
If `capacity=0`:
`c.put("a", 1)`
`if key not in self.data and len(self.data) >= self.capacity:`
`len(self.data)` is 0, `self.capacity` is 0. `0 >= 0` is True.
`oldest = next(iter(self.data))` -> `StopIteration` because `self.data` is empty.

So I need to handle `capacity=0` in `put`.

And negative capacity:
`c = LRUCache(-1)`
`self.capacity = -1`
`c.put("a", 1)`
`if key not in self.data and len(self.data) >= self.capacity:`
`len(self.data)` is 0, `self.capacity` is -1. `0 >= -1` is True.
`oldest = next(iter(self.data))` -> `StopIteration`.

So I need to add validation in `__init__`.

Let's update my notes.</thought>
```
## ASSISTANT -> update_notes
```json
{"notes":"Requirements:\n- [ ] `get(key)` counts as a use and makes the key most recent.\n- [ ] `put(key, value)` on an existing key updates the value and makes it most recent.\n- [ ] `key in cache` must work, and must NOT count as a use.\n- [ ] `capacity=0` is allowed; the cache then stores nothing.\n- [ ] A negative capacity raises `ValueError`.\n"}
```
## TOOL
```
Notes saved.
```
## ASSISTANT
```
<thought>I'll start by creating a reproduction test file `test_issue_checks.py` that covers all the requirements.</thought>
```
## ASSISTANT -> create_file
```json
{"path":"test_issue_checks.py","content":"from cache import LRUCache\nimport pytest\n\ndef test_get_refreshes():\n    c = LRUCache(2)\n    c.put(\"a\", 1)\n    c.put(\"b\", 2)\n    c.get(\"a\")\n    c.put(\"c\", 3)\n    assert c.get(\"a\") == 1\n    assert c.get(\"b\") is None\n\ndef test_put_updates_existing_key_and_refreshes():\n    c = LRUCache(2)\n    c.put(\"a\", 1)\n    c.put(\"b\", 2)\n    c.put(\"a\", 3)\n    c.put(\"c\", 4)\n    assert c.get(\"a\") == 3\n    assert c.get(\"b\") is None\n    assert c.get(\"c\") == 4\n\ndef test_contains_does_not_refresh():\n    c = LRUCache(2)\n    c.put(\"a\", 1)\n    c.put(\"b\", 2)\n    assert \"a\" in c\n    c.put(\"c\", 3)\n    assert c.get(\"a\") == 1\n    assert c.get(\"b\") is None\n\ndef test_capacity_zero():\n    c = LRUCache(0)\n    c.put(\"a\", 1)\n    assert len(c) == 0\n    assert c.get(\"a\") is None\n\ndef test_negative_capacity():\n    with pytest.raises(ValueError):\n        LRUCache(-1)\n\ndef test_len():\n    c = LRUCache(2)\n    c.put(\"a\", 1)\n    c.put(\"b\", 2)\n    assert len(c) == 2\n    c.put(\"c\", 3)\n    assert len(c) == 2\n"}
```
## TOOL
```
Created test_issue_checks.py (49 lines).
```
## ASSISTANT
```
<thought>Now I run the newly created tests.</thought>
```
## ASSISTANT -> run_tests
```json
{"path":"test_issue_checks.py"}
```
## TOOL
```
TESTS FAILING (5 failed, 1 passed in 0.08s)
FFFFF.                                                                   [100%]
================================== FAILURES ===================================
_____________________________ test_get_refreshes ______________________________
test_issue_checks.py:10: in test_get_refreshes
    assert c.get("a") == 1
E   AssertionError: assert None == 1
E    +  where None = get('a')
E    +    where get = <cache.LRUCache object at 0x000001E0DA92C830>.get
_________________ test_put_updates_existing_key_and_refreshes _________________
test_issue_checks.py:19: in test_put_updates_existing_key_and_refreshes
    assert c.get("a") == 3
E   AssertionError: assert None == 3
E    +  where None = get('a')
E    +    where get = <cache.LRUCache object at 0x000001E0DA911590>.get
_______________________ test_contains_does_not_refresh ________________________
test_issue_checks.py:27: in test_contains_does_not_refresh
    assert "a" in c
           ^^^^^^^^
E   TypeError: argument of type 'LRUCache' is not iterable
_____________________________ test_capacity_zero ______________________________
test_issue_checks.py:34: in test_capacity_zero
    c.put("a", 1)
cache.py:11: in put
    oldest = next(iter(self.data))
             ^^^^^^^^^^^^^^^^^^^^^
E   StopIteration
___________________________ test_negative_capacity ____________________________
test_issue_checks.py:39: in test_negative_capacity
    with pytest.raises(ValueError):
         ^^^^^^^^^^^^^^^^^^^^^^^^^
E   Failed: DID NOT RAISE ValueError
5 failed, 1 passed in 0.08s
```
## ASSISTANT
```
<thought>Okay, the tests failed as expected. Now I will implement the fixes in `cache.py`.

To implement LRU in Python, I can use `collections.OrderedDict`. It has `move_to_end` which is perfect for this.

Let's plan the changes in `cache.py`:
1. Import `OrderedDict` from `collections`.
2. In `__init__`:
   - Check if `capacity < 0`, if so, raise `ValueError`.
   - Initialize `self.data` as `OrderedDict()`.
3. In `get`:
   - If `key` is in `self.data`, use `self.data.move_to_end(key)` to make it most recent.
   - Return the value.
4. In `put`:
   - If `key` is in `self.data`:
     - Update the value.
     - `self.data.move_to_end(key)` to make it most recent.
   - If `key` is not in `self.data`:
     - If `self.capacity > 0` and `len(self.data) >= self.capacity`:
       - `self.data.popitem(last=False)` to remove the oldest item.
     - If `self.capacity > 0`:
       - `self.data[key] = value`
     - If `self.capacity == 0`:
       - Do nothing (or rather, don't add it).
5. Implement `__contains__`:
   - `return key in self.data`

Wait, if `capacity=0`, `put` should not add anything.
If `capacity=0`, `len(self.data)` will always be 0.
In `put(key, value)`:
If `key` not in `self.data`:
  If `len(self.data) >= self.capacity`:
    If `self.capacity > 0`:
       `oldest = next(iter(self.data))`
       `del self.data[oldest]`
    else: # capacity is 0
       # we don't want to add anything if capacity is 0
       return
  `self.data[key] = value`

Actually, if `capacity=0`, `len(self.data)` is 0, and `self.capacity` is 0. `0 >= 0` is true.
If I use `OrderedDict`:

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        if capacity < 0:
            raise ValueError("Capacity must be non-negative")
        self.capacity = capacity
        self.data = OrderedDict()

    def get(self, key, default=None):
        if key in self.data:
            self.data.move_to_end(key)
            return self.data[key]
        return default

    def put(self, key, value):
        if self.capacity <= 0:
            return
        if key in self.data:
            self.data[key] = value
            self.data.move_to_end(key)
        else:
            if len(self.data) >= self.capacity:
                self.data.popitem(last=False)
            self.data[key] = value

    def __contains__(self, key):
        return key in self.data

    def __len__(self):
        return len(self.data)
```

Let's re-verify `put` with `capacity=0`.
If `capacity=0`, `self.capacity <= 0` is true, so it returns immediately. `self.data` remains empty. Correct.

If `capacity=1`:
`put("a", 1)`: `key` not in `self.data`. `len(self.data)` is 0. `0 >= 1` is false. `self.data["a"] = 1`. `self.data` is `{"a": 1}`.
`put("b", 2)`: `key` not in `self.data`. `len(self.data)` is 1. `1 >= 1` is true. `self.data.popitem(last=False)` removes `"a"`. `self.data["b"] = 2`. `self.data` is `{"b": 2}`.
`put("a", 3)`: `key` in `self.data` (if it was there). `self.data["
...[trace truncated]
```
## ASSISTANT -> edit_file
```json
{"old_text":"class LRUCache:\n    def __init__(self, capacity):\n        self.capacity = capacity\n        self.data = {}\n\n    def get(self, key, default=None):\n        return self.data.get(key, default)\n\n    def put(self, key, value):\n        if key not in self.data and len(self.data) \u003e= self.capacity:\n            oldest = next(iter(self.data))\n            del self.data[oldest]\n        self.data[key] = value\n\n    def __len__(self):\n        return len(self.data)\n","new_text":"from collections import OrderedDict\n\nclass LRUCache:\n    def __init__(self, capacity):\n        if capacity \u003c 0:\n            raise ValueError(\"Capacity must be non-negative\")\n        self.capacity = capacity\n        self.data = OrderedDict()\n\n    def get(self, key, default=None):\n        if key in self.data:\n            self.data.move_to_end(key)\n            return self.data[key]\n        return default\n\n    def put(self, key, value):\n        if self.capacity \u003c= 0:\n            return\n        if key in self.data:\n            self.data.move_to_end(key)\n        elif len(self.data) \u003e= self.capacity:\n            self.data.popitem(last=False)\n        self.data[key] = value\n\n    def __contains__(self, key):\n        return key in self.data\n\n    def __len__(self):\n        return len(self.data)\n","path":"cache.py"}
```
## TOOL
```
Edited cache.py. The changed region now reads:
    1  from collections import OrderedDict
    2  
    3  class LRUCache:
    4      def __init__(self, capacity):
    5          if capacity < 0:
    6              raise ValueError("Capacity must be non-negative")
    7          self.capacity = capacity
    8          self.data = OrderedDict()
    9  
   10      def get(self, key, default=None):
   11          if key in self.data:
   12              self.data.move_to_end(key)
   13              return self.data[key]
   14          return default
   15  
   16      def put(self, key, value):
   17          if self.capacity <= 0:
   18              return
   19          if key in self.data:
   20              self.data.move_to_end(key)
   21          elif len(self.data) >= self.capacity:
   22              self.data.popitem(last=False)
   23          self.data[key] = value
   24  
   25      def __contains__(self, key):
   26          return key in self.data
   27  
   28      def __len__(self):
   29          return len(self.data)
```
## ASSISTANT
```
<thought>Now that I've applied the changes, I need to run the tests again to verify everything is working as expected.</thought>
```
## ASSISTANT -> run_tests
```json
{"path":"test_issue_checks.py"}
```
## TOOL
```
TESTS FAILING (1 failed, 5 passed in 0.07s)
..F...                                                                   [100%]
================================== FAILURES ===================================
_______________________ test_contains_does_not_refresh ________________________
test_issue_checks.py:29: in test_contains_does_not_refresh
    assert c.get("a") == 1
E   AssertionError: assert None == 1
E    +  where None = get('a')
E    +    where get = <cache.LRUCache object at 0x000002AC7A52D310>.get
1 failed, 5 passed in 0.07s
```
## ASSISTANT
```
<thought>The test `test_contains_does_not_refresh` failed.

```python
def test_contains_does_not_refresh():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    assert "a" in c
    c.put("c", 3)
    assert c.get("a") == 1
    assert c.get("b") is None
```

Wait, if `c.put("c", 3)` is called, and `capacity` is 2, then `"a"` or `"b"` should be evicted.
In `test_contains_does_not_refresh`:
1. `c = LRUCache(2)`
2. `c.put("a", 1)` -> `self.data = {"a": 1}`
3. `c.put("b", 2)` -> `self.data = {"a": 1, "b": 2}`
4. `assert "a" in c` -> calls `__contains__("a")`. `self.data` is still `{"a": 1, "b": 2}`.
5. `c.put("c", 3)`:
   - `key` ("c") not in `self.data`.
   - `len(self.data)` is 2. `self.capacity` is 2. `2 >= 2` is true.
   - `self.data.popitem(last=False)` removes `"a"`.
   - `self.data["c"] = 3`.
   - `self.data` is now `{"b": 2, "c": 3}`.
6. `assert c.get("a") == 1` -> `c.get("a")` returns `None` because `"a"` was evicted.

Wait, the test expects `c.get("a") == 1`. This means `"a"` should NOT have been evicted.
If `"a"` was not evicted, then `"b"` must have been evicted.
But `"a"` was inserted before `"b"`. So `"a"` is the oldest.

If `key in cache` does NOT count as a use, then `"a"` should still be the oldest.
If `"a"` is the oldest, it should be evicted when `"c"` is put.

Let's re-read the test.

```python
def test_contains_does_not_refresh():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    assert "a" in c
    c.put("c", 3)
    assert c.get("a") == 1
    assert c.get("b") is None
```

If `c.get("a") == 1` is true, it means `"a"` was NOT evicted.
If `"a"` was not evicted, then `"b"` must have been evicted.
If `"b"` was evicted, it means `"b"` was the oldest.
But `"a"` was inserted first.

Wait, if `key in cache` DOES count as a use, then `"a"` becomes the most recent.
Then `self.data` would be `{"b": 2, "a": 1}`.
Then `c.put("c", 3)` would evict `"b"`.
Then `c.get("a")` would be `1`.
And `c.get("b")` would be `None`.

So the test `test_contains_does_not_refresh` actually expects that `key in cache` DOES NOT refresh the key, but it seems I misunderstood the expected behavior of the test or the requirement.

Requirement: "`key in cache` must work, and must NOT count as a use."

If it must NOT count as a use, then `"a"` remains the oldest.
If `"a"` is the oldest, it should be evicted.

Let's look at the test again.

```python
def test_contains_does_not_refresh():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    assert "a" in c
    c.put("c", 3)
    assert c.get("a") == 1
    assert c.get("b") is None
```

If `key in cache` does NOT count as a use, then:
`put("a", 1)` -> `{"a": 1}`
`put("b", 2)` -> `{"a": 1, "b": 2}`
`"a" in c` -> `{"a": 1, "b": 2}` (no change)
`put("c", 3)` -> `{"b": 2, "c": 3}` (evicts "a")
`get("a")` -> `None`
`get("b")` -> `2`

The test says:
`assert c.get("a") == 1`
`assert c.get("b") is None`

This test seems to expect that `"b"` was evicted, which means `"b"` was the oldest.
But `"a"` was inserte
...[trace truncated]
```
## USER
```
Your last reply was cut off for being too long. Make smaller changes (use edit_file for small edits).
```
## ASSISTANT
```
<thought>The user is telling me that my last reply was cut off. I should make smaller changes.
I was trying to fix `test_issue_checks.py` by replacing the `test_contains_does_not_refresh` function.

The current `test_contains_does_not_refresh` in `test_issue_checks.py` is:
```python
def test_contains_does_not_refresh():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    assert "a" in c
    c.put("c", 3)
    assert c.get("a") == 1
    assert c.get("b") is None
```

It should be:
```python
def test_contains_does_not_refresh():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    assert "a" in c
    c.put("c", 3)
    assert c.get("a") is None
    assert c.get("b") == 2
```

I will use `edit_file` to replace this function.</thought>
```
## ASSISTANT -> edit_file
```json
{"old_text":"def test_contains_does_not_refresh():\n    c = LRUCache(2)\n    c.put(\"a\", 1)\n    c.put(\"b\", 2)\n    assert \"a\" in c\n    c.put(\"c\", 3)\n    assert c.get(\"a\") == 1\n    assert c.get(\"b\") is None","path":"test_issue_checks.py","new_text":"def test_contains_does_not_refresh():\n    c = LRUCache(2)\n    c.put(\"a\", 1)\n    c.put(\"b\", 2)\n    assert \"a\" in c\n    c.put(\"c\", 3)\n    assert c.get(\"a\") is None\n    assert c.get(\"b\") == 2"}
```
## TOOL
```
Edited test_issue_checks.py. The changed region now reads:
   21      assert c.get("c") == 4
   22  
   23  def test_contains_does_not_refresh():
   24      c = LRUCache(2)
   25      c.put("a", 1)
   26      c.put("b", 2)
   27      assert "a" in c
   28      c.put("c", 3)
   29      assert c.get("a") is None
   30      assert c.get("b") == 2
   31  
   32  def test_capacity_zero():
```
## ASSISTANT
```
<thought>The tests in `test_issue_checks.py` should now pass. I'll run them again.
I also want to run the original tests in `tests/test_cache.py` to make sure they pass too.
</thought>
```
## ASSISTANT -> run_tests
```json
{"path":"test_issue_checks.py"}
```
## TOOL
```
All tests passed (6 passed in 0.03s).
```
## ASSISTANT
```
<thought>The tests in `test_issue_checks.py` passed. Now I need to run the original tests in `tests/test_cache.py` to ensure they also pass.
</thought><thought>
</thought>
```
## ASSISTANT -> run_tests
```json
{"path":"tests/test_cache.py"}
```
## TOOL
```
All tests passed (2 passed in 0.02s).
```
## ASSISTANT
```
<thought>The user has provided the current status.
All requirements seem to be met and verified by the tests.

Checklist:
- [x] `get(key)` counts as a use and makes the key most recent. (Verified by `test_get_refreshes` in `test_issue_checks.py` and `tests/test_cache.py`)
- [x] `put(key, value)` on an existing key updates the value and makes it most recent. (Verified by `test_put_updates_existing_key_and_refreshes` in `test_issue_checks.py`)
- [x] `key in cache` must work, and must NOT count as a use. (Verified by `test_contains_does_not_refresh` in `test_issue_checks.py`)
- [x] `capacity=0` is allowed; the cache then stores nothing. (Verified by `test_capacity_zero` in `test_issue_checks.py`)
- [x] A negative capacity raises `ValueError`. (Verified by `test_negative_capacity` in `test_issue_checks.py`)

I've also verified `__len__` with `test_len` in `test_issue_checks.py`.

I'm confident with the solution.
</thought>
```
## ASSISTANT -> finish
```json
{"summary":"Implemented LRU eviction policy using collections.OrderedDict, added support for capacity=0, and ensured negative capacity raises ValueError."}
```
## TOOL
```
Accepted: all tests pass.
```
## GRADING
```
.......                                                                  [100%]
7 passed in 0.02s
```