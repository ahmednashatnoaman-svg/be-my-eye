from __future__ import annotations

from fastapi import APIRouter

from app.providers.base import ProductLookupProvider, ProductLookupUnavailableError
from app.schemas.product import ProductLookupRequest, ProductLookupResponse


def create_product_router(provider: ProductLookupProvider) -> APIRouter:
    router = APIRouter()

    @router.post("/product-lookup", response_model=ProductLookupResponse)
    def post_product_lookup(payload: ProductLookupRequest) -> ProductLookupResponse:
        try:
            product = provider.lookup_by_barcode(payload.barcode)
        except ProductLookupUnavailableError:
            return ProductLookupResponse(found=False, product=None, service_error=True)
        return ProductLookupResponse(found=product is not None, product=product)

    return router
