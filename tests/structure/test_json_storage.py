import pytest

from app.repositories import json_store


def test_write_then_read_returns_same_records(isolated_data):
    records = [{"id": "X1", "name": "Test"}]
    json_store.write_list("things.json", records)
    assert json_store.read_list("things.json") == records


def test_reads_from_the_isolated_data_folder(isolated_data):
    (isolated_data / "only.json").write_text('[{"id": "T1"}]', encoding="utf-8")
    assert json_store.read_list("only.json") == [{"id": "T1"}]


@pytest.mark.parametrize("ids, expected", [
    ([], "A1"),
    (["A1", "A2"], "A3"),
    (["A1", "A7", "A3"], "A8"),   # gaps are never filled
    (["A2", "M9"], "A3"),         # other prefixes are ignored
])
def test_next_id(ids, expected):
    assert json_store.next_id([{"id": i} for i in ids], "A") == expected