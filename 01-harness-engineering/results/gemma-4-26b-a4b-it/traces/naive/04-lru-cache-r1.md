# 04-lru-cache / naive / run 1
solved=True end=finished steps=11 tokens=53770+8570

## SYSTEM
```
You are a helpful coding assistant with tools for working with a code repository. Solve the user's issue.
```
## USER
```
`LRUCache` in `cache.py` is supposed to evict the least recently *used* key, but it evicts the oldest *inserted* key.

Expected behaviour:
- `get(key)` counts as a use and makes the key most recent.
- `put(key, value)` on an existing key updates the value and makes it most recent.
- `key in cache` must work, and must NOT count as a use.
- `capacity=0` is allowed; the cache then stores nothing.
- A negative capacity raises `ValueError`.
```
## ASSISTANT
```
<thought>Okay, I understand the issue. The `LRUCache` implementation in `cache.py` is currently behaving like a FIFO (First-In-First-Out) cache instead of an LRU (Least Recently Used) cache. I need to fix it so that `get` and `put` (on existing keys) update the key's position to be the most recent. Also, I need to ensure that `key in cache` does not count as a use, and handle `capacity=0` and negative capacity correctly.

First, I'll explore the repository to find `cache.py`.</thought>
```
## ASSISTANT -> list_files
```json
{}
```
## TOOL
```
cache.py
tests/test_cache.py
```
## ASSISTANT
```
<thought>Okay, I see `cache.py` and `tests/test_cache.py`. I'll start by reading `cache.py` to understand the current implementation.</thought>
```
## ASSISTANT -> read_file
```json
{"path":"cache.py"}
```
## TOOL
```
class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.data = {}

    def get(self, key, default=None):
        return self.data.get(key, default)

    def put(self, key, value):
        if key not in self.data and len(self.data) >= self.capacity:
            oldest = next(iter(self.data))
            del self.data[oldest]
        self.data[key] = value

    def __len__(self):
        return len(self.data)

```
## ASSISTANT
```
<thought>The current implementation uses a regular dictionary. In Python 3.7+, dictionaries maintain insertion order. The `put` method evicts the first key in the dictionary, which is the oldest inserted key. This is indeed FIFO.

To implement LRU, I need to move the key to the end of the dictionary whenever it is accessed via `get` or updated via `put`.

Wait, I should also check the requirements again.
- `get(key)` counts as a use and makes the key most recent.
- `put(key, value)` on an existing key updates the value and makes it most recent.
- `key in cache` must work, and must NOT count as a use.
- `capacity=0` is allowed; the cache then stores nothing.
- A negative capacity raises `ValueError`.

Let's see if `__contains__` is implemented. It's not explicitly, but `key in cache` will use `__contains__` if it exists, otherwise it might fall back to something else or fail if not implemented. Actually, for a dict-like object, if `__contains__` is not implemented, it might not work as expected if it's not a subclass of `dict`. Here it's just a class.

Let's look at the tests to see what's currently there and what's expected.<thought>I'll read `tests/test_cache.py` to see the existing tests and how they are structured.</thought>
```
## ASSISTANT -> read_file
```json
{"path":"tests/test_cache.py"}
```
## TOOL
```
from cache import LRUCache


def test_evicts_when_full():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    c.put("c", 3)
    assert len(c) == 2
    assert c.get("c") == 3


def test_get_refreshes():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    c.get("a")
    c.put("c", 3)
    assert c.get("a") == 1
    assert c.get("b") is None

```
## ASSISTANT
```
<thought>The tests confirm the issue. `test_get_refreshes` expects `get("a")` to refresh "a", so that "b" is evicted when "c" is put.

Let's run the tests to confirm they fail.
```
## ASSISTANT -> run_tests
```json
{}
```
## TOOL
```
============================= test session starts =============================
platform win32 -- Python 3.13.1, pytest-9.1.1, pluggy-1.7.0 -- <home>\01-harness-engineering\.venv\Scripts\python.exe
rootdir: <home>\Temp\harness-engineering-work\gemma-4-26b-a4b-it\naive\04-lru-cache-r1
plugins: anyio-4.15.1
collecting ... collected 2 items

tests/test_cache.py::test_evicts_when_full PASSED                        [ 50%]
tests/test_cache.py::test_get_refreshes FAILED                           [100%]

================================== FAILURES ===================================
_____________________________ test_get_refreshes ______________________________

    def test_get_refreshes():
        c = LRUCache(2)
        c.put("a", 1)
        c.put("b", 2)
        c.get("a")
        c.put("c", 3)
>       assert c.get("a") == 1
E       AssertionError: assert None == 1
E        +  where None = get('a')
E        +    where get = <cache.LRUCache object at 0x0000020535322FD0>.get

tests\test_cache.py:19: AssertionError
========================= 1 failed, 1 passed in 0.15s =========================
```
## ASSISTANT
```
<thought>The tests failed as expected. `test_get_refreshes` failed because `c.get("a")` returned `None` instead of `1`. This is because "a" was evicted instead of "b".

Now I will implement the fixes.

Plan:
1.  Update `__init__` to handle negative capacity by raising `ValueError`.
2.  Update `get` to move the accessed key to the end of `self.data` (making it most recent).
3.  Update `put` to:
    -   Handle `capacity=0` case.
    -   If key exists, update value and move to end.
    -   If key doesn't exist, check capacity. If full, evict the oldest (first) key. Then add the new key.
4.  Implement `__contains__` to support `key in cache` without affecting LRU order.

Wait, if I use `collections.OrderedDict`, it might be easier. `OrderedDict` has `move_to_end`.

Let's see how I can implement it with a regular dict (since Python 3.7+ dicts are ordered).
To move a key to the end in a regular dict: `del self.data[key]; self.data[key] = value`.

Let's refine the plan.

`__init__(self, capacity)`:
```python
    def __init__(self, capacity):
        if capacity < 0:
            raise ValueError("capacity must be non-negative")
        self.capacity = capacity
        self.data = {}
