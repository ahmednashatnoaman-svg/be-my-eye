import base64

from app.providers.fakes import FakeASRProvider, FakeLLMProvider, FakeOCRProvider, FakeTTSProvider, FakeVisionProvider
from app.schemas.conversation import ConversationRequest
from app.services.conversation_service import ConversationService
from app.services.intent_router import IntentRouter
from app.services.session_store import InMemorySessionStore


def make_service() -> ConversationService:
    return ConversationService(
        asr=FakeASRProvider(),
        vision=FakeVisionProvider(),
        ocr=FakeOCRProvider(),
        llm=FakeLLMProvider(),
        tts=FakeTTSProvider(),
        session_store=InMemorySessionStore(),
        router=IntentRouter(),
    )


def test_conversation_service_returns_response_and_debug():
    service = make_service()
    request = ConversationRequest(
        session_id="session-1",
        image_base64=base64.b64encode(b"image-bytes").decode("ascii"),
        audio_base64=base64.b64encode(b"Read this page").decode("ascii"),
        debug=True,
    )

    response = service.handle(request)

    assert response.session_id == "session-1"
    assert response.text == "I can read the text: sample printed text."
    assert base64.b64decode(response.audio_base64).decode("utf-8") == "I can read the text: sample printed text."
    assert response.debug is not None
    assert response.debug.transcript == "Read this page"
    assert response.debug.selected_providers == ["vision", "ocr"]


def test_conversation_service_persists_history():
    service = make_service()
    request = ConversationRequest(
        session_id="session-1",
        image_base64=base64.b64encode(b"image-bytes").decode("ascii"),
        audio_base64=base64.b64encode(b"What is in front of me?").decode("ascii"),
    )

    service.handle(request)

    history = service.session_store.get_history("session-1")
    assert len(history) == 1
    assert history[0].user_text == "What is in front of me?"

