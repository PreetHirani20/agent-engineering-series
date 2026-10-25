import json


def load_stats(path):
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return {k: int(v) for k, v in raw.items()}