```

`get(self, key, default=None)`:
```python
    def get(self, key, default=None):
        if key in self.data:
            value = self.data.pop(key)
            self.data[key] = value
            return value
        return default
```

`put(self, key, value)`:
```python
    def put(self, key, value):
        if self.capacity <= 0:
            return

        if key in self.data:
            del self.data[key]
        elif len(self.data) >= self.capacity:
            oldest = next(iter(self.data))
            del self.data[oldest]
        
        self.data[key] = value
```

`__contains__(self, key)`:
```python
    def __contains__(self, key):
        return key in self.data
```

`__len__(self)`:
```python
    def __len__(self):
        return len(self.data)
```

Wait, if `capacity=0`, `put` should do nothing. My implementation above handles it.

Let's double check `put` for existing key.
If `key` is in `self.data`, I delete it and then re-insert it. This moves it to the end.
If `key` is NOT in `self.data`, I check if I'm at capacity. If so, I delete the first key. Then I insert the new key.

Wait, if `capacity=0`, `len(self.data)` will always be `>= 0`.
If `capacity=0`, `len(self.data) >= 0` is true.
If `capacity=0`, `self.data` should always be empty.

If `capacity=0`:
`put("a", 1)`:
`if self.capacity <= 0: return` -> returns immediately. `self.data` remains `{}`. Correct.

If `capacity=1`:
`put("a", 1)`:
`key in self.data` is False.
`len(self.data)` is 0. `0 >= 1` is False.
`self.data["a"] = 1`. `self.data` is `{"a": 1}`.

`put("b", 2)`:
`key in self.data` is False.
`len(self.data)` is 1. `1 >= 1` is True.
`oldest = next(iter(self.data))` -> "a".
`del self.data["a"]`.
`self.data["b"] = 2`. `self.data` is `{"b": 2}`. Correct.

`put("a", 3)` (updating "a" if it was there
...[trace truncated]
```
## ASSISTANT -> write_file
```json
{"content":"from cache import LRUCache\nimport pytest\n\n\ndef test_evicts_when_full():\n    c = LRUCache(2)\n    c.put(\"a\", 1)\n    c.put(\"b\", 2)\n    c.put(\"c\", 3)\n    assert len(c) == 2\n    assert c.get(\"c\") == 3\n\n\ndef test_get_refreshes():\n    c = LRUCache(2)\n    c.put(\"a\", 1)\n    c.put(\"b\", 2)\n    c.get(\"a\")\n    c.put(\"c\", 3)\n    assert c.get(\"a\") == 1\n    assert c.get(\"b\") is None\n\n\ndef test_capacity_zero():\n    c = LRUCache(0)\n    c.put(\"a\", 1)\n    assert len(c) == 0\n    assert c.get(\"a\") is None\n\n\ndef test_negative_capacity():\n    with pytest.raises(ValueError):\n        LRUCache(-1)\n\n\ndef test_contains_does_not_refresh():\n    c = LRUCache(2)\n    c.put(\"a\", 1)\n    c.put(\"b\", 2)\n    assert \"a\" in c\n    c.put(\"c\", 3)\n    assert c.get(\"a\") == 1\n    assert c.get(\"b\") is None\n\n\ndef test_put_updates_existing_key():\n    c = LRUCache(2)\n    c.put(\"a\", 1)\n    c.put(\"b\", 2)\n    c.put(\"a\", 3)\n    c.put(\"c\", 4)\n    assert c.get(\"a\") == 3\n    assert c.get(\"b\") is None\n    assert c.get(\"c\") == 4\n","path":"tests/test_cache.py"}
```
## TOOL
```
OK
```
## ASSISTANT
```
<thought>Now I'll run the tests to see which ones fail. I expect most of them to fail because the current implementation is FIFO and doesn't handle the new requirements.</thought>
```
## ASSISTANT -> run_tests
```json
{}
```
## TOOL
```
============================= test session starts =============================
platform win32 -- Python 3.13.1, pytest-9.1.1, pluggy-1.7.0 -- <home>\01-harness-engineering\.venv\Scripts\python.exe
rootdir: <home>\Temp\harness-engineering-work\gemma-4-26b-a4b-it\naive\04-lru-cache-r1
plugins: anyio-4.15.1
collecting ... collected 6 items

tests/test_cache.py::test_evicts_when_full PASSED                        [ 16%]
tests/test_cache.py::test_get_refreshes FAILED                           [ 33%]
tests/test_cache.py::test_capacity_zero FAILED                           [ 50%]
tests/test_cache.py::test_negative_capacity FAILED                       [ 66%]
tests/test_cache.py::test_contains_does_not_refresh FAILED               [ 83%]
tests/test_cache.py::test_put_updates_existing_key FAILED                [100%]

================================== FAILURES ===================================
_____________________________ test_get_refreshes ______________________________

    def test_get_refreshes():
        c = LRUCache(2)
        c.put("a", 1)
        c.put("b", 2)
        c.get("a")
        c.put("c", 3)
>       assert c.get("a") == 1
E       AssertionError: assert None == 1
E        +  where None = get('a')
E        +    where get = <cache.LRUCache object at 0x0000021747A92FD0>.get

tests\test_cache.py:20: AssertionError
_____________________________ test_capacity_zero ______________________________

    def test_capacity_zero():
        c = LRUCache(0)
>       c.put("a", 1)

tests\test_cache.py:26: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <cache.LRUCache object at 0x0000021747A92E90>, key = 'a', value = 1

    def put(self, key, value):
        if key not in self.data and len(self.data) >= self.capacity:
>           oldest = next(iter(self.data))
                     ^^^^^^^^^^^^^^^^^^^^^
E           StopIteration

cache.py:11: StopIteration
___________________________ test_negative_capacity ____________________________

    def test_negative_capacity():
>       with pytest.raises(ValueError):
             ^^^^^^^^^^^^^^^^^^^^^^^^^
E       Failed: DID NOT RAISE ValueError

tests\test_cache.py:32: Failed
_______________________ test_contains_does_not_refresh ________________________

    def test_contains_does_not_refresh():
        c = LRUCache(2)
        c.put("a", 1)
        c.put("b", 2)
>       assert "a" in c
               ^^^^^^^^
E       TypeError: argument of type 'LRUCache' is not iterable

tests\test_cache.py:40: TypeError
________________________ test_put_updates_existing_key ________________________

    def test_put_updates_existing_key():
        c = LRUCache(2)
        c.put("a", 1)
        c.put("b", 2)
        c.put("a", 3)
        c.put("c", 4)
>       assert c.get("a") == 3
E       AssertionError: assert None == 3
E        +  where None = get('a')
E        +    where get = <cache.LRUCache object at
...[trace truncated]
```
## ASSISTANT
```
<thought
Okay, the failures confirm my analysis:
- `test_get_refreshes` failed because `get` doesn't refresh the key.
- `test_capacity_zero` failed with `StopIteration` because `next(iter(self.data))` was called on an empty dictionary when `capacity=0`.
- `test_negative_capacity` failed because `ValueError` was not raised.
- `test_contains_does_not_refresh` failed because `__contains__` is not implemented.
- `test_put_updates_existing_key` failed because `put` on an existing key doesn't refresh the key (it just updates the value, but since it's a regular dict, it stays in the same position, but wait, in Python 3.7+ dicts, updating an existing key doesn't change its position. So it's not "most recent"). Actually, in the current implementation:
```python
    def put(self, key, value):
        if key not in self.data and len(self.data) >= self.capacity:
            oldest = next(iter(self.data))
            del self.data[oldest]
        self.data[key] = value
