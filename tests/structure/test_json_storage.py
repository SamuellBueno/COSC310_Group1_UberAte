import pytest

from app.core.errors import DataStoreError
from app.repositories import json_storage


def test_write_then_read_returns_same_records(isolated_data):
    records = [{"id": "X1", "name": "Test"}]
    json_storage.write_list("things.json", records)
    assert json_storage.read_list("things.json") == records


def test_reads_from_the_isolated_data_folder(isolated_data):
    (isolated_data / "only.json").write_text('[{"id": "T1"}]', encoding="utf-8")
    assert json_storage.read_list("only.json") == [{"id": "T1"}]


def test_missing_file_raises_data_store_error(isolated_data):
    # missing data files are reported as data store errors
    with pytest.raises(DataStoreError):
        json_storage.read_list("missing.json")


def test_invalid_json_raises_data_store_error(isolated_data):
    # invalid JSON is reported as a data store error
    (isolated_data / "invalid.json").write_text("not json", encoding="utf-8")
    with pytest.raises(DataStoreError):
        json_storage.read_list("invalid.json")


def test_object_json_raises_data_store_error(isolated_data):
    # data files must contain lists
    (isolated_data / "object.json").write_text('{"id": "X1"}', encoding="utf-8")
    with pytest.raises(DataStoreError):
        json_storage.read_list("object.json")


@pytest.mark.parametrize("ids, expected", [
    ([], "A1"),
    (["A1", "A2"], "A3"),
    (["A1", "A7", "A3"], "A8"),   # gaps are never filled
    (["A2", "M9"], "A3"),         # other prefixes are ignored
])
def test_next_id(ids, expected):
    assert json_storage.next_id([{"id": i} for i in ids], "A") == expected
