import pytest

from app.providers.base import (
    ASRProvider,
    CurrencyDetectionProvider,
    LLMProvider,
    OCRProvider,
    ProductLookupProvider,
    TTSProvider,
    VisionProvider,
)


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
    with pytest.raises(TypeError):
        ProductLookupProvider()
    with pytest.raises(TypeError):
        CurrencyDetectionProvider()


def test_product_lookup_provider_concrete_subclass_satisfies_interface():
    from app.schemas.product import ProductInfo

    class ConcreteProductLookup(ProductLookupProvider):
        def lookup_by_barcode(self, barcode: str) -> ProductInfo | None:
            return ProductInfo(name="test product")

    provider = ConcreteProductLookup()
    result = provider.lookup_by_barcode("123")
    assert result.name == "test product"


def test_tts_unavailable_error_is_an_exception():
    from app.providers.base import TTSUnavailableError

    error = TTSUnavailableError("synthesis failed")
    assert isinstance(error, Exception)
    assert str(error) == "synthesis failed"


def test_currency_detection_provider_concrete_subclass_satisfies_interface():
    from app.schemas.currency import CurrencyDetectionResult

    class ConcreteCurrencyDetector(CurrencyDetectionProvider):
        def detect_currency(self, image_bytes: bytes) -> CurrencyDetectionResult | None:
            return CurrencyDetectionResult(denomination="20 EGP", confidence=0.9)

    provider = ConcreteCurrencyDetector()
    result = provider.detect_currency(b"fake-image-bytes")
    assert result.denomination == "20 EGP"
    assert result.confidence == 0.9

