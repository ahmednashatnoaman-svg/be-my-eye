from __future__ import annotations

from app.providers.base import TTSProvider, TTSUnavailableError


class EgyptianTTSProvider(TTSProvider):
    """Calls the free, public omarelshehy/NAMAA-Egyptian-Voice Gradio Space
    for Egyptian-Arabic speech synthesis. Its API was live-verified during
    design: /generate_tts_audio takes text_input plus five optional tuning
    parameters, and returns a filepath to a generated WAV file.
    """

    def __init__(self, space_id: str, client: object | None = None) -> None:
        self._space_id = space_id
        self._client = client

    def _ensure_client(self) -> object:
        if self._client is None:
            from gradio_client import Client

            self._client = Client(self._space_id)
        return self._client

    def synthesize_speech(self, text: str) -> bytes:
        try:
            client = self._ensure_client()
            result_path = client.predict(
                text_input=text,
                audio_prompt_path_input=None,
                exaggeration_input=0.5,
                temperature_input=0.8,
                seed_num_input=0,
                cfgw_input=0.5,
                api_name="/generate_tts_audio",
            )
            with open(result_path, "rb") as audio_file:
                return audio_file.read()
        except Exception as exc:  # noqa: BLE001 -- any failure here means "use the fallback"
            raise TTSUnavailableError(f"Egyptian TTS unavailable: {exc}") from exc
