import pytest
from pydantic import ValidationError

from app.schemas.product import ProductInfo, ProductLookupRequest, ProductLookupResponse


def test_product_lookup_request_accepts_valid_barcode():
    request = ProductLookupRequest(barcode="6224000123456")

    assert request.barcode == "6224000123456"


def test_product_lookup_request_rejects_non_numeric_barcode():
    with pytest.raises(ValidationError):
        ProductLookupRequest(barcode="../../etc/passwd")


def test_product_lookup_request_rejects_barcode_with_url_injection_characters():
    with pytest.raises(ValidationError):
        ProductLookupRequest(barcode="123?redirect=evil.com")


def test_product_lookup_request_rejects_too_short_barcode():
    with pytest.raises(ValidationError):
        ProductLookupRequest(barcode="123")


def test_product_lookup_request_rejects_too_long_barcode():
    with pytest.raises(ValidationError):
        ProductLookupRequest(barcode="1" * 15)


def test_product_lookup_response_allows_not_found():
    response = ProductLookupResponse(found=False, product=None)

    assert response.found is False
    assert response.product is None


def test_product_info_defaults_allergens_to_empty_list():
    info = ProductInfo(name="Sample")

    assert info.allergens == []
