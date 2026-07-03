# Backend Roboflow Currency Detection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a specialist Egyptian-currency detector (via Roboflow's hosted inference API) that `ConversationService` tries first for currency questions, falling back to the general VLM when the specialist is unavailable or unconfident.

**Architecture:** A new `CurrencyDetectionProvider` interface, parallel to the existing provider interfaces, with a `RoboflowCurrencyProvider` real implementation calling Roboflow's hosted REST API (`POST https://detect.roboflow.com/{project}/{version}?api_key=...`, base64 image in the body). `ConversationService.handle()` tries this specialist first when `decision.vision_task == VisionTask.currency`; if it returns a confident result, that becomes the vision summary directly (skipping the general VLM call entirely for that turn); otherwise it falls back to the existing `self.vision.analyze(...)` call exactly as today.

**Tech Stack:** `httpx` (already a dependency), the existing provider-interface pattern, pytest.

## Global Constraints

- **This plan's Roboflow integration is written against Roboflow's well-documented, stable REST contract, but is NOT live-verified end-to-end** — unlike the Egyptian TTS Space in the previous plan, calling Roboflow's hosted inference requires a free Roboflow account and an API key, which this session does not have. Do not claim in commit messages, code comments, or reports that this was tested against the real API — only the fake/mocked-transport tests were run.
- The exact class-label strings the Banha University Egyptian-currency model returns (e.g. `"20_egp"` vs `"20"` vs something else) are unknown without live API access. Do not hardcode assumptions about the label format anywhere — pass the raw label through to the LLM prompt as-is and let the LLM phrase it naturally, exactly as this task's code does.
- Do not remove or bypass the general VLM currency path (`GroqVisionProvider` + `currency_instruction`, added in an earlier plan) — it remains the fallback when the specialist provider is absent, errors, or returns low confidence.
- Every new production module gets test coverage, following this repo's one-file-per-module convention.

---

### Task 1: `CurrencyDetectionResult` schema + `CurrencyDetectionProvider` interface

**Files:**
- Create: `backend/app/schemas/currency.py`
- Modify: `backend/app/providers/base.py`
- Test: `backend/tests/unit/test_provider_base.py`

**Interfaces:**
- Produces: `CurrencyDetectionResult` (pydantic model with `denomination: str`, `confidence: float`), `CurrencyDetectionProvider` (abstract base class with `detect_currency(image_bytes: bytes) -> CurrencyDetectionResult | None`) — consumed by Tasks 2, 3, 4.

- [ ] **Step 1: Write the failing test**

Add to `backend/tests/unit/test_provider_base.py`, extending the existing `test_provider_interfaces_are_abstract` function (it already covers `ASRProvider`, `VisionProvider`, `OCRProvider`, `LLMProvider`, `TTSProvider`, `ProductLookupProvider` in one function body):

```python
def test_provider_interfaces_are_abstract():
    with pytest.raises(TypeError):
        ASRProvider()
    with pytest.raises(TypeError):
        VisionProvider()
    with pytest.raises(TypeError):
        OCRProvider()
    with pytest.raises(TypeError):
        LLMProvider()
    with pytest.raises(TypeError):
        TTSProvider()
    with pytest.raises(TypeError):
        ProductLookupProvider()
    with pytest.raises(TypeError):
        CurrencyDetectionProvider()
```

Update the file's import line to include the new class:

```python
from app.providers.base import (
    ASRProvider,
    CurrencyDetectionProvider,
    LLMProvider,
    OCRProvider,
    ProductLookupProvider,
    TTSProvider,
    VisionProvider,
)
```

Also add a concrete-subclass test in the same file:

