import pytest

from app.providers.base import ASRProvider, LLMProvider, OCRProvider, TTSProvider, VisionProvider


def test_provider_interfaces_are_abstract():
    with pytest.raises(TypeError):
        ASRProvider()
    with pytest.raises(TypeError):
        VisionProvider()
    with pytest.raises(TypeError):
        OCRProvider()
    with pytest.raises(TypeError):
        LLMProvider()
    with pytest.raises(TypeError):
        TTSProvider()