```
If `key` is in `self.data`, it just does `self.data[key] = value`. The position doesn't change.

Now I will implement the fix in `cache.py`.

```python
class LRUCache:
    def __init__(self, capacity):
        if capacity < 0:
            raise ValueError("capacity must be non-negative")
        self.capacity = capacity
        self.data = {}

    def get(self, key, default=None):
        if key in self.data:
            value = self.data.pop(key)
            self.data[key] = value
            return value
        return default

    def put(self, key, value):
        if self.capacity <= 0:
            return

        if key in self.data:
            del self.data[key]
        elif len(self.data) >= self.capacity:
            oldest = next(iter(self.data))
            del self.data[oldest]
        
        self.data[key] = value

    def __contains__(self, key):
        return key in self.data

    def __len__(self):
        return len(self.data)
```

Wait, I should check if `self.data.pop(key)` is safe. Yes, because I check `if key in self.data`.

Let's apply this to `cache.py`.<thought>I'll update `cache.py` with the correct implementation of `LRUCache`. I'll include the `ValueError` for negative capacity, the `get` method that refreshes the key, the `put` method that handles capacity and refreshes the key, the `__contains__` method, and the `__len__` method. I'll also make sure `capacity=0` is handled correctly in `put`.</thought>
```
## ASSISTANT -> write_file
```json
{"content":"class LRUCache:\n    def __init__(self, capacity):\n        if capacity \u003c 0:\n            raise ValueError(\"capacity must be non-negative\")\n        self.capacity = capacity\n        self.data = {}\n\n    def get(self, key, default=None):\n        if key in self.data:\n            value = self.data.pop(key)\n            self.data[key] = value\n            return value\n        return default\n\n    def put(self, key, value):\n        if self.capacity \u003c= 0:\n            return\n\n        if key in self.data:\n            del self.data[key]\n        elif len(self.data) \u003e= self.capacity:\n            oldest = next(iter(self.data))\n            del self.data[oldest]\n        \n        self.data[key] = value\n\n    def __contains__(self, key):\n        return key in self.data\n\n    def __len__(self):\n        return len(self.data)\n","path":"cache.py"}
```
## TOOL
```
OK
```
## ASSISTANT
```
<thought>Now I'll run the tests again to verify the fix. All tests should pass now.</thought>
```
## ASSISTANT -> run_tests
```json
{}
```
## TOOL
```
============================= test session starts =============================
platform win32 -- Python 3.13.1, pytest-9.1.1, pluggy-1.7.0 -- <home>\01-harness-engineering\.venv\Scripts\python.exe
rootdir: <home>\Temp\harness-engineering-work\gemma-4-26b-a4b-it\naive\04-lru-cache-r1
plugins: anyio-4.15.1
collecting ... collected 6 items

tests/test_cache.py::test_evicts_when_full PASSED                        [ 16%]
tests/test_cache.py::test_get_refreshes PASSED                           [ 33%]
tests/test_cache.py::test_capacity_zero PASSED                           [ 50%]
tests/test_cache.py::test_negative_capacity PASSED                       [ 66%]
tests/test_cache.py::test_contains_does_not_refresh FAILED               [ 83%]
tests/test_cache.py::test_put_updates_existing_key PASSED                [100%]

================================== FAILURES ===================================
_______________________ test_contains_does_not_refresh ________________________

    def test_contains_does_not_refresh():
        c = LRUCache(2)
        c.put("a", 1)
        c.put("b", 2)
        assert "a" in c
        c.put("c", 3)
>       assert c.get("a") == 1
E       AssertionError: assert None == 1
E        +  where None = get('a')
E        +    where get = <cache.LRUCache object at 0x000002418EE35350>.get

tests\test_cache.py:42: AssertionError
========================= 1 failed, 5 passed in 0.12s =========================
```
## ASSISTANT
```
<thought>Wait, `test_contains_does_not_refresh` failed.

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

If `c.put("c", 3)` is called, and `capacity=2`, it should evict the oldest.
In `test_contains_does_not_refresh`:
1. `c.put("a", 1)` -> `{"a": 1}`
2. `c.put("b", 2)` -> `{"a": 1, "b": 2}`
3. `"a" in c` -> True. This should NOT refresh "a".
4. `c.put("c", 3)` -> `len(self.data)` is 2, `capacity` is 2. `key` "c" is not in `self.data`.
   `oldest = next(iter(self.data))` -> "a".
   `del self.data["a"]`.
   `self.data["c"] = 3`.
   `self.data` is `{"b": 2, "c": 3}`.
5. `c.get("a")` should be `None`.

Wait, the test expects `c.get("a") == 1`.

```python
    assert c.get("a") == 1
    assert c.get("b") is None
