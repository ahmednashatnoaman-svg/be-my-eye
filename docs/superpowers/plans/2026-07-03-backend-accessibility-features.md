# Backend Accessibility Features Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add five new backend `VisionTask` capabilities (food, people, environment, clothing, label) plus a barcode-to-product-info lookup endpoint, extending the existing MVP's provider-interface architecture.

**Architecture:** Follows the exact pattern used for currency/color/product in the prior MVP round: a new `VisionTask` enum value + a dedicated `PromptConfig` instruction field + a keyword-routing entry in `IntentRouter` (English and Arabic, since this app's ASR defaults to Arabic) + wiring into `GroqVisionProvider`'s instruction dispatch. Barcode lookup is a new, separate capability (not a `VisionTask`) since it queries an external product database (Open Food Facts) instead of the VLM, so it gets its own provider interface, schema, and endpoint.

**Tech Stack:** FastAPI, Pydantic v2, pytest, `httpx` (new dependency, for the Open Food Facts HTTP call).

## Global Constraints

- Every new food/allergen/dietary/medicine-related instruction must use hedged language ("appears to," "looks like," "may contain") — never a bare guarantee. This is a safety requirement from the design spec (`docs/superpowers/specs/2026-07-03-blind-accessibility-feature-expansion-design.md`), not a style preference.
- All new `IntentRouter` keyword sets must include both English and Arabic variants, matching the existing five keyword tuples — this app's ASR defaults to Arabic (`GROQ_ASR_LANGUAGE=ar`), and English-only keywords silently never match real transcripts (this exact bug was found and fixed earlier in this project).
- Barcode-to-**price** lookup is explicitly out of scope — no free, reliable data source exists. Do not add a price field.
- Every new production module gets its own test file or test additions in the matching existing test file, per this repo's established one-file-per-module convention.

---

### Task 1: Extend `VisionTask` with five new capabilities

**Files:**
- Modify: `backend/app/schemas/common.py:9-13`
- Test: `backend/tests/unit/test_common_schemas.py`

**Interfaces:**
- Produces: `VisionTask.food`, `VisionTask.people`, `VisionTask.environment`, `VisionTask.clothing`, `VisionTask.label` — five new enum members, used by Tasks 2-4.

- [ ] **Step 1: Write the failing test**

Open `backend/tests/unit/test_common_schemas.py` and add:

```python
def test_vision_task_includes_new_accessibility_capabilities():
    assert VisionTask.food.value == "food"
    assert VisionTask.people.value == "people"
    assert VisionTask.environment.value == "environment"
    assert VisionTask.clothing.value == "clothing"
    assert VisionTask.label.value == "label"
```

Make sure the file's existing imports include `VisionTask` from `app.schemas.common` (check the top of the file — if it's not imported, add `from app.schemas.common import VisionTask` alongside the existing imports).

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python3 -m pytest tests/unit/test_common_schemas.py::test_vision_task_includes_new_accessibility_capabilities -v`
Expected: FAIL with `AttributeError: food` (or similar — the enum member doesn't exist yet).

- [ ] **Step 3: Write minimal implementation**

In `backend/app/schemas/common.py`, change:

```python
class VisionTask(str, Enum):
    scene = "scene"
    currency = "currency"
    color = "color"
    product = "product"
