"""Named harness configurations.

`naive` and `engineered` are the two harnesses compared in the blog post.
The ablations switch one part at a time to see which part carries the gap:
  naive+<part>          naive with only that part turned on
  engineered-no-<part>  engineered with only that part turned off
"""

from dataclasses import replace

from .agent import PARTS, HarnessConfig

NAIVE = HarnessConfig("naive")
ENGINEERED = HarnessConfig("engineered", **{p: True for p in PARTS})

CONFIGS: dict[str, HarnessConfig] = {"naive": NAIVE, "engineered": ENGINEERED}
for _p in PARTS:
    CONFIGS[f"naive+{_p}"] = replace(NAIVE, name=f"naive+{_p}", **{_p: True})
    CONFIGS[f"engineered-no-{_p}"] = replace(ENGINEERED, name=f"engineered-no-{_p}", **{_p: False})

ADD_ONE = [f"naive+{p}" for p in PARTS]
REMOVE_ONE = [f"engineered-no-{p}" for p in PARTS]
