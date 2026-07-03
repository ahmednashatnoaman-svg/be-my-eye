import pytest

from app.providers.base import ASRProvider, LLMProvider, OCRProvider, ProductLookupProvider, TTSProvider, VisionProvider


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


def test_product_lookup_provider_concrete_subclass_satisfies_interface():
    from app.schemas.product import ProductInfo

    class ConcreteProductLookup(ProductLookupProvider):
        def lookup_by_barcode(self, barcode: str) -> ProductInfo | None:
            return ProductInfo(name="test product")

    provider = ConcreteProductLookup()
    result = provider.lookup_by_barcode("123")
    assert result.name == "test product"

