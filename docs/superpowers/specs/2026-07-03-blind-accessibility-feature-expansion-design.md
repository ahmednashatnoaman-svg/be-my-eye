# Be My Eye: Blind-Accessibility Feature Expansion — Design

## 1. Understanding Summary

- **What:** Expand Be My Eye from a single-cloud-VLM MVP into a hybrid assistant: the existing Groq VLM stays for rich description, a new **on-device** Egyptian banknote detector handles money, and a **native Egyptian voice** replaces the current Saudi TTS. A broad set of new single-photo capabilities is added for blind/low-vision Egyptian Arabic speakers.
- **Why:** Money and voice authenticity are both accuracy-critical for real-world trust, and the current one-VLM-for-everything design can't hit acceptable accuracy on either.
- **Who:** Blind and low-vision Egyptian Arabic speakers, in everyday moments — shopping, cooking, reading labels, judging a room, being around other people.
- **Scope (this expansion):** Egyptian money (on-device), Egyptian voice (cloud + offline fallback), food (dish + ingredients + dietary flags + allergens + nutrition estimate, all hedged), full scene + object description, product & label reading (identity/ingredients/expiry/medicine — not price), people & social awareness (describe, never identify), environment & safety cues, daily-living helpers (clothing match, screen/ATM reading).
- **Explicit non-goals:** Real-time obstacle/hazard alerts and Emergency/SOS (need live-video streaming — a different, safety-critical pipeline); face *identity* recognition (privacy); barcode → live price (no free data source exists).
- **Guiding constraint:** Every feature stays on the existing single-photo → analyze → speak pipeline, and everything stays free to run.

## 2. Assumptions

- **Cost:** Groq free tier (VLM + ASR, as today), a free Hugging Face Space for Egyptian TTS, on-device money model (free forever, no hosting), Open Food Facts (free, open) for barcode lookups.
- **Platforms:** On-device money model ships for **both iOS and Android** (per "implement all").
- **Egyptian TTS choice:** **NAMAA-Egyptian-TTS** as primary (newest, actively maintained), **EGTTS V0.1** as a documented fallback if NAMAA proves unreliable to self-host.
- **Latency targets:** money detection <1s on-device; VLM-based description tasks ~2-5s online; every safety-relevant answer (money, allergens, dietary, medicine) is hedged ("appears to," "looks like," never a bare guarantee).
- **Privacy:** people-awareness features describe appearance/behavior only, never identify individuals by name or match against any stored identity. Images leave the phone only for the online description tasks that need the cloud VLM; money detection and the offline TTS fallback never leave the device.
- **Architecture hygiene:** every new capability is added behind the existing provider-interface pattern (`VisionProvider`, `OCRProvider`, etc.) and the existing bilingual (EN/AR) keyword `IntentRouter`, matching how currency/color/product/grounding were added in the prior MVP round.
- **Money UX:** a **dedicated "Money Mode" gesture** (not the general voice hold-to-ask flow) triggers on-device detection directly — see Decision D-1 below for why.

## 3. Decision Log

| # | Decision | Alternatives considered | Why |
|---|---|---|---|
| D-1 | Money detection is triggered by a **dedicated gesture/button**, bypassing ASR and the network entirely | Route through the existing voice flow, relying on the backend's transcript to detect "money" intent | The offline/instant promise for money is impossible if it depends on a server round-trip for transcription. A dedicated trigger guarantees money works with zero network dependency, matching how a real blind user needs it to work at a cash register. |
| D-2 | Egyptian pound denominations are spoken via a small set of **pre-cached/on-device phrases**, not the cloud Egyptian TTS | Route money announcements through the same Egyptian cloud TTS as everything else | Denominations are a closed set (5/10/20/50/100/200 EGP + coins) — perfect for caching. This also means money mode has zero TTS latency and zero TTS network dependency, consistent with D-1. |
| D-3 | Money model = reuse existing open Egyptian banknote weights (Roboflow/Banha University dataset, YOLOv8-family), converted to TFLite (Android) / Core ML (iOS) | Train a new model from scratch | A ready, well-performing (~99% mAP@0.5 in published research) open model already exists; training from scratch would be far more effort for no accuracy gain. |
| D-4 | Egyptian voice = cloud TTS (NAMAA) for all *non-money* speech, with the phone's built-in offline Arabic voice as a fallback when offline or the cloud model is cold | Cloud-only; on-device-only | Balances authentic dialect (online) against "never silent" (offline), at the cost of building two TTS paths. |
| D-5 | New VLM-based features (food, people, environment, clothing) are added as new `VisionTask` enum values with dedicated prompts, following the exact pattern used for currency/color/product | A single mega-prompt covering everything at once | Keeps each task's prompt focused and testable in isolation; matches the codebase's existing extension point exactly, so no new architecture is needed. |
| D-6 | Barcode lookup returns product identity, ingredients, and allergens via Open Food Facts; **price is dropped from scope** | Promise price lookup via a scraped/paid API | No free, reliable, real-time price data source exists. Overselling this would ship a broken/misleading feature. |
| D-7 | Single design spec, multiple implementation plans (not one plan) | One large plan covering everything | The work spans genuinely separate subsystems (mobile on-device ML, mobile barcode UI, backend prompts/routing, backend TTS proxy) — matches how the original MVP was split into Plans 1/2/3/5. |