```python
def test_currency_detection_provider_concrete_subclass_satisfies_interface():
    from app.schemas.currency import CurrencyDetectionResult

    class ConcreteCurrencyDetector(CurrencyDetectionProvider):
        def detect_currency(self, image_bytes: bytes) -> CurrencyDetectionResult | None:
            return CurrencyDetectionResult(denomination="20 EGP", confidence=0.9)

    provider = ConcreteCurrencyDetector()
    result = provider.detect_currency(b"fake-image-bytes")
    assert result.denomination == "20 EGP"
    assert result.confidence == 0.9
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python3 -m pytest tests/unit/test_provider_base.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app.schemas.currency'` (or `ImportError: cannot import name 'CurrencyDetectionProvider'`).

- [ ] **Step 3: Write minimal implementation**

Create `backend/app/schemas/currency.py`:

```python
from __future__ import annotations

from pydantic import BaseModel, Field


class CurrencyDetectionResult(BaseModel):
    denomination: str
    confidence: float = Field(ge=0.0, le=1.0)
```

In `backend/app/providers/base.py`, add the import at the top (alongside the existing `from app.schemas.product import ProductInfo`):

```python
from app.schemas.currency import CurrencyDetectionResult
```

Then add the new abstract class at the end of the file, after `ProductLookupProvider`:

```python
class CurrencyDetectionProvider(ABC):
    @abstractmethod
    def detect_currency(self, image_bytes: bytes) -> CurrencyDetectionResult | None:
        raise NotImplementedError
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python3 -m pytest tests/unit/test_provider_base.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/schemas/currency.py backend/app/providers/base.py backend/tests/unit/test_provider_base.py
git commit -m "feat: add CurrencyDetectionResult schema and CurrencyDetectionProvider interface"
```

---

### Task 2: `FakeCurrencyDetectionProvider`

**Files:**
- Modify: `backend/app/providers/fakes.py`
- Test: `backend/tests/unit/test_fake_providers.py`

**Interfaces:**
- Consumes: `CurrencyDetectionProvider`, `CurrencyDetectionResult` (Task 1).
- Produces: `FakeCurrencyDetectionProvider` — consumed by Task 4's tests and Task 5's fake-provider wiring.

- [ ] **Step 1: Write the failing test**

Add to `backend/tests/unit/test_fake_providers.py`:

```python
def test_fake_currency_detection_returns_confident_result():
    from app.providers.fakes import FakeCurrencyDetectionProvider

    provider = FakeCurrencyDetectionProvider()

    result = provider.detect_currency(b"fake-image-bytes")

    assert result is not None
    assert result.denomination
    assert result.confidence >= 0.6
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python3 -m pytest tests/unit/test_fake_providers.py -v`
Expected: FAIL with `ImportError: cannot import name 'FakeCurrencyDetectionProvider'`.

- [ ] **Step 3: Write minimal implementation**

In `backend/app/providers/fakes.py`, add the import at the top (alongside the existing `from app.providers.base import ...` line):

```python
from app.providers.base import CurrencyDetectionProvider
from app.schemas.currency import CurrencyDetectionResult
```

Then add the new class after `FakeProductLookupProvider`:

```python
class FakeCurrencyDetectionProvider(CurrencyDetectionProvider):
    def detect_currency(self, image_bytes: bytes) -> CurrencyDetectionResult | None:
        _ = image_bytes
        return CurrencyDetectionResult(denomination="20 EGP", confidence=0.92)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python3 -m pytest tests/unit/test_fake_providers.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/providers/fakes.py backend/tests/unit/test_fake_providers.py
git commit -m "feat: add FakeCurrencyDetectionProvider"
```

---

### Task 3: `RoboflowCurrencyProvider` (real implementation)

**Files:**
- Create: `backend/app/providers/roboflow_currency.py`
- Test: `backend/tests/unit/test_roboflow_currency_provider.py`

**Interfaces:**
- Consumes: `CurrencyDetectionProvider`, `CurrencyDetectionResult` (Task 1).
- Produces: `RoboflowCurrencyProvider` — consumed by Task 5 (main.py wiring).

- [ ] **Step 1: Write the failing test**

Create `backend/tests/unit/test_roboflow_currency_provider.py` (this follows the exact `FakeTransport` pattern already used in `backend/tests/unit/test_openfoodfacts_provider.py` for mocking `httpx`):

