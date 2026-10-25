`merge(base, override)` in `config.py` is used to layer config files, but it is shallow and it modifies `base` in place, so the defaults get corrupted after the first merge.

Required behaviour:
- Nested dicts merge recursively: `merge({"db": {"host": "a", "port": 1}}, {"db": {"port": 2}})` -> `{"db": {"host": "a", "port": 2}}`.
- Lists are replaced, not concatenated.
- An override value of `None` removes that key from the result (at any depth).
- If one side is a dict and the other is not, the override wins.
- Neither input is modified, and the result shares no dicts or lists with the inputs (changing the result later must not change `base` or `override`).

`load_layers(*layers)` should keep working on top of `merge`.
