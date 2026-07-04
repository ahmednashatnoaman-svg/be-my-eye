# API_SPEC

## Overview

The mobile application communicates with the backend through four endpoints: the
general-purpose conversational flow (`/conversation`), and three dedicated fast paths
added for specific accessibility features (`/currency-lookup`, `/product-lookup`,
`/health`). `/conversation` remains the primary, catch-all endpoint; the others exist
because Money Mode and barcode scanning need a faster, more direct round-trip than
routing every request through the full ASR → routing → LLM pipeline.

The backend is responsible for orchestrating each endpoint's request lifecycle,
including provider selection, reasoning, and response generation. The client remains
unaware of which AI providers are used to answer a request.

---

## Endpoints

### POST `/conversation`

Processes a single conversational interaction between the user and the assistant —
the hold-to-ask flow. Also supports multi-turn history (see below).

### POST `/currency-lookup`

Powers Money Mode: a direct image-in, spoken-denomination-out request that bypasses
ASR/LLM entirely. Tries the specialist `CurrencyDetectionProvider` (Roboflow) first,
falling back to the general VLM when unconfident or unconfigured.

### POST `/product-lookup`

Powers barcode scanning: takes a scanned barcode string and returns product identity,
ingredients, and allergens via Open Food Facts. No image or audio involved.

### GET `/health`

Liveness check. Returns `{"status": "ok"}`.

---

## Request

### `/conversation`

The client sends:

* Current camera frame (`image_base64`)
* Recorded user audio (`audio_base64`)
* Session ID (`session_id`)
* Optional `history`: a list of `{user_text, assistant_text}` turns from earlier in
  the conversation. When supplied, this is preferred over the backend's own
  in-memory session store — see [Session Management](#session-management).
* Optional `debug` flag for verbose response metadata

### `/currency-lookup`

* Current camera frame (`image_base64`) only — no audio, no session ID.

### `/product-lookup`

* A scanned barcode string (`barcode`, 6-14 numeric digits) only — no image, audio,
  or session ID.

---

## Backend Workflow

### `/conversation`

1. Transcribes the user's speech.
2. Retrieves the conversation history (from `request.history` if supplied, otherwise
   the backend's own in-memory session store).
3. Determines the required AI providers.
4. Invokes the selected providers.
5. Aggregates provider outputs.
6. Generates the final response using the LLM.
7. Synthesizes the response into speech.
8. Returns the response to the client.

### `/currency-lookup`

1. Tries the specialist currency-detection provider on the image.
2. Falls back to the general VLM if unconfident (below 60% confidence) or
   unconfigured.
3. Maps the result to a spoken phrase and synthesizes speech.

### `/product-lookup`

1. Looks up the barcode against the product-lookup provider (Open Food Facts).
2. Returns whether a product was found and its details, if so.

---

## Response

### `/conversation`

The backend returns:

* Generated response text (`text`)
* The ASR transcript of what the user said (`transcript`) — always present,
  regardless of the `debug` flag, so clients can build multi-turn history without
  needing debug mode
* Synthesized speech (`audio_base64`), or an empty string with
  `tts_fallback_required: true` if TTS synthesis failed (the mobile client then
  speaks the text locally using the device's own voice)
* Optional metadata (`debug`, only when the `debug` flag is set on the request)

### `/currency-lookup`

* Whether a confident detection was found (`found`), the denomination and
  confidence if so, and a spoken phrase (`spoken_text`) plus synthesized audio
  (with the same `tts_fallback_required` fallback behavior as `/conversation`)

### `/product-lookup`

* Whether the barcode matched a product (`found`) and its details if so (name,
  brand, ingredients, allergens)

The mobile application is responsible only for presenting the response to the user.

---

## Session Management

`/conversation` requests belong to a conversation session, identified by `session_id`.

Multi-turn history can come from either side: the client can send `history` directly
in the request (the mobile app does this, accumulating `ConversationTurn`s locally
after each turn), or the backend falls back to its own in-memory session store keyed
by `session_id`. The client-supplied path is preferred because the backend runs on
Vercel's serverless functions, where an in-process store does not reliably survive
across function invocations or cold starts — see `docs/DECISIONS.md` (D-021).

`/currency-lookup` and `/product-lookup` are stateless — no session ID or history.

---

## Error Handling

Every endpoint returns structured errors for situations such as:

* Invalid request format (schema validation failures — FastAPI's built-in 422).
* Invalid base64 payloads for image/audio fields (`400`, `ErrorResponse`).
* Provider failures — `/conversation` wraps every provider call (ASR, Vision, OCR,
  grounding, LLM) so an upstream rejection (e.g. malformed audio/image) returns a
  clean `400 ErrorResponse` instead of an unhandled `500`.

Whenever possible, the assistant should return a meaningful spoken error message
instead of failing silently — see `tts_fallback_required` above.

---

## Design Principles

* `/conversation` is the general-purpose, catch-all endpoint for anything not covered
  by a dedicated fast path.
* Dedicated endpoints (`/currency-lookup`, `/product-lookup`) exist only when a
  feature genuinely needs a faster, more direct round-trip than the full
  conversational pipeline — not by default for every new capability.
* The client never communicates directly with AI providers.
* Provider selection is an internal backend concern.
* The API should remain stable as providers evolve.
