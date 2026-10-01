"""Configuration precedence and optional voice behavior."""

from unittest.mock import Mock

from gencook.backend.speech import SpeechService
from gencook.config import Settings


def test_dotenv_settings_and_environment_precedence(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for name in ["OPENAI_API_KEY", "OPENAI_MODEL", "GENCOOK_SPEECH_ENABLED"]:
        monkeypatch.delenv(name, raising=False)
    (tmp_path / ".env").write_text(
        "OPENAI_API_KEY=test-file-key\nOPENAI_MODEL=file-model\nGENCOOK_SPEECH_ENABLED=false\n"
    )
    monkeypatch.setenv("OPENAI_API_KEY", "test-env-key")
    settings = Settings.from_env()
    assert settings.api_key == "test-env-key"
    assert settings.model == "file-model"
    assert settings.speech_enabled is False
    assert settings.api_key not in repr(settings)


def test_default_settings(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for name in ["OPENAI_API_KEY", "OPENAI_MODEL", "GENCOOK_SPEECH_ENABLED"]:
        monkeypatch.delenv(name, raising=False)
    assert Settings.from_env() == Settings()


def test_voice_initializes_lazily_and_is_reused():
    engine = Mock()
    factory = Mock(return_value=engine)
    speech = SpeechService(engine_factory=factory)
    factory.assert_not_called()
    speech.speak("First")
    speech.speak("Second")
    factory.assert_called_once()
    engine.setProperty.assert_called_once_with("rate", 150)
    assert engine.runAndWait.call_count == 2
    speech.close()
    engine.stop.assert_called_once()


def test_unavailable_voice_disables_speech_without_raising():
    factory = Mock(side_effect=RuntimeError("No voices"))
    speech = SpeechService(engine_factory=factory)
    speech.speak("First")
    speech.speak("Second")
    assert not speech.enabled
    factory.assert_called_once()


def test_disabled_speech_never_initializes():
    factory = Mock()
    speech = SpeechService(enabled=False, engine_factory=factory)
    speech.speak("Silent")
    speech.close()
    factory.assert_not_called()