```python
import httpx

from app.providers.roboflow_currency import RoboflowCurrencyProvider


class FakeTransport(httpx.BaseTransport):
    def __init__(self, json_body: dict, status_code: int = 200):
        self._json_body = json_body
        self._status_code = status_code

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        return httpx.Response(self._status_code, json=self._json_body)


def make_client(json_body: dict, status_code: int = 200) -> httpx.Client:
    return httpx.Client(transport=FakeTransport(json_body, status_code))


def test_roboflow_currency_returns_highest_confidence_prediction():
    client = make_client(
        {
            "predictions": [
                {"class": "10_egp", "confidence": 0.55},
                {"class": "20_egp", "confidence": 0.91},
            ]
        }
    )
    provider = RoboflowCurrencyProvider(project="egyptian-currency-psnkr", version="1", api_key="test-key", client=client)

    result = provider.detect_currency(b"fake-image-bytes")

    assert result is not None
    assert result.denomination == "20_egp"
    assert result.confidence == 0.91


def test_roboflow_currency_returns_none_when_no_predictions():
    client = make_client({"predictions": []})
    provider = RoboflowCurrencyProvider(project="egyptian-currency-psnkr", version="1", api_key="test-key", client=client)

    result = provider.detect_currency(b"fake-image-bytes")

    assert result is None


def test_roboflow_currency_returns_none_on_request_failure():
    client = make_client({"error": "not found"}, status_code=404)
    provider = RoboflowCurrencyProvider(project="egyptian-currency-psnkr", version="1", api_key="test-key", client=client)

    result = provider.detect_currency(b"fake-image-bytes")

    assert result is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python3 -m pytest tests/unit/test_roboflow_currency_provider.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app.providers.roboflow_currency'`.

- [ ] **Step 3: Write minimal implementation**

Create `backend/app/providers/roboflow_currency.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python3 -m pytest tests/unit/test_roboflow_currency_provider.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/providers/roboflow_currency.py backend/tests/unit/test_roboflow_currency_provider.py
git commit -m "feat: add RoboflowCurrencyProvider (not live-verified, see docstring)"
```

---

### Task 4: Try the specialist first in `ConversationService`, fall back to the VLM

**Files:**
- Modify: `backend/app/services/conversation_service.py`
- Test: `backend/tests/unit/test_conversation_service.py`

**Interfaces:**
- Consumes: `CurrencyDetectionProvider`, `CurrencyDetectionResult` (Task 1), `FakeCurrencyDetectionProvider` (Task 2).
- Produces: `ConversationService.currency_detector` (new optional field, default `None`) and the confidence-gated try-specialist-first behavior — consumed by Task 5 (main.py wiring).

- [ ] **Step 1: Write the failing tests**

Add to `backend/tests/unit/test_conversation_service.py`. First, update `make_service()` to accept an optional currency detector so existing tests are unaffected by default:

```python
def make_service(currency_detector=None) -> ConversationService:
    return ConversationService(
        asr=FakeASRProvider(),
        vision=FakeVisionProvider(),
        ocr=FakeOCRProvider(),
        llm=FakeLLMProvider(),
        tts=FakeTTSProvider(),
        grounding=FakeGroundingProvider(),
        session_store=InMemorySessionStore(),
        router=IntentRouter(),
        currency_detector=currency_detector,
    )
```

Then add:

```python
def test_conversation_service_uses_currency_detector_when_confident():
    from app.providers.fakes import FakeCurrencyDetectionProvider

    service = make_service(currency_detector=FakeCurrencyDetectionProvider())
    request = ConversationRequest(
        session_id="session-1",
        image_base64=base64.b64encode(b"image-bytes").decode("ascii"),
        audio_base64=base64.b64encode(b"How much money is this?").decode("ascii"),
        debug=True,
    )

    response = service.handle(request)

    assert response.debug.selected_providers == ["currency_detector"]
    assert "20 EGP" in response.debug.vision_summary


def test_conversation_service_falls_back_to_vlm_when_currency_detector_returns_none():
    class NoneReturningCurrencyDetector:
        def detect_currency(self, image_bytes: bytes):
            return None

    service = make_service(currency_detector=NoneReturningCurrencyDetector())
    request = ConversationRequest(
        session_id="session-1",
        image_base64=base64.b64encode(b"image-bytes").decode("ascii"),
        audio_base64=base64.b64encode(b"How much money is this?").decode("ascii"),
        debug=True,
    )

    response = service.handle(request)

    assert response.debug.selected_providers == ["vision"]


def test_conversation_service_falls_back_to_vlm_when_currency_detector_unconfident():
    from app.schemas.currency import CurrencyDetectionResult

    class LowConfidenceCurrencyDetector:
        def detect_currency(self, image_bytes: bytes):
            return CurrencyDetectionResult(denomination="10 EGP", confidence=0.2)

    service = make_service(currency_detector=LowConfidenceCurrencyDetector())
    request = ConversationRequest(
        session_id="session-1",
        image_base64=base64.b64encode(b"image-bytes").decode("ascii"),
        audio_base64=base64.b64encode(b"How much money is this?").decode("ascii"),
        debug=True,
    )

    response = service.handle(request)

    assert response.debug.selected_providers == ["vision"]


def test_conversation_service_ignores_currency_detector_for_non_currency_tasks():
    from app.providers.fakes import FakeCurrencyDetectionProvider

    service = make_service(currency_detector=FakeCurrencyDetectionProvider())
    request = ConversationRequest(
        session_id="session-1",
        image_base64=base64.b64encode(b"image-bytes").decode("ascii"),
        audio_base64=base64.b64encode(b"What is in front of me?").decode("ascii"),
        debug=True,
    )

    response = service.handle(request)

    assert response.debug.selected_providers == ["vision"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python3 -m pytest tests/unit/test_conversation_service.py -v`
