from app.services.intent_router import IntentRouter


def test_intent_router_selects_vision_by_default():
    router = IntentRouter()

    assert router.select_providers("What is in front of me?") == ["vision"]


def test_intent_router_adds_ocr_for_text_requests():
    router = IntentRouter()

    assert router.select_providers("Please read this document") == ["vision", "ocr"]

