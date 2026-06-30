from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    app_name: str = "Be My Eye Backend"
    environment: str = "development"
    debug: bool = True
    use_real_providers: bool = False
    groq_api_key: str = ""
    groq_multimodal_model: str = ""
    groq_llm_model: str = "llama-3.3-70b-versatile"
    groq_asr_model: str = "whisper-large-v3"
    groq_tts_model: str = "canopylabs/orpheus-arabic-saudi"
    groq_tts_voice: str = "abdullah"
    groq_asr_language: str = "ar"


def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("BE_MY_EYE_APP_NAME", "Be My Eye Backend"),
        environment=os.getenv("BE_MY_EYE_ENV", "development"),
        debug=os.getenv("BE_MY_EYE_DEBUG", "true").lower() in {"1", "true", "yes", "on"},
        use_real_providers=os.getenv("BE_MY_EYE_USE_REAL_PROVIDERS", "false").lower() in {"1", "true", "yes", "on"},
        groq_api_key=os.getenv("GROQ_API_KEY", ""),
        groq_multimodal_model=os.getenv("BE_MY_EYE_GROQ_MULTIMODAL_MODEL", ""),
        groq_llm_model=os.getenv("BE_MY_EYE_GROQ_LLM_MODEL", "llama-3.3-70b-versatile"),
        groq_asr_model=os.getenv("BE_MY_EYE_GROQ_ASR_MODEL", "whisper-large-v3"),
        groq_tts_model=os.getenv("BE_MY_EYE_GROQ_TTS_MODEL", "canopylabs/orpheus-arabic-saudi"),
        groq_tts_voice=os.getenv("BE_MY_EYE_GROQ_TTS_VOICE", "abdullah"),
        groq_asr_language=os.getenv("BE_MY_EYE_GROQ_ASR_LANGUAGE", "ar"),
    )