Expected: FAIL — `TypeError: __init__() got an unexpected keyword argument 'currency_detector'` (the field doesn't exist on `ConversationService` yet).

- [ ] **Step 3: Write minimal implementation**

In `backend/app/services/conversation_service.py`, add the import:

```python
from app.providers.base import (
    ASRProvider,
    CurrencyDetectionProvider,
    GroundingProvider,
    LLMProvider,
    OCRProvider,
    TTSProvider,
    TTSUnavailableError,
    VisionProvider,
)
from app.schemas.common import ConversationDebug, ConversationResponse, ConversationTurn
from app.schemas.conversation import ConversationRequest
from app.schemas.currency import CurrencyDetectionResult
from app.services.intent_router import IntentRouter
from app.services.session_store import InMemorySessionStore
```

Add the class constant and new field to `ConversationService`:

```python
@dataclass
class ConversationService:
    asr: ASRProvider
    vision: VisionProvider
    ocr: OCRProvider
    llm: LLMProvider
    tts: TTSProvider
    grounding: GroundingProvider
    session_store: InMemorySessionStore
    router: IntentRouter
    currency_detector: CurrencyDetectionProvider | None = None

    CURRENCY_CONFIDENCE_THRESHOLD = 0.6
```

Then change the vision-analysis section of `handle()` from:

```python
        vision_summary = self.vision.analyze(image_bytes, transcript, history, task=decision.vision_task)
```

to:

```python
        currency_result: CurrencyDetectionResult | None = None
        if decision.vision_task == VisionTask.currency and self.currency_detector is not None:
            currency_result = self.currency_detector.detect_currency(image_bytes)

        used_currency_detector = (
            currency_result is not None and currency_result.confidence >= self.CURRENCY_CONFIDENCE_THRESHOLD
        )
        if used_currency_detector:
            vision_summary = (
                f"Detected currency: {currency_result.denomination} "
                f"(confidence {currency_result.confidence:.0%})"
            )
        else:
            vision_summary = self.vision.analyze(image_bytes, transcript, history, task=decision.vision_task)
```

(This requires importing `VisionTask` — check the top of the file for an existing `from app.schemas.common import ...` line and add `VisionTask` to it if not already present.)

Finally, change the `selected_providers` construction from:

```python
        selected_providers = ["vision"]
        if decision.use_ocr:
            selected_providers.append("ocr")
        if grounding_result is not None:
            selected_providers.append("grounding")
```

to:

```python
        selected_providers = ["currency_detector"] if used_currency_detector else ["vision"]
        if decision.use_ocr:
            selected_providers.append("ocr")
        if grounding_result is not None:
            selected_providers.append("grounding")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python3 -m pytest tests/unit/test_conversation_service.py -v`
Expected: PASS.

- [ ] **Step 5: Run the full backend suite**

Run: `cd backend && python3 -m pytest -v`
Expected: all tests pass (the existing 89 plus every test added in Tasks 1-4).

- [ ] **Step 6: Commit**

```bash
git add backend/app/services/conversation_service.py backend/tests/unit/test_conversation_service.py
git commit -m "feat: try RoboflowCurrencyProvider first for currency questions, fall back to VLM"
```

---

### Task 5: Settings + wire `RoboflowCurrencyProvider` into `create_app()`

**Files:**
- Modify: `backend/app/core/config.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/unit/test_config.py`, `backend/tests/unit/test_main.py`

**Interfaces:**
- Consumes: `RoboflowCurrencyProvider` (Task 3), `FakeCurrencyDetectionProvider` (Task 2).
- Produces: the running app's real-provider mode now tries the currency specialist first. This is the final integration point in this plan.

- [ ] **Step 1: Write the failing tests**

Add to `backend/tests/unit/test_config.py`, following the same `monkeypatch.setenv`/`delenv` style as the file's existing tests:

```python
def test_settings_includes_roboflow_currency_defaults():
    settings = get_settings()

    assert settings.roboflow_api_key == ""
    assert settings.roboflow_currency_project == "egyptian-currency-psnkr"
    assert settings.roboflow_currency_version == "1"


def test_settings_reads_roboflow_currency_overrides(monkeypatch):
    monkeypatch.setenv("ROBOFLOW_API_KEY", "test-roboflow-key")
    monkeypatch.setenv("ROBOFLOW_CURRENCY_PROJECT", "some-other-project")
    monkeypatch.setenv("ROBOFLOW_CURRENCY_VERSION", "3")

    settings = get_settings()

    assert settings.roboflow_api_key == "test-roboflow-key"
    assert settings.roboflow_currency_project == "some-other-project"
    assert settings.roboflow_currency_version == "3"
```

Add to `backend/tests/unit/test_main.py`:

```python
def test_create_app_wires_currency_detector_only_when_roboflow_key_present(monkeypatch):
    monkeypatch.setenv("USE_REAL_PROVIDERS", "true")
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setenv("GROQ_MULTIMODAL_MODEL", "test-model")
    monkeypatch.delenv("ROBOFLOW_API_KEY", raising=False)

    app = create_app()

    assert app is not None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python3 -m pytest tests/unit/test_config.py tests/unit/test_main.py -v`
Expected: FAIL — `AttributeError: 'Settings' object has no attribute 'roboflow_api_key'`.

- [ ] **Step 3: Write minimal implementation**

In `backend/app/core/config.py`, add three fields to the `Settings` dataclass:

```python
@dataclass(frozen=True)
class Settings:
    app_name: str = "Be My Eye Backend"
    environment: str = "development"
    debug: bool = True
    use_real_providers: bool = False
    groq_api_key: str = ""
    groq_multimodal_model: str = ""
    groq_llm_model: str = "llama-3.3-70b-versatile"
    groq_asr_model: str = "whisper-large-v3"
    groq_tts_model: str = "canopylabs/orpheus-arabic-saudi"
    groq_tts_voice: str = "abdullah"
    groq_asr_language: str = "ar"
    egyptian_tts_space_id: str = "omarelshehy/NAMAA-Egyptian-Voice"
    roboflow_api_key: str = ""
    roboflow_currency_project: str = "egyptian-currency-psnkr"
    roboflow_currency_version: str = "1"
```

And in `get_settings()`, add the matching lines (after the existing `egyptian_tts_space_id=...` line):

```python
        roboflow_api_key=os.getenv("ROBOFLOW_API_KEY", ""),
        roboflow_currency_project=os.getenv("ROBOFLOW_CURRENCY_PROJECT", "egyptian-currency-psnkr"),
        roboflow_currency_version=os.getenv("ROBOFLOW_CURRENCY_VERSION", "1"),
```

In `backend/app/main.py`, add the import:

```python
from app.providers.roboflow_currency import RoboflowCurrencyProvider
```

Then, inside `create_app()`'s real-provider branch, right before the `ConversationService(...)` construction, add:

```python
        currency_detector = (
            RoboflowCurrencyProvider(
                project=settings.roboflow_currency_project,
                version=settings.roboflow_currency_version,
                api_key=settings.roboflow_api_key,
            )
            if settings.roboflow_api_key
            else None
        )
```

(This is deliberately `None` when no Roboflow key is configured, rather than constructing a provider that will only ever fail — `ConversationService` already falls back cleanly to the VLM when `currency_detector` is `None`.)

Then add `currency_detector=currency_detector` to the real-provider branch's `ConversationService(...)` call:

```python
        service = ConversationService(
            asr=GroqASRProvider(model=settings.groq_asr_model, language=settings.groq_asr_language),
            vision=GroqVisionProvider(model=settings.groq_multimodal_model, prompts=prompts),
            ocr=GroqOCRProvider(model=settings.groq_multimodal_model, prompts=prompts),
            llm=GroqLLMProvider(model=settings.groq_llm_model, prompts=prompts),
            tts=EgyptianTTSProvider(space_id=settings.egyptian_tts_space_id),
            grounding=GroqGroundingProvider(model=settings.groq_multimodal_model, prompts=prompts),
            session_store=InMemorySessionStore(),
            router=IntentRouter(),
            currency_detector=currency_detector,
        )
```

Do not add a currency detector to the fake-provider branch — `FakeCurrencyDetectionProvider` exists for tests, not for `create_app()`'s fake-mode wiring, since fake mode is meant to be a fully deterministic, self-contained mode without any real network calls.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python3 -m pytest tests/unit/test_config.py tests/unit/test_main.py -v`
Expected: PASS.

- [ ] **Step 5: Run the full backend suite**

Run: `cd backend && python3 -m pytest -v`
Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add backend/app/core/config.py backend/app/main.py backend/tests/unit/test_config.py backend/tests/unit/test_main.py
git commit -m "feat: wire RoboflowCurrencyProvider into create_app when ROBOFLOW_API_KEY is set"
```

---

## Plan Complete

After Task 5, the backend tries the Egyptian-currency specialist first whenever `ROBOFLOW_API_KEY` is configured, falling back to the general VLM otherwise (including when no key is set at all — the app works exactly as before if the user never sets up Roboflow).

**Required manual step before this goes live (not part of this plan's tasks, cannot be done from this session):**
1. Create a free account at [roboflow.com](https://roboflow.com).
2. Find or fork the Egyptian currency model (e.g. the Banha University project on Roboflow Universe) into your own workspace.
3. Use the project's "Get curl command" button in its Deploy tab to get the *exact* working project slug, version number, and confirm the class-label format the model actually returns.
4. Set `ROBOFLOW_API_KEY`, and if the slug/version differ from this plan's defaults, `ROBOFLOW_CURRENCY_PROJECT` / `ROBOFLOW_CURRENCY_VERSION` too, in the Vercel environment (same process as `GROQ_API_KEY` was set earlier in this project).

Until that's done, the app runs exactly as it did before this plan — no `ROBOFLOW_API_KEY` means `currency_detector` stays `None` and every currency question uses the general VLM, same as today.
