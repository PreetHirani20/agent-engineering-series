from mdtable import to_markdown


def test_issue_example():
    rows = [{"name": "Ada", "score": 9.5}, {"name": "Grace Hopper", "score": 10, "note": "a|b"}]
    assert to_markdown(rows) == (
        "| name         | score | note |\n"
        "| ------------ | ----: | ---- |\n"
        "| Ada          |   9.5 |      |\n"
        "| Grace Hopper |    10 | a\\|b |"
    )
