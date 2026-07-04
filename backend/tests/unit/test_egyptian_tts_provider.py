import pytest

from app.providers.base import TTSUnavailableError
from app.providers.egyptian_tts import EgyptianTTSProvider


class FakeGradioClient:
    def __init__(self, result_path: str | None = None, error: Exception | None = None):
        self._result_path = result_path
        self._error = error
        self.calls = []

    def predict(self, **kwargs):
        self.calls.append(kwargs)
        if self._error is not None:
            raise self._error
        return self._result_path


def test_egyptian_tts_returns_audio_bytes_on_success(tmp_path):
    audio_file = tmp_path / "output.wav"
    audio_file.write_bytes(b"fake-wav-bytes")
    client = FakeGradioClient(result_path=str(audio_file))
    provider = EgyptianTTSProvider(space_id="omarelshehy/NAMAA-Egyptian-Voice", client=client)

    result = provider.synthesize_speech("إزيك عامل ايه")

    assert result == b"fake-wav-bytes"
    assert client.calls[0]["text_input"] == "إزيك عامل ايه"
    assert client.calls[0]["api_name"] == "/generate_tts_audio"


def test_egyptian_tts_raises_unavailable_error_on_client_failure():
    client = FakeGradioClient(error=RuntimeError("space is sleeping"))
    provider = EgyptianTTSProvider(space_id="omarelshehy/NAMAA-Egyptian-Voice", client=client)

    with pytest.raises(TTSUnavailableError):
        provider.synthesize_speech("hello")
