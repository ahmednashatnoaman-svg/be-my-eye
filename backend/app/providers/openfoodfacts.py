from __future__ import annotations

from urllib.parse import quote

import httpx

from app.providers.base import ProductLookupProvider, ProductLookupUnavailableError
from app.schemas.product import ProductInfo

OPEN_FOOD_FACTS_URL = "https://world.openfoodfacts.org/api/v2/product/{barcode}.json"


class OpenFoodFactsProductLookupProvider(ProductLookupProvider):
    def __init__(self, client: httpx.Client | None = None, timeout: float = 5.0) -> None:
        self._client = client or httpx.Client(timeout=timeout)

    def lookup_by_barcode(self, barcode: str) -> ProductInfo | None:
        # ProductLookupRequest already restricts barcode to digits, but this
        # provider can be called directly (not only via the API layer), so
        # percent-encode here too rather than relying solely on the caller.
        try:
            response = self._client.get(OPEN_FOOD_FACTS_URL.format(barcode=quote(barcode, safe="")))
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return None
            raise ProductLookupUnavailableError(
                f"Open Food Facts returned {exc.response.status_code}"
            ) from exc
        except httpx.TransportError as exc:
            # Timeout, connection refused, DNS failure, etc. -- this is a
            # failure to reach Open Food Facts, not a genuine "no product
            # for this barcode" result, so it must not be silently treated
            # as not-found.
            raise ProductLookupUnavailableError(f"Could not reach Open Food Facts: {exc}") from exc
        except Exception as exc:  # noqa: BLE001 -- any other unexpected failure (e.g. malformed
            # JSON) is a service problem, not a genuine not-found result, and must not leak as an
            # unhandled 500 either.
            raise ProductLookupUnavailableError(f"Open Food Facts lookup failed: {exc}") from exc

        if data.get("status") != 1:
            return None

        product = data.get("product", {})
        return ProductInfo(
            name=product.get("product_name") or "Unknown product",
            brand=product.get("brands"),
            ingredients_text=product.get("ingredients_text"),
            allergens=[tag.removeprefix("en:") for tag in product.get("allergens_tags", [])],
        )
