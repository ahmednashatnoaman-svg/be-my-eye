from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.api.product import create_product_router
from app.providers.base import ProductLookupUnavailableError
from app.providers.fakes import FakeProductLookupProvider


class RaisingProductLookupProvider:
    def lookup_by_barcode(self, barcode: str):
        raise ProductLookupUnavailableError("Open Food Facts unreachable")


def make_client(provider=None) -> TestClient:
    app = FastAPI()
    app.include_router(create_product_router(provider or FakeProductLookupProvider()))
    return TestClient(app)


def test_product_lookup_returns_product_for_known_barcode():
    client = make_client()

    response = client.post("/product-lookup", json={"barcode": "1234567890123"})

    assert response.status_code == 200
    body = response.json()
    assert body["found"] is True
    assert body["product"]["name"] == "Sample Product"


def test_product_lookup_returns_not_found_for_unknown_barcode():
    client = make_client()

    response = client.post("/product-lookup", json={"barcode": "0000000000000"})

    assert response.status_code == 200
    body = response.json()
    assert body["found"] is False
    assert body["product"] is None


def test_product_lookup_sets_service_error_when_lookup_unavailable():
    client = make_client(RaisingProductLookupProvider())

    response = client.post("/product-lookup", json={"barcode": "1234567890123"})

    assert response.status_code == 200
    body = response.json()
    assert body["found"] is False
    assert body["service_error"] is True
