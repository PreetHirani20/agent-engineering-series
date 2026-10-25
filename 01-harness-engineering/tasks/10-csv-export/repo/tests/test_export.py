from export import to_csv


def test_plain_values():
    out = to_csv([{"id": 1, "name": "Ada"}], ["id", "name"])
    assert out.splitlines() == ["id,name", "1,Ada"]


def test_comma_is_quoted():
    out = to_csv([{"city": "Paris, France"}], ["city"])
    assert out.splitlines()[1] == '"Paris, France"'
