from __future__ import annotations

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.conversation import create_conversation_router
from app.api.currency import create_currency_router
from app.api.product import create_product_router
from app.core.config import get_settings
from app.core.prompts import get_prompt_config
from app.providers.fakes import (
    FakeASRProvider,
    FakeGroundingProvider,
    FakeLLMProvider,
    FakeOCRProvider,
    FakeProductLookupProvider,
    FakeTTSProvider,
    FakeVisionProvider,
)
from app.providers.egyptian_tts import EgyptianTTSProvider
from app.providers.openfoodfacts import OpenFoodFactsProductLookupProvider
from app.providers.roboflow_currency import RoboflowCurrencyProvider
from app.providers.groq import (
    GroqASRProvider,
    GroqGroundingProvider,
    GroqLLMProvider,
    GroqOCRProvider,
    GroqVisionProvider,
)
from app.services.conversation_service import ConversationService
from app.services.currency_lookup_service import CurrencyLookupService
from app.services.intent_router import IntentRouter
from app.services.session_store import InMemorySessionStore


def _make_verify_api_key(expected_key: str):
    # Cost/abuse protection: the backend URL is public (linked from the
    # README) and every request triggers paid Groq/Roboflow API calls with
    # no other gate. When BE_MY_EYE_API_KEY is unset (local dev, CI), the
    # check is a no-op -- this is opt-in so it never breaks existing setups
    # that don't configure it.
    async def verify_api_key(x_api_key: str | None = Header(default=None)) -> None:
        if expected_key and x_api_key != expected_key:
            raise HTTPException(
                status_code=401,
                detail={"code": "unauthorized", "message": "Missing or invalid API key"},
            )

    return verify_api_key


def create_app() -> FastAPI:
    settings = get_settings()
    prompts = get_prompt_config()

    if settings.use_real_providers:
        if not settings.groq_multimodal_model:
            raise RuntimeError("GROQ_MULTIMODAL_MODEL is required when real providers are enabled.")
        currency_detector = (
            RoboflowCurrencyProvider(
                project=settings.roboflow_currency_project,
                version=settings.roboflow_currency_version,
                api_key=settings.roboflow_api_key,
            )
            if settings.roboflow_api_key
            else None
        )
        service = ConversationService(
            asr=GroqASRProvider(model=settings.groq_asr_model, language=settings.groq_asr_language),
            vision=GroqVisionProvider(model=settings.groq_multimodal_model, prompts=prompts),
            ocr=GroqOCRProvider(model=settings.groq_multimodal_model, prompts=prompts),
            llm=GroqLLMProvider(model=settings.groq_llm_model, prompts=prompts),
            tts=EgyptianTTSProvider(space_id=settings.egyptian_tts_space_id),
            grounding=GroqGroundingProvider(model=settings.groq_multimodal_model, prompts=prompts),
            session_store=InMemorySessionStore(),
            router=IntentRouter(),
            currency_detector=currency_detector,
        )
    else:
        service = ConversationService(
            asr=FakeASRProvider(),
            vision=FakeVisionProvider(),
            ocr=FakeOCRProvider(),
            llm=FakeLLMProvider(),
            tts=FakeTTSProvider(),
            grounding=FakeGroundingProvider(),
            session_store=InMemorySessionStore(),
            router=IntentRouter(),
        )

    product_lookup_provider = (
        OpenFoodFactsProductLookupProvider() if settings.use_real_providers else FakeProductLookupProvider()
    )

    if settings.use_real_providers:
        currency_lookup_service = CurrencyLookupService(
            vision=GroqVisionProvider(model=settings.groq_multimodal_model, prompts=prompts),
            tts=EgyptianTTSProvider(space_id=settings.egyptian_tts_space_id),
            currency_detector=currency_detector,
        )
    else:
        currency_lookup_service = CurrencyLookupService(
            vision=FakeVisionProvider(),
            tts=FakeTTSProvider(),
            currency_detector=None,
        )

    app = FastAPI(title=settings.app_name, debug=settings.debug)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    api_key_dependency = [Depends(_make_verify_api_key(settings.api_key))]
    app.include_router(create_conversation_router(service), dependencies=api_key_dependency)
    app.include_router(create_product_router(product_lookup_provider), dependencies=api_key_dependency)
    app.include_router(create_currency_router(currency_lookup_service), dependencies=api_key_dependency)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