```

If `a` was NOT refreshed by `in`, then `a` is the oldest, so it should be evicted when `c` is put.
If `a` WAS refreshed by `in`, then `b` is the oldest, so `b` should be evicted.

The test says:
```python
    assert "a" in c
    c.put("c", 3)
    assert c.get("a") == 1
    assert c.get("b") is None
```
This test expects `a` to NOT be evicted, meaning `a` must have been refreshed. But the test name is `test_contains_does_not_refresh`.

If `contains` does NOT refresh, then `a` is the oldest.
When `c.put("c", 3)` is called, `a` is evicted.
So `c.get("a")` should be `None`.

The test assertion `assert c.get("a") == 1` is actually testing that `a` IS NOT evicted, which means it WAS refreshed.

Wait, let me re-read the test.

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

If `a` is NOT refreshed by `in`, then `a` is the oldest.
`c.put("c", 3)` will evict `a`.
Then `c.get("a")` will be `None`.
The test expects `c.get("a") == 1`.

So the test is actually asserting that `a` IS NOT evicted, which means it WAS refreshed. But the test name says `test_contains_does_not_refresh`.

If the requirement is "`key in cache` must work, and must NOT count as a use", then `a` should NOT be refreshed.
If `a` is not refreshed, then `a` is the oldest.
When `c` is put, `a` is evicted.
So `c.get("a")` should be `None`.

The test is wrong! It's asserting the opposite of what it says in its name and what the requirement says.

Let me check the requirement again.
- `key in cache` must work, and must NOT count as a use.

If it doesn't count as a use, it shouldn't be moved to the end.
If it's not moved to the end, it remains the oldest.
If it's the oldest, it gets evicted.

So `test_contains_does_not_refresh` should be:

```python
def test_contains_does_not_refresh():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    assert "a" in c
    c.put("c", 3)
    assert c.get("a") is None
    assert c.get("b") == 2
    assert c.get("c") == 3
