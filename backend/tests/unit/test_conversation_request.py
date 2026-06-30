import pytest
from pydantic import ValidationError

from app.schemas.conversation import ConversationRequest


def test_conversation_request_validates_required_fields():
    request = ConversationRequest(
        session_id="session-1",
        image_base64="aW1hZ2U=",
        audio_base64="YXVkaW8=",
        debug=True,
    )

    assert request.session_id == "session-1"
    assert request.debug is True


def test_conversation_request_rejects_empty_session_id():
    with pytest.raises(ValidationError):
        ConversationRequest(session_id="", image_base64="aW1hZ2U=", audio_base64="YXVkaW8=")