```

to:

```python
class VisionTask(str, Enum):
    scene = "scene"
    currency = "currency"
    color = "color"
    product = "product"
    food = "food"
    people = "people"
    environment = "environment"
    clothing = "clothing"
    label = "label"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python3 -m pytest tests/unit/test_common_schemas.py -v`
Expected: PASS (all tests in the file, including the new one).

- [ ] **Step 5: Commit**

```bash
git add backend/app/schemas/common.py backend/tests/unit/test_common_schemas.py
git commit -m "feat: add food/people/environment/clothing/label VisionTask values"
```

---

### Task 2: Add prompt instructions for the five new tasks

**Files:**
- Modify: `backend/app/core/prompts.py`
- Test: `backend/tests/unit/test_prompts.py`

**Interfaces:**
- Consumes: nothing new.
- Produces: `PromptConfig.food_instruction`, `.people_instruction`, `.environment_instruction`, `.clothing_instruction`, `.label_instruction` — five new fields, consumed by Task 3.

- [ ] **Step 1: Write the failing test**

Add to `backend/tests/unit/test_prompts.py`:

```python
def test_prompt_config_includes_new_accessibility_task_instructions(monkeypatch):
    monkeypatch.delenv("BE_MY_EYE_FOOD_INSTRUCTION_PROMPT", raising=False)
    monkeypatch.delenv("BE_MY_EYE_PEOPLE_INSTRUCTION_PROMPT", raising=False)
    monkeypatch.delenv("BE_MY_EYE_ENVIRONMENT_INSTRUCTION_PROMPT", raising=False)
    monkeypatch.delenv("BE_MY_EYE_CLOTHING_INSTRUCTION_PROMPT", raising=False)
    monkeypatch.delenv("BE_MY_EYE_LABEL_INSTRUCTION_PROMPT", raising=False)

    prompts = get_prompt_config()

    assert "dish" in prompts.food_instruction.lower()
    assert "allerg" in prompts.food_instruction.lower()
    assert "identify" not in prompts.people_instruction.lower()
    assert "light" in prompts.environment_instruction.lower()
    assert "match" in prompts.clothing_instruction.lower() or "stain" in prompts.clothing_instruction.lower()
    assert "expir" in prompts.label_instruction.lower() or "medicine" in prompts.label_instruction.lower()


def test_prompt_config_reads_new_accessibility_task_overrides(monkeypatch):
    monkeypatch.setenv("BE_MY_EYE_FOOD_INSTRUCTION_PROMPT", "food override")
    monkeypatch.setenv("BE_MY_EYE_PEOPLE_INSTRUCTION_PROMPT", "people override")
    monkeypatch.setenv("BE_MY_EYE_ENVIRONMENT_INSTRUCTION_PROMPT", "environment override")
    monkeypatch.setenv("BE_MY_EYE_CLOTHING_INSTRUCTION_PROMPT", "clothing override")
    monkeypatch.setenv("BE_MY_EYE_LABEL_INSTRUCTION_PROMPT", "label override")

    prompts = get_prompt_config()

    assert prompts.food_instruction == "food override"
    assert prompts.people_instruction == "people override"
    assert prompts.environment_instruction == "environment override"
    assert prompts.clothing_instruction == "clothing override"
    assert prompts.label_instruction == "label override"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python3 -m pytest tests/unit/test_prompts.py -v`
Expected: FAIL with `AttributeError: 'PromptConfig' object has no attribute 'food_instruction'`.

- [ ] **Step 3: Write minimal implementation**

In `backend/app/core/prompts.py`, change the dataclass:

```python
@dataclass(frozen=True)
class PromptConfig:
    vision_system: str
    vision_instruction: str
    ocr_system: str
    llm_system: str
    llm_answer_style: str
    grounding_system: str
    currency_instruction: str
    color_instruction: str
    product_instruction: str
    food_instruction: str
    people_instruction: str
    environment_instruction: str
    clothing_instruction: str
    label_instruction: str