```

Wait, let me re-r
...[trace truncated]
```
## ASSISTANT -> write_file
```json
{"path":"tests/test_cache.py","content":"from cache import LRUCache\nimport pytest\n\n\ndef test_evicts_when_full():\n    c = LRUCache(2)\n    c.put(\"a\", 1)\n    c.put(\"b\", 2)\n    c.put(\"c\", 3)\n    assert len(c) == 2\n    assert c.get(\"c\") == 3\n\n\ndef test_get_refreshes():\n    c = LRUCache(2)\n    c.put(\"a\", 1)\n    c.put(\"b\", 2)\n    c.get(\"a\")\n    c.put(\"c\", 3)\n    assert c.get(\"a\") == 1\n    assert c.get(\"b\") is None\n\n\ndef test_capacity_zero():\n    c = LRUCache(0)\n    c.put(\"a\", 1)\n    assert len(c) == 0\n    assert c.get(\"a\") is None\n\n\ndef test_negative_capacity():\n    with pytest.raises(ValueError):\n        LRUCache(-1)\n\n\ndef test_contains_does_not_refresh():\n    c = LRUCache(2)\n    c.put(\"a\", 1)\n    c.put(\"b\", 2)\n    assert \"a\" in c\n    c.put(\"c\", 3)\n    assert c.get(\"a\") is None\n    assert c.get(\"b\") == 2\n    assert c.get(\"c\") == 3\n\n\ndef test_put_updates_existing_key():\n    c = LRUCache(2)\n    c.put(\"a\", 1)\n    c.put(\"b\", 2)\n    c.put(\"a\", 3)\n    c.put(\"c\", 4)\n    assert c.get(\"a\") == 3\n    assert c.get(\"b\") is None\n    assert c.get(\"c\") == 4\n"}
```
## TOOL
```
OK
```
## ASSISTANT
```
<thought>Now I'll run the tests again. All tests should pass now.<thought>I'll run the tests one last time to ensure everything is working as expected. All tests should pass now.</thought>
```
## ASSISTANT -> run_tests
```json
{}
```
## TOOL
```
============================= test session starts =============================
platform win32 -- Python 3.13.1, pytest-9.1.1, pluggy-1.7.0 -- <home>\01-harness-engineering\.venv\Scripts\python.exe
rootdir: <home>\Temp\harness-engineering-work\gemma-4-26b-a4b-it\naive\04-lru-cache-r1
plugins: anyio-4.15.1
collecting ... collected 6 items

tests/test_cache.py::test_evicts_when_full PASSED                        [ 16%]
tests/test_cache.py::test_get_refreshes PASSED                           [ 33%]
tests/test_cache.py::test_capacity_zero PASSED                           [ 50%]
tests/test_cache.py::test_negative_capacity PASSED                       [ 66%]
tests/test_cache.py::test_contains_does_not_refresh PASSED               [ 83%]
tests/test_cache.py::test_put_updates_existing_key PASSED                [100%]

============================== 6 passed in 0.06s ==============================
```
## ASSISTANT
```
<thought>All tests passed. The implementation of `LRUCache` is now correct according to the requirements.

Summary of changes:
1.  Modified `LRUCache.__init__` to raise `ValueError` for negative capacity.
2.  Modified `LRUCache.get` to move the accessed key to the end of the dictionary (making it most recent).
3.  Modified `LRUCache.put` to:
    -   Handle `capacity=0` by doing nothing.
    -   If the key exists, delete it first to ensure it's moved to the end when re-inserted.
    -   If the key doesn't exist and the cache is at capacity, evict the oldest key (the first one in the dictionary).
4.  Implemented `LRUCache.__contains__` to support `key in cache` without affecting the LRU order.
5.  Updated `tests/test_cache.py` to include more comprehensive tests and fixed a faulty test case.

I'm done.</thought>The `LRUCache` implementation in `cache.py` was behaving as a FIFO cache instead of an LRU cache. I have updated it to correctly implement the LRU policy, where `get` and `put` (on existing keys) refresh the key's position to be the most recent. I also added support for `capacity=0`, ensured that `key in cache` does not refresh the key, and made sure that a negative capacity raises a `ValueError`.

### Changes made:

#### `cache.py`
-   **`__init__(self, capacity)`**: Added a check to raise `ValueError` if `capacity` is negative.
-   **`get(self, key, default=None)`**: Updated to move the accessed key to the end of the dictionary (making it the most recent) using `pop` and re-insertion.
-   **`put(self, key, value)`**:
    -   Added a check to return immediately if `capacity` is 0.
    -   If the key already exists, it is deleted before being re-inserted to ensure it becomes the most recent.
    -   If the key is new and the cache is at capacity, the oldest key (the first one in the dictionary) is evicted.
-   **`__contains__(self, key)`**: Implemented to allow `key in cache` checks without affecting the LRU order.

#### `tests/test_cache.py`
-   Added `test_capacity_zero` to verify that a cache with zero capacity stores nothing.
-   Added `test_negative_capacity` to verify that a negative capacity raises a `ValueError`.
-   Added `test_contains_does_not_refresh` to verify that checking for existence does not change the LRU order.
-   Added `test_put_updates_existing_key` to verify that updating an existing key makes it the most recent.
-   Fixed an error in the original `test_contains_does_not_refresh` which was asserting the wrong behavior.

All tests now pass.
```
## GRADING
```
.......                                                                  [100%]
7 passed in 0.02s
```