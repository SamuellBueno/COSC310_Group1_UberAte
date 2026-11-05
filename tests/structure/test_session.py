import json

from app.core.security import is_expired
from app.repositories import session_repository


def test_add_creates_a_session_that_can_be_found(isolated_data):
    # a saved sign in gets an id, and can be found again with it
    session = session_repository.add("U4")
    found = session_repository.get(session.session_id)
    assert found is not None
    assert found.user_id == "U4"


def test_session_ids_are_random_and_long(isolated_data):
    # two sign ins never get the same id, and it's long enough that nobody can guess it
    first = session_repository.add("U4")
    second = session_repository.add("U4")
    assert first.session_id != second.session_id
    assert len(first.session_id) >= 40


def test_new_session_is_not_expired(isolated_data):
    # a sign in made right now is good for the next 8 hours
    session = session_repository.add("U4")
    assert is_expired(session.expires_at) is False


def test_unknown_session_gives_none(isolated_data):
    # failure case: an id we never saved finds nothing
    assert session_repository.get("not a valid session id(unless randomization is insane)") is None


def test_delete_removes_only_that_session(isolated_data):
    # signing out on one browser doesn't sign out the others
    first = session_repository.add("U4")
    second = session_repository.add("U4")
    session_repository.delete(first.session_id)
    assert session_repository.get(first.session_id) is None
    assert session_repository.get(second.session_id) is not None


def test_old_session_is_found_but_expired(isolated_data):
    # get only finds, it doesn't judge, deciding an old session doesn't count is sign in's job
    old_session = [{"session_id": "old", "user_id": "U4", "expires_at": "2000-01-01T00:00:00+00:00"}]
    (isolated_data / "sessions.json").write_text(json.dumps(old_session), encoding="utf-8")
    session = session_repository.get("old")
    assert session is not None
    assert is_expired(session.expires_at) is True