```

Then add to the end of `get_prompt_config()`, right after `product_instruction=os.getenv(...)`  (before the closing `)`):

```python
        food_instruction=os.getenv(
            "BE_MY_EYE_FOOD_INSTRUCTION_PROMPT",
            "Identify the dish and list the visible ingredients. If asked about dietary suitability, "
            "state that it 'appears to' or 'looks like' it contains meat, pork, or alcohol -- never "
            "guarantee halal or vegetarian status. Call out visible common allergens (nuts, dairy, "
            "eggs, gluten, shellfish) as a caution, noting that hidden ingredients cannot be seen. "
            "If asked for a nutrition estimate, give a rough calorie range and state clearly that it "
            "is an approximate, photo-based guess, not a measurement.",
        ),
        people_instruction=os.getenv(
            "BE_MY_EYE_PEOPLE_INSTRUCTION_PROMPT",
            "Describe how many people are visible, their general orientation (facing toward or away "
            "from the camera), and visible expression or body language. Do not attempt to identify "
            "who any person is -- describe appearance and behavior only, never a name or identity.",
        ),
        environment_instruction=os.getenv(
            "BE_MY_EYE_ENVIRONMENT_INSTRUCTION_PROMPT",
            "Describe environment and safety-relevant conditions: whether lights appear on or off, "
            "whether the room is bright or dark, and whether any visible stove or burner appears lit. "
            "State these plainly, and say so if a condition is not clearly visible in the image.",
        ),
        clothing_instruction=os.getenv(
            "BE_MY_EYE_CLOTHING_INSTRUCTION_PROMPT",
            "Describe the visible clothing items, whether their colors match or clash, and note any "
            "visible stains or wrinkles. Keep the assessment plain and practical.",
        ),
        label_instruction=os.getenv(
            "BE_MY_EYE_LABEL_INSTRUCTION_PROMPT",
            "Read any expiry date or medicine/drug name visible on the label. State the date or name "
            "plainly. If the text is unclear or partially obscured, say so rather than guessing.",
        ),
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python3 -m pytest tests/unit/test_prompts.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/core/prompts.py backend/tests/unit/test_prompts.py
git commit -m "feat: add hedged prompt instructions for food/people/environment/clothing/label tasks"
```

---

### Task 3: Wire the five new instructions into `GroqVisionProvider`

**Files:**
- Modify: `backend/app/providers/groq.py:63-69`
- Test: `backend/tests/unit/test_groq_providers.py`

**Interfaces:**
- Consumes: `VisionTask.food/.people/.environment/.clothing/.label` (Task 1), `PromptConfig.food_instruction` etc. (Task 2).
- Produces: nothing new for later tasks — this closes the vision-task loop.

- [ ] **Step 1: Write the failing test**

In `backend/tests/unit/test_groq_providers.py`, update the shared `PROMPTS` fixture (around line 63-73) to include the five new fields:

```python
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
```

Then add a new test after `test_groq_vision_provider_defaults_to_scene_instruction`:

```python
def test_groq_vision_provider_selects_food_instruction():
    client = FakeGroqClient()
    provider = GroqVisionProvider(model="qwen-model", prompts=PROMPTS, client=client)

    provider.analyze(make_image_bytes(), "What am I eating?", [], task=VisionTask.food)

    prompt = client.chat.completions.calls[0]["messages"][0]["content"]
    prompt_text = " ".join(part.get("text", "") for part in prompt if isinstance(part, dict))
    assert "food instruction" in prompt_text
    assert "vision instruction" not in prompt_text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python3 -m pytest tests/unit/test_groq_providers.py -v`
Expected: FAIL — `PROMPTS = PromptConfig(...)` raises `TypeError: __init__() missing 5 required positional arguments` because the dataclass now requires the five new fields.

- [ ] **Step 3: Write minimal implementation**

In `backend/app/providers/groq.py`, change `_instruction_for` (currently at lines 63-69):

```python
    def _instruction_for(self, task: VisionTask) -> str:
        return {
            VisionTask.scene: self.prompts.vision_instruction,
            VisionTask.currency: self.prompts.currency_instruction,
            VisionTask.color: self.prompts.color_instruction,
            VisionTask.product: self.prompts.product_instruction,
        }[task]
```

to:

```python
    def _instruction_for(self, task: VisionTask) -> str:
        return {
            VisionTask.scene: self.prompts.vision_instruction,
            VisionTask.currency: self.prompts.currency_instruction,
            VisionTask.color: self.prompts.color_instruction,
            VisionTask.product: self.prompts.product_instruction,
            VisionTask.food: self.prompts.food_instruction,
            VisionTask.people: self.prompts.people_instruction,
            VisionTask.environment: self.prompts.environment_instruction,
            VisionTask.clothing: self.prompts.clothing_instruction,
            VisionTask.label: self.prompts.label_instruction,
        }[task]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python3 -m pytest tests/unit/test_groq_providers.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/providers/groq.py backend/tests/unit/test_groq_providers.py
git commit -m "feat: wire food/people/environment/clothing/label instructions into GroqVisionProvider"
```

---

### Task 4: Route the five new tasks in `IntentRouter` (English + Arabic)

**Files:**
- Modify: `backend/app/services/intent_router.py`
- Test: `backend/tests/unit/test_intent_router.py`

**Interfaces:**
- Consumes: `VisionTask.food/.people/.environment/.clothing/.label` (Task 1).
- Produces: `RoutingDecision.vision_task` now resolves to the new tasks based on keywords — consumed at runtime by `ConversationService` (no code change needed there; it already calls `self.router.route(transcript)` generically).

- [ ] **Step 1: Write the failing test**

Add to `backend/tests/unit/test_intent_router.py`:

```python
def test_intent_router_selects_food_task():
    router = IntentRouter()

    decision = router.route("What am I eating?")

    assert decision.vision_task == VisionTask.food


def test_intent_router_selects_food_task_in_arabic():
    router = IntentRouter()

    decision = router.route("ايه ده اللي قدامي في الطبق؟")

    assert decision.vision_task == VisionTask.food


def test_intent_router_selects_people_task():
    router = IntentRouter()

    decision = router.route("Is anyone standing in front of me?")

    assert decision.vision_task == VisionTask.people


def test_intent_router_selects_environment_task():
    router = IntentRouter()

    decision = router.route("Is the light on in this room?")

    assert decision.vision_task == VisionTask.environment


def test_intent_router_selects_clothing_task():
    router = IntentRouter()

    decision = router.route("Do my clothes match?")

    assert decision.vision_task == VisionTask.clothing


def test_intent_router_selects_label_task_for_expiry():
    router = IntentRouter()

    decision = router.route("Has this expired?")

    assert decision.vision_task == VisionTask.label


def test_intent_router_priority_food_over_scene():
    router = IntentRouter()

    decision = router.route("What food is on this plate?")

    assert decision.vision_task == VisionTask.food
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python3 -m pytest tests/unit/test_intent_router.py -v`
Expected: FAIL — all six new tests fail because `route()` falls back to `VisionTask.scene` for every one of them (no matching keyword tuple exists yet).

- [ ] **Step 3: Write minimal implementation**

In `backend/app/services/intent_router.py`, add four new keyword tuples as class attributes, right after `PRODUCT_KEYWORDS` (currently ending at line 77) and before `GROUNDING_KEYWORDS`:

```python
    FOOD_KEYWORDS = (
        "eating",
        "eat",
        "food",
        "dish",
        "meal",
        "plate",
        "ingredient",
        "اكل",
        "أكل",
        "طعام",
        "طبق",
        "وجبة",
        "مكونات",
    )
    PEOPLE_KEYWORDS = (
        "anyone",
        "someone",
        "person",
        "people",
        "standing in front",
        "facing me",
        "حد",
        "شخص",
        "ناس",
        "واقف قدامي",
        "بيبصلي",
    )
    ENVIRONMENT_KEYWORDS = (
        "light on",
        "light off",
        "lights",
        "dark",
        "bright",
        "stove",
        "burner",
        "نور",
        "ضلمة",
        "مضي",
        "البوتاجاز",
        "الفرن مشغول",
    )
    CLOTHING_KEYWORDS = (
        "clothes match",
        "match",
        "clash",
        "stain",
        "outfit",
        "هدوم",
        "متناسقة",
        "بقعة",
        "لبس",
    )
    LABEL_KEYWORDS = (
        "expired",
        "expiry",
        "expire",
        "medicine",
        "medication",
        "pill",
        "انتهت الصلاحية",
        "صلاحية",
        "دواء",
        "علاج",
    )
```

Then update the `route()` method's if/elif chain (currently lines 95-102):

```python
        if any(keyword in normalized for keyword in self.CURRENCY_KEYWORDS):
            vision_task = VisionTask.currency
        elif any(keyword in normalized for keyword in self.COLOR_KEYWORDS):
            vision_task = VisionTask.color
        elif any(keyword in normalized for keyword in self.PRODUCT_KEYWORDS):
            vision_task = VisionTask.product
        else:
            vision_task = VisionTask.scene
```

to:

```python
        if any(keyword in normalized for keyword in self.CURRENCY_KEYWORDS):
            vision_task = VisionTask.currency
        elif any(keyword in normalized for keyword in self.COLOR_KEYWORDS):
            vision_task = VisionTask.color
        elif any(keyword in normalized for keyword in self.PRODUCT_KEYWORDS):
            vision_task = VisionTask.product
        elif any(keyword in normalized for keyword in self.FOOD_KEYWORDS):
            vision_task = VisionTask.food
        elif any(keyword in normalized for keyword in self.PEOPLE_KEYWORDS):
            vision_task = VisionTask.people
        elif any(keyword in normalized for keyword in self.ENVIRONMENT_KEYWORDS):
            vision_task = VisionTask.environment
        elif any(keyword in normalized for keyword in self.CLOTHING_KEYWORDS):
            vision_task = VisionTask.clothing
        elif any(keyword in normalized for keyword in self.LABEL_KEYWORDS):
            vision_task = VisionTask.label
        else:
            vision_task = VisionTask.scene
```

**Note on keyword overlap:** `"label"` already exists in `PRODUCT_KEYWORDS` (for "what product is this, read the label") — this is intentional and pre-existing; `LABEL_KEYWORDS` here is for *expiry/medicine* label reading specifically, and since `PRODUCT_KEYWORDS` is checked first in the if/elif chain, a message containing both "label" and "expired" will resolve to `product`, not `label`. This is acceptable per YAGNI — do not attempt to disambiguate further in this task; if real usage shows this is wrong, it's a one-line reorder, not a redesign.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python3 -m pytest tests/unit/test_intent_router.py -v`
Expected: PASS — all tests, including the 7 new ones.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/intent_router.py backend/tests/unit/test_intent_router.py
git commit -m "feat: route food/people/environment/clothing/label intents (EN+AR keywords)"
```

---

### Task 5: `ProductInfo` schema + `ProductLookupProvider` interface

**Files:**
- Create: `backend/app/schemas/product.py`
- Modify: `backend/app/providers/base.py`
- Test: `backend/tests/unit/test_provider_base.py`

**Interfaces:**
- Produces: `ProductInfo` (pydantic model), `ProductLookupProvider` (abstract base class with `lookup_by_barcode(barcode: str) -> ProductInfo | None`) — consumed by Tasks 6, 7, 8.

- [ ] **Step 1: Write the failing test**

`backend/tests/unit/test_provider_base.py` currently contains exactly one test, `test_provider_interfaces_are_abstract`, which asserts `pytest.raises(TypeError)` for each existing provider ABC in one function body (it already imports `pytest` at the top). Extend that same function rather than adding a new one, to match the file's existing one-function convention:

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
```

Update the file's import line to include the new class:

```python
from app.providers.base import ASRProvider, LLMProvider, OCRProvider, ProductLookupProvider, TTSProvider, VisionProvider
```

Also add a second test in the same file confirming a concrete subclass satisfies the interface (this pattern doesn't exist yet for the other providers, but it's the only way to exercise `ProductInfo` at this layer):

```python
def test_product_lookup_provider_concrete_subclass_satisfies_interface():
    from app.schemas.product import ProductInfo

    class ConcreteProductLookup(ProductLookupProvider):
        def lookup_by_barcode(self, barcode: str) -> ProductInfo | None:
            return ProductInfo(name="test product")

    provider = ConcreteProductLookup()
    result = provider.lookup_by_barcode("123")
    assert result.name == "test product"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python3 -m pytest tests/unit/test_provider_base.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app.schemas.product'` (or `ImportError: cannot import name 'ProductLookupProvider'`).

- [ ] **Step 3: Write minimal implementation**

Create `backend/app/schemas/product.py`:

```python
from __future__ import annotations

from pydantic import BaseModel, Field


class ProductInfo(BaseModel):
    name: str
    brand: str | None = None
    ingredients_text: str | None = None
    allergens: list[str] = Field(default_factory=list)


class ProductLookupRequest(BaseModel):
    barcode: str = Field(min_length=1)


class ProductLookupResponse(BaseModel):
    found: bool
    product: ProductInfo | None = None
```

In `backend/app/providers/base.py`, add the import at the top (alongside the existing `from app.schemas.common import ConversationTurn, VisionTask`):

```python
from app.schemas.product import ProductInfo
```

Then add the new abstract class at the end of the file, after `TTSProvider`:

```python
class ProductLookupProvider(ABC):
    @abstractmethod
    def lookup_by_barcode(self, barcode: str) -> ProductInfo | None:
        raise NotImplementedError
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python3 -m pytest tests/unit/test_provider_base.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/schemas/product.py backend/app/providers/base.py backend/tests/unit/test_provider_base.py
git commit -m "feat: add ProductInfo schema and ProductLookupProvider interface"
```

