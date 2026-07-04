from __future__ import annotations

import base64

import httpx

from app.providers.base import CurrencyDetectionProvider
from app.schemas.currency import CurrencyDetectionResult

ROBOFLOW_DETECT_URL = "https://detect.roboflow.com/{project}/{version}"


class RoboflowCurrencyProvider(CurrencyDetectionProvider):
    """Calls Roboflow's hosted inference API for the Egyptian-currency
    detection model. NOTE: this integration is written against Roboflow's
    documented REST contract but was not live-verified end-to-end during
    design (unlike EgyptianTTSProvider) -- it requires a Roboflow account
    and API key this session does not have. The exact class-label strings
    the model returns are unknown until confirmed against a live project;
    detect_currency() passes the raw label through unmodified rather than
    assuming a specific format.
    """

    def __init__(
        self,
        project: str,
        version: str,
        api_key: str,
        client: httpx.Client | None = None,
        timeout: float = 10.0,
    ) -> None:
        self._project = project
        self._version = version
        self._api_key = api_key
        self._client = client or httpx.Client(timeout=timeout)

    def detect_currency(self, image_bytes: bytes) -> CurrencyDetectionResult | None:
        encoded_image = base64.b64encode(image_bytes).decode("ascii")
        url = ROBOFLOW_DETECT_URL.format(project=self._project, version=self._version)

        try:
            response = self._client.post(
                url,
                params={"api_key": self._api_key},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                content=encoded_image,
            )
            response.raise_for_status()
            data = response.json()
        except Exception:  # noqa: BLE001 -- any failure here means "fall back to the VLM"
            return None

        predictions = data.get("predictions", [])
        if not predictions:
            return None

        best = max(predictions, key=lambda prediction: prediction.get("confidence", 0.0))
        return CurrencyDetectionResult(
            denomination=str(best.get("class", "unknown")),
            confidence=float(best.get("confidence", 0.0)),
        )
