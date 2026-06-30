# PROVIDERS

## Overview

Every AI capability is exposed through a provider interface.

Providers encapsulate model-specific logic and expose a stable capability to the rest of the application. The backend interacts only with provider interfaces and never directly with underlying models or external APIs.

---

## Vision Provider

**Responsibility**

Analyze visual scenes and answer questions about image content.

**Current Implementation**

Vision-Language Model (VLM).

**Future Extensions**

* Scene summarization
* Object relationships
* Visual reasoning
* Image comparison

---

## OCR Provider

**Responsibility**

Extract and interpret textual information from images.

**Current Implementation**

May delegate to the VLM.

**Future Extensions**

Dedicated OCR models and document understanding.

---

## LLM Provider

**Responsibility**

Generate natural-language responses using the collected context from all providers and the conversation history.

The LLM is responsible for reasoning, not orchestration.

---

## ASR Provider

**Responsibility**

Convert user speech into text.

---

## TTS Provider

**Responsibility**

Convert generated text responses into natural speech.

---

## Grounding Provider (Future)

**Responsibility**

Locate user-requested objects within the scene.

**Examples**

* "Where are my keys?"
* "Find my wallet."
* "Locate the coffee mug."

This provider is a placeholder for the POC.

---

## Depth Provider (Future)

**Responsibility**

Estimate spatial relationships and approximate distances between the camera and detected objects.

**Examples**

* "How far is the chair?"
* "Is the bottle within reach?"

This provider is a placeholder for the POC.

---

## Provider Principles

All providers should:

* Have a single responsibility.
* Hide implementation details.
* Be independently replaceable.
* Be independently testable.
* Avoid dependencies on other providers whenever possible.
* Expose stable interfaces to the backend.

The backend is the only component responsible for coordinating multiple providers.

---

## Provider Independence

Changing a provider implementation must not require changes to the application logic.

Examples:

* Replace Gemini with another VLM.
* Replace Whisper with another ASR model.
* Replace a cloud provider with a local model.
* Introduce a dedicated OCR engine.
* Add Grounding or Depth providers.

These changes should be isolated to the corresponding provider implementation.