---

### Task 6: `FakeProductLookupProvider`

**Files:**
- Modify: `backend/app/providers/fakes.py`
- Test: `backend/tests/unit/test_fake_providers.py`

**Interfaces:**
- Consumes: `ProductLookupProvider`, `ProductInfo` (Task 5).
- Produces: `FakeProductLookupProvider` — consumed by Task 9 (main.py wiring) for `USE_REAL_PROVIDERS=false` mode.

- [ ] **Step 1: Write the failing test**

Add to `backend/tests/unit/test_fake_providers.py`:

```python
def test_fake_product_lookup_returns_sample_product_for_known_barcode():
    from app.providers.fakes import FakeProductLookupProvider

    provider = FakeProductLookupProvider()

    result = provider.lookup_by_barcode("1234567890123")

    assert result is not None
    assert result.name
    assert "milk" in result.allergens or result.allergens == [] or result.allergens


def test_fake_product_lookup_returns_none_for_unknown_barcode():
    from app.providers.fakes import FakeProductLookupProvider

    provider = FakeProductLookupProvider()

    result = provider.lookup_by_barcode("0000000000000")

    assert result is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python3 -m pytest tests/unit/test_fake_providers.py -v`
Expected: FAIL with `ImportError: cannot import name 'FakeProductLookupProvider'`.

- [ ] **Step 3: Write minimal implementation**

In `backend/app/providers/fakes.py`, add the import at the top (alongside the existing `from app.providers.base import ...`):

```python
from app.providers.base import ProductLookupProvider
from app.schemas.product import ProductInfo
```

Then add the new class after `FakeTTSProvider`:

```python
class FakeProductLookupProvider(ProductLookupProvider):
    def lookup_by_barcode(self, barcode: str) -> ProductInfo | None:
        if barcode == "0000000000000":
            return None
        return ProductInfo(
            name="Sample Product",
            brand="Sample Brand",
            ingredients_text="water, sugar, salt",
            allergens=["milk"],
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python3 -m pytest tests/unit/test_fake_providers.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/providers/fakes.py backend/tests/unit/test_fake_providers.py
git commit -m "feat: add FakeProductLookupProvider"
```

---

### Task 7: `OpenFoodFactsProductLookupProvider` (real implementation)

**Files:**
- Add dependency: `backend/pyproject.toml`, `backend/requirements.txt`
- Create: `backend/app/providers/openfoodfacts.py`
- Test: `backend/tests/unit/test_openfoodfacts_provider.py`

**Interfaces:**
- Consumes: `ProductLookupProvider`, `ProductInfo` (Task 5).
- Produces: `OpenFoodFactsProductLookupProvider` — consumed by Task 9 (main.py wiring) for `USE_REAL_PROVIDERS=true` mode.

- [ ] **Step 1: Add the `httpx` dependency**

In `backend/pyproject.toml`, add `"httpx>=0.27"` to the `dependencies` list (alongside `fastapi`, `groq`, `pydantic`, `pillow`, `uvicorn`):

```toml
dependencies = [
    "fastapi>=0.115",
    "groq>=0.31",
    "pydantic>=2.8",
    "pillow>=10.0",
    "uvicorn>=0.30",
    "httpx>=0.27",
]
```

Then update `backend/requirements.txt` — this repo mirrors `pyproject.toml`'s dependencies there because Vercel's Python builder reads `requirements.txt`, not `pyproject.toml` (see `docs/DECISIONS.md`). Unlike `pyproject.toml`'s `>=` ranges, this file pins exact versions (e.g. `fastapi==0.136.1`). Add:

```
httpx==0.28.1
```

as a new line, so the file reads:

```
fastapi==0.136.1
groq==1.4.0
pydantic==2.12.5
pillow==12.0.0
uvicorn==0.47.0
httpx==0.28.1
```

Run: `cd backend && pip install httpx==0.28.1` to install it into your local environment.

- [ ] **Step 2: Write the failing test**

Create `backend/tests/unit/test_openfoodfacts_provider.py`:

```python
import httpx

from app.providers.openfoodfacts import OpenFoodFactsProductLookupProvider


class FakeTransport(httpx.BaseTransport):
    def __init__(self, json_body: dict, status_code: int = 200):
        self._json_body = json_body
        self._status_code = status_code

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        return httpx.Response(self._status_code, json=self._json_body)


def make_client(json_body: dict, status_code: int = 200) -> httpx.Client:
    return httpx.Client(transport=FakeTransport(json_body, status_code))


def test_openfoodfacts_returns_product_info_when_found():
    client = make_client(
        {
            "status": 1,
            "product": {
                "product_name": "Juhayna Full Cream Milk",
                "brands": "Juhayna",
                "ingredients_text": "Full cream milk",
                "allergens_tags": ["en:milk"],
            },
        }
    )
    provider = OpenFoodFactsProductLookupProvider(client=client)

    result = provider.lookup_by_barcode("6224000123456")

    assert result is not None
    assert result.name == "Juhayna Full Cream Milk"
    assert result.brand == "Juhayna"
    assert result.allergens == ["milk"]


def test_openfoodfacts_returns_none_when_not_found():
    client = make_client({"status": 0})
    provider = OpenFoodFactsProductLookupProvider(client=client)

    result = provider.lookup_by_barcode("0000000000000")

    assert result is None
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd backend && python3 -m pytest tests/unit/test_openfoodfacts_provider.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app.providers.openfoodfacts'`.

- [ ] **Step 4: Write minimal implementation**

Create `backend/app/providers/openfoodfacts.py`:

```python
from __future__ import annotations

import httpx

from app.providers.base import ProductLookupProvider
from app.schemas.product import ProductInfo

OPEN_FOOD_FACTS_URL = "https://world.openfoodfacts.org/api/v2/product/{barcode}.json"


class OpenFoodFactsProductLookupProvider(ProductLookupProvider):
    def __init__(self, client: httpx.Client | None = None, timeout: float = 5.0) -> None:
        self._client = client or httpx.Client(timeout=timeout)

    def lookup_by_barcode(self, barcode: str) -> ProductInfo | None:
        response = self._client.get(OPEN_FOOD_FACTS_URL.format(barcode=barcode))
        response.raise_for_status()
        data = response.json()

        if data.get("status") != 1:
            return None

        product = data.get("product", {})
        return ProductInfo(
            name=product.get("product_name") or "Unknown product",
            brand=product.get("brands"),
            ingredients_text=product.get("ingredients_text"),
            allergens=[tag.removeprefix("en:") for tag in product.get("allergens_tags", [])],
        )
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd backend && python3 -m pytest tests/unit/test_openfoodfacts_provider.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/pyproject.toml backend/requirements.txt backend/app/providers/openfoodfacts.py backend/tests/unit/test_openfoodfacts_provider.py
git commit -m "feat: add OpenFoodFactsProductLookupProvider"
```

---

### Task 8: `POST /product-lookup` endpoint

**Files:**
- Create: `backend/app/api/product.py`
- Test: `backend/tests/integration/test_product_api.py`

**Interfaces:**
- Consumes: `ProductLookupProvider`, `ProductLookupRequest`, `ProductLookupResponse` (Tasks 5-7).
- Produces: `create_product_router(provider)` — a FastAPI `APIRouter` factory, consumed by Task 9 (main.py wiring), matching the exact pattern `create_conversation_router` already uses in `backend/app/api/conversation.py`.

- [ ] **Step 1: Write the failing test**

Create `backend/tests/integration/test_product_api.py`:

```python
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.api.product import create_product_router
from app.providers.fakes import FakeProductLookupProvider


def make_client() -> TestClient:
    app = FastAPI()
    app.include_router(create_product_router(FakeProductLookupProvider()))
    return TestClient(app)


def test_product_lookup_returns_product_for_known_barcode():
    client = make_client()

    response = client.post("/product-lookup", json={"barcode": "1234567890123"})

    assert response.status_code == 200
    body = response.json()
    assert body["found"] is True
    assert body["product"]["name"] == "Sample Product"


def test_product_lookup_returns_not_found_for_unknown_barcode():
    client = make_client()

    response = client.post("/product-lookup", json={"barcode": "0000000000000"})

    assert response.status_code == 200
    body = response.json()
    assert body["found"] is False
    assert body["product"] is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python3 -m pytest tests/integration/test_product_api.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app.api.product'`.

