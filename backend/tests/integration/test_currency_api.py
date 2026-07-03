import base64

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.currency import create_currency_router
from app.providers.fakes import FakeCurrencyDetectionProvider, FakeTTSProvider, FakeVisionProvider
from app.services.currency_lookup_service import CurrencyLookupService


def make_client() -> TestClient:
    service = CurrencyLookupService(
        vision=FakeVisionProvider(),
        tts=FakeTTSProvider(),
        currency_detector=FakeCurrencyDetectionProvider(),
    )
    app = FastAPI()
    app.include_router(create_currency_router(service))
    return TestClient(app)


def test_currency_lookup_endpoint_returns_detection():
    client = make_client()

    response = client.post(
        "/currency-lookup",
        json={"image_base64": base64.b64encode(b"fake-image-bytes").decode("ascii")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["found"] is True
    assert body["denomination"] == "20 EGP"


def test_currency_lookup_endpoint_rejects_invalid_base64():
    client = make_client()

    response = client.post("/currency-lookup", json={"image_base64": "not-valid-base64!!!"})

    assert response.status_code == 400
