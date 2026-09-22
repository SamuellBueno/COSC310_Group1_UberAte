from app.core.config import DATA_DIR_ENV_VAR, DEFAULT_DATA_DIR, get_data_dir


def test_get_data_dir_returns_default_when_env_var_not_set(monkeypatch):
    monkeypatch.delenv(DATA_DIR_ENV_VAR, raising=False)
    assert get_data_dir() == DEFAULT_DATA_DIR


def test_get_data_dir_returns_override_when_env_var_set(monkeypatch, tmp_path):
    monkeypatch.setenv(DATA_DIR_ENV_VAR, str(tmp_path))
    assert get_data_dir() == tmp_path