- [ ] **Step 3: Write minimal implementation**

Create `backend/app/api/product.py`:

```python
from __future__ import annotations

from fastapi import APIRouter

from app.providers.base import ProductLookupProvider
from app.schemas.product import ProductLookupRequest, ProductLookupResponse


def create_product_router(provider: ProductLookupProvider) -> APIRouter:
    router = APIRouter()

    @router.post("/product-lookup", response_model=ProductLookupResponse)
    def post_product_lookup(payload: ProductLookupRequest) -> ProductLookupResponse:
        product = provider.lookup_by_barcode(payload.barcode)
        return ProductLookupResponse(found=product is not None, product=product)

    return router
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python3 -m pytest tests/integration/test_product_api.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/api/product.py backend/tests/integration/test_product_api.py
git commit -m "feat: add POST /product-lookup endpoint"
```

---

### Task 9: Wire `ProductLookupProvider` into `create_app()`

**Files:**
- Modify: `backend/app/main.py`
- Test: `backend/tests/unit/test_main.py`

**Interfaces:**
- Consumes: `FakeProductLookupProvider` (Task 6), `OpenFoodFactsProductLookupProvider` (Task 7), `create_product_router` (Task 8).
- Produces: the running app now serves `/product-lookup` alongside `/conversation` and `/health` — this is the final integration point, nothing later depends on it.

- [ ] **Step 1: Write the failing test**

`backend/tests/unit/test_main.py` currently has two tests: one checking CORS middleware registration, one checking that `create_app()` doesn't error in fake-provider mode (both call `create_app()` directly and inspect the returned `FastAPI` instance). Add a third test in the same style:

```python
def test_create_app_registers_product_lookup_route():
    app = create_app()

    paths = {route.path for route in app.routes}
    assert "/product-lookup" in paths
```

(`create_app` is already imported at the top of the file — no new import needed.)

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python3 -m pytest tests/unit/test_main.py -v`
Expected: FAIL — `/product-lookup` is not yet a registered route.

- [ ] **Step 3: Write minimal implementation**

In `backend/app/main.py`, add the new imports at the top:

```python
from app.api.product import create_product_router
from app.providers.fakes import (
    FakeASRProvider,
    FakeGroundingProvider,
    FakeLLMProvider,
    FakeOCRProvider,
    FakeProductLookupProvider,
    FakeTTSProvider,
    FakeVisionProvider,
)
from app.providers.openfoodfacts import OpenFoodFactsProductLookupProvider
```

(Note: `FakeProductLookupProvider` is added to the existing `from app.providers.fakes import (...)` block — don't create a second import line for the same module.)

Then, inside `create_app()`, right after the `if settings.use_real_providers: ... else: ...` block that builds `service` (currently ending around line 57), add:

```python
    product_lookup_provider = (
        OpenFoodFactsProductLookupProvider() if settings.use_real_providers else FakeProductLookupProvider()
    )
```

Finally, add the new router alongside the existing one:

```python
    app.include_router(create_conversation_router(service))
    app.include_router(create_product_router(product_lookup_provider))
```

(This replaces the single existing `app.include_router(create_conversation_router(service))` line — add the second line right after it.)

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python3 -m pytest tests/unit/test_main.py -v`
Expected: PASS.

- [ ] **Step 5: Run the full backend suite**

Run: `cd backend && python3 -m pytest -v`
Expected: all tests pass (the existing ~54 plus every test added in Tasks 1-9 above).

- [ ] **Step 6: Commit**

```bash
git add backend/app/main.py backend/tests/unit/test_main.py
git commit -m "feat: wire ProductLookupProvider and /product-lookup into create_app"
```

---

## Plan Complete

After Task 9, the backend supports all five new `VisionTask` capabilities (food, people, environment, clothing, label) through the existing `/conversation` endpoint, plus a new `/product-lookup` endpoint backed by Open Food Facts (or its fake, in test/dev mode). This unblocks:

- **Plan 2 (Backend TTS)** — independent of this plan, can run in parallel.
- **Plan 3 (Mobile money)** — independent of this plan, can run in parallel.
- **Plan 4 (Mobile barcode + TTS fallback)** — depends on this plan's `/product-lookup` endpoint being live.
