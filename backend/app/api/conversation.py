from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.common import ErrorResponse, ConversationResponse
from app.schemas.conversation import ConversationRequest
from app.services.conversation_service import ConversationError, ConversationService


def create_conversation_router(service: ConversationService) -> APIRouter:
    router = APIRouter()

    @router.post(
        "/conversation",
        response_model=ConversationResponse,
        responses={
            400: {"model": ErrorResponse},
        },
    )
    def post_conversation(payload: ConversationRequest) -> ConversationResponse:
        try:
            return service.handle(payload)
        except ConversationError as exc:
            raise HTTPException(status_code=400, detail=ErrorResponse(code="invalid_request", message=str(exc)).model_dump()) from exc

    return router