## 4. Architecture

```
Voice flow (existing, extended):
  Mobile: hold-to-ask -> capture photo + audio -> POST /conversation
  Backend: ASR -> IntentRouter (EN+AR keywords) -> route to one of:
     scene | currency(*) | color | product | food | people | environment
     | clothing | label  -> Vision/OCR/Grounding -> LLM -> TTS -> response
  (*) "currency" via voice still works online, using the VLM as today —
      just less accurate than Money Mode. Kept for continuity/backup.

Money Mode (new, separate trigger):
  Mobile: dedicated gesture -> capture photo only (no audio, no network)
     -> on-device YOLOv8 (TFLite/Core ML) -> denomination + confidence
     -> speak from small pre-cached phrase set (on-device)
  Fully offline. Falls back to "please reposition, not clear enough"
  below a confidence threshold instead of guessing.

TTS path (new):
  Backend or mobile calls Egyptian cloud TTS (NAMAA, hosted on a free
  HF Space) for all non-money responses.
  If the call fails or times out (cold start / offline): mobile speaks
  the response text using the phone's built-in Arabic voice instead.

Barcode / label flow (new):
  Mobile: barcode scan (camera, on-device barcode reader) -> barcode
     value -> backend -> Open Food Facts lookup -> name/ingredients/
     allergens -> LLM phrases the answer -> TTS
  Expiry-date and medicine-label reading: existing OCR provider + a
  new `label` VisionTask prompt tuned for dates and drug names.
```

## 5. Components

**Backend (`backend/app/`)**
- `schemas/common.py`: extend `VisionTask` with `food`, `people`, `environment`, `clothing`, `label`.
- `core/prompts.py`: add an instruction field per new task, following the existing `currency_instruction`/`color_instruction` pattern — each hedged per the safety framing above.
- `services/intent_router.py`: extend EN+AR keyword tuples for each new task.
- `providers/`: new `ProductLookupProvider` interface (+ fake + real Open Food Facts implementation); new `EgyptianTTSProvider` wrapping the HF Space call, with the existing `GroqTTSProvider` demoted to the "OS-fallback signal" path (backend returns a flag when its own TTS call fails, so mobile knows to use the local voice).
- `api/`: no new endpoints needed for VLM-based tasks (routed through existing `/conversation`); one new endpoint for barcode lookup (`POST /product-lookup`).

**Mobile (`mobile/lib/`)**
- New `money/` feature module: on-device YOLOv8 inference (via a TFLite/Core ML Flutter plugin), a dedicated Money Mode entry point (separate gesture from hold-to-ask), and a small `EgyptianDenominationPhrases` cache.
- `conversation/audio_playback.dart` or a new `tts_fallback.dart`: try cloud-voiced audio from the backend response; on failure/timeout, use `flutter_tts` (or equivalent) with the OS Arabic voice.
- New `barcode/` feature module: camera-based barcode scanning, calling the new backend endpoint.
- Existing `conversation_screen.dart`: add a second, always-visible button (below/beside the hold-to-ask target) labeled "Money" with its own `Semantics` label, plus a third for "Scan barcode." A discrete tappable button — not a gesture variant on the same target — is the most screen-reader-discoverable pattern (TalkBack/VoiceOver users swipe between distinct focusable elements; a long-press-count or double-tap variant on one element is not reliably discoverable).

## 6. Error Handling & Edge Cases

- Money: below-confidence-threshold result → "I'm not confident, please reposition the note" (never guesses a wrong denomination).
- TTS: any cloud failure/timeout → immediate fallback to on-device OS voice, never silent.
- Barcode: not found in Open Food Facts → "I don't recognize this product's barcode," falls back to VLM label reading.
- Allergen/dietary/medicine outputs: always hedged language, explicitly never phrased as a medical or religious guarantee.
- Offline entirely: Money Mode works fully; everything else (voice flow, barcode lookup, VLM tasks) requires connectivity and surfaces a clear "no connection" spoken message rather than hanging.

## 7. Testing Strategy

- Backend: one unit test file per new provider/task, following the existing per-module pattern; router tests extended with EN+AR cases per new keyword set (mirroring the Arabic-bug fix precedent from the MVP round).
- Mobile: on-device model tested against a held-out sample of real Egyptian banknote photos (accuracy spot-check, not exhaustive); TTS fallback tested by simulating a cloud-call failure; barcode flow tested with fake lookup responses.
- Live verification: reuse `backend/scripts/live_image_smoke.py` pattern for each new voice-routed feature, since this MVP already learned that fakes alone missed the Arabic-routing bug.

## 8. Delivery Plan (multiple plans, per D-7)

1. **Backend features plan** — new VisionTasks, prompts, router keywords, ProductLookupProvider + Open Food Facts, `/product-lookup` endpoint.
2. **Backend TTS plan** — EgyptianTTSProvider (HF Space), OS-fallback signaling in the response contract.
3. **Mobile money plan** — on-device YOLOv8 conversion (iOS + Android), Money Mode UI, cached denomination phrases.
4. **Mobile barcode + TTS-fallback plan** — barcode scanning UI, OS Arabic voice fallback wiring, calling the new endpoints.
5. **Docs plan** — README/ROADMAP updates, new decisions in DECISIONS.md.
