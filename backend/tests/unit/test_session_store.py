from app.schemas.common import ConversationTurn
from app.services.session_store import InMemorySessionStore


def test_session_store_keeps_histories_separate():
    store = InMemorySessionStore()
    turn = ConversationTurn(user_text="What is this?", assistant_text="A desk.")

    store.append_turn("session-1", turn)

    assert store.get_history("session-1") == [turn]
    assert store.get_history("session-2") == []

