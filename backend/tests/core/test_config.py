from app.core.config import Settings


def test_settings_env_override(monkeypatch):
    monkeypatch.setenv("APP_NAME", "Test API")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost:5432/db")

    s = Settings(_env_file=None)
    assert s.app_name == "Test API"
    assert s.database_url.startswith("postgresql+asyncpg://")