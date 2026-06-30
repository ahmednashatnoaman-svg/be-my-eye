from app.core.config import get_settings


def test_get_settings_uses_environment_defaults(monkeypatch):
    monkeypatch.delenv("BE_MY_EYE_APP_NAME", raising=False)
    monkeypatch.delenv("BE_MY_EYE_ENV", raising=False)
    monkeypatch.delenv("BE_MY_EYE_DEBUG", raising=False)

    settings = get_settings()

    assert settings.app_name == "Be My Eye Backend"
    assert settings.environment == "development"
    assert settings.debug is True


def test_get_settings_reads_environment(monkeypatch):
    monkeypatch.setenv("BE_MY_EYE_APP_NAME", "Custom App")
    monkeypatch.setenv("BE_MY_EYE_ENV", "test")
    monkeypatch.setenv("BE_MY_EYE_DEBUG", "false")

    settings = get_settings()

    assert settings.app_name == "Custom App"
    assert settings.environment == "test"
    assert settings.debug is False

