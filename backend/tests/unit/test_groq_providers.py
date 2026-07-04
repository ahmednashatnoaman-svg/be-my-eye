from io import BytesIO

from PIL import Image

from app.core.prompts import PromptConfig
from app.providers.groq import GroqASRProvider, GroqGroundingProvider, GroqLLMProvider, GroqOCRProvider, GroqTTSProvider, GroqVisionProvider
from app.schemas.common import ConversationTurn, VisionTask


class FakeChatCompletions:
    def __init__(self):
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        message_texts = []
        for message in kwargs["messages"]:
            content = message["content"]
            if isinstance(content, list):
                message_texts.append(" ".join(part.get("text", "") for part in content if isinstance(part, dict)))
            else:
                message_texts.append(content)
        prompt_text = " ".join(message_texts)

        class Choice:
            class Message:
                content = "assistant answer" if "respond" in prompt_text.lower() else "scene summary"

            message = Message()

        class Response:
            choices = [Choice()]

        return Response()


class FakeTranscriptions:
    def __init__(self):
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return "مرحبا"


class FakeSpeech:
    def __init__(self):
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)

        class Response:
            def read(self_inner):
                return b"wav-bytes"

        return Response()


class FakeGroqClient:
    def __init__(self):
        self.chat = type("Chat", (), {"completions": FakeChatCompletions()})()
        self.audio = type("Audio", (), {"transcriptions": FakeTranscriptions(), "speech": FakeSpeech()})()


PROMPTS = PromptConfig(
    vision_system="vision system",
    vision_instruction="vision instruction",
    ocr_system="ocr system",
    llm_system="llm system",
    llm_answer_style="respond briefly",
    grounding_system="grounding system",
    currency_instruction="currency instruction",
    color_instruction="color instruction",
    product_instruction="product instruction",
    food_instruction="food instruction",
    people_instruction="people instruction",
    environment_instruction="environment instruction",
    clothing_instruction="clothing instruction",
    label_instruction="label instruction",
)


def make_image_bytes() -> bytes:
    image = Image.new("RGB", (1, 1), color="white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_groq_vision_provider_builds_chat_request():
    client = FakeGroqClient()
    provider = GroqVisionProvider(model="qwen-model", prompts=PROMPTS, client=client)

    result = provider.analyze(make_image_bytes(), "What is in front of me?", [])

    assert result == "scene summary"
    assert client.chat.completions.calls[0]["model"] == "qwen-model"


def test_groq_ocr_provider_uses_shared_model():
    client = FakeGroqClient()
    provider = GroqOCRProvider(model="qwen-model", prompts=PROMPTS, client=client)

    result = provider.extract_text(make_image_bytes())

    assert result == "scene summary"
    assert client.chat.completions.calls[0]["model"] == "qwen-model"


def test_groq_grounding_provider_uses_shared_model():
    client = FakeGroqClient()
    provider = GroqGroundingProvider(model="qwen-model", prompts=PROMPTS, client=client)

    result = provider.locate_object(make_image_bytes(), "my keys", [])

    assert result == "scene summary"
    assert client.chat.completions.calls[0]["model"] == "qwen-model"


def test_groq_llm_provider_includes_history_and_context():
    client = FakeGroqClient()
    provider = GroqLLMProvider(model="llama-model", prompts=PROMPTS, client=client)
    history = [ConversationTurn(user_text="What is this?", assistant_text="A desk.")]

    result = provider.generate_response("Is it clean?", "a desk", "text", history)

    assert result == "assistant answer"
    messages = client.chat.completions.calls[0]["messages"]
    assert messages[0] == {"role": "system", "content": "llm system"}
    assert messages[1] == {"role": "user", "content": "What is this?"}
    assert messages[2] == {"role": "assistant", "content": "A desk."}
    assert messages[-1]["role"] == "user"
    assert "Is it clean?" in messages[-1]["content"]
    assert "a desk" in messages[-1]["content"]
    assert "text" in messages[-1]["content"]


def test_groq_asr_provider_submits_audio():
    client = FakeGroqClient()
    provider = GroqASRProvider(model="whisper-large-v3", client=client)

    assert provider.transcribe(b"audio-bytes") == "مرحبا"
    assert client.audio.transcriptions.calls[0]["model"] == "whisper-large-v3"


def test_groq_tts_provider_returns_bytes():
    client = FakeGroqClient()
    provider = GroqTTSProvider(model="canopylabs/orpheus-arabic-saudi", voice="abdullah", client=client)

    assert provider.synthesize_speech("hello") == b"wav-bytes"
    assert client.audio.speech.calls[0]["voice"] == "abdullah"


def test_groq_vision_provider_selects_currency_instruction():
    client = FakeGroqClient()
    provider = GroqVisionProvider(model="qwen-model", prompts=PROMPTS, client=client)

    provider.analyze(make_image_bytes(), "How much money is this?", [], task=VisionTask.currency)

    prompt = client.chat.completions.calls[0]["messages"][0]["content"]
    assert isinstance(prompt, list)
    prompt_text = " ".join(part.get("text", "") for part in prompt if isinstance(part, dict))
    assert "currency instruction" in prompt_text
    assert "vision instruction" not in prompt_text


def test_groq_vision_provider_defaults_to_scene_instruction():
    client = FakeGroqClient()
    provider = GroqVisionProvider(model="qwen-model", prompts=PROMPTS, client=client)

    provider.analyze(make_image_bytes(), "What is this?", [])

    prompt = client.chat.completions.calls[0]["messages"][0]["content"]
    prompt_text = " ".join(part.get("text", "") for part in prompt if isinstance(part, dict))
    assert "vision instruction" in prompt_text


def test_groq_vision_provider_selects_food_instruction():
    client = FakeGroqClient()
    provider = GroqVisionProvider(model="qwen-model", prompts=PROMPTS, client=client)

    provider.analyze(make_image_bytes(), "What am I eating?", [], task=VisionTask.food)

    prompt = client.chat.completions.calls[0]["messages"][0]["content"]
    prompt_text = " ".join(part.get("text", "") for part in prompt if isinstance(part, dict))
    assert "food instruction" in prompt_text
    assert "vision instruction" not in prompt_text
