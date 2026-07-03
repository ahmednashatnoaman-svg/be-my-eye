from __future__ import annotations

import base64

from fastapi import APIRouter, HTTPException

from app.schemas.common import ErrorResponse
from app.schemas.currency import CurrencyLookupRequest, CurrencyLookupResponse
from app.services.currency_lookup_service import CurrencyLookupService


def create_currency_router(service: CurrencyLookupService) -> APIRouter:
    router = APIRouter()

    @router.post(
        "/currency-lookup",
        response_model=CurrencyLookupResponse,
        responses={400: {"model": ErrorResponse}},
    )
    def post_currency_lookup(payload: CurrencyLookupRequest) -> CurrencyLookupResponse:
        try:
            image_bytes = base64.b64decode(payload.image_base64, validate=True)
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(code="invalid_request", message="Invalid base64 payload for image_base64").model_dump(),
            ) from exc
        return service.handle(image_bytes)

    return router
