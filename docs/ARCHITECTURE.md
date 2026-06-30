# ARCHITECTURE

## Overview

Be My Eye follows a modular, provider-based architecture. The backend orchestrates the application flow, invokes the required AI providers, aggregates their outputs, and asks the LLM to generate the final response.

All AI capabilities are accessed through provider interfaces, allowing implementations to be replaced without affecting the rest of the system.

---

## High-Level Components

* Mobile Application
* Backend API
* Conversation Service (Orchestrator)
* AI Providers
* External AI Models

---

## Backend Responsibilities

The backend is responsible for:

* Receiving user requests.
* Managing conversation history.
* Determining which providers are required.
* Invoking the appropriate providers.
* Aggregating provider outputs.
* Invoking the LLM for reasoning.
* Returning text and audio responses to the mobile application.

The backend owns the application workflow. The LLM does not decide which providers to invoke.

---

## Provider Architecture

Each AI capability is exposed through a provider interface.

Current providers:

* Vision Provider
* OCR Provider
* LLM Provider
* ASR Provider
* TTS Provider

Planned providers:

* Grounding Provider
* Depth Provider

Providers should expose stable interfaces while hiding implementation details.

---

## Request Lifecycle

1. User captures the current scene.
2. User asks a spoken question.
3. Backend transcribes the speech.
4. Backend determines the required providers.
5. Required providers analyze the request.
6. Backend aggregates the collected information.
7. LLM generates the final response.
8. TTS converts the response into speech.
9. Mobile application plays the response.

---

## Conversation Memory

The backend maintains short-term conversation history.

Conversation history is provided to the LLM whenever it contributes to answering the user's request.

Long-term memory is outside the scope of the POC.

---

## Extensibility

The architecture is designed to support future capabilities without modifying the application workflow.

Future providers include:

* Object Grounding
* Depth Estimation
* Navigation Assistance
* Additional perception modules

Adding a new provider should require only:

1. Implementing the provider interface.
2. Registering the provider.
3. Updating the orchestration logic when appropriate.

---

## Design Principles

* Modular over monolithic.
* Provider interfaces over model-specific code.
* Backend orchestration over LLM tool orchestration.
* Accessibility over feature count.
* Extensibility over premature optimization.
* Keep the POC simple while designing for future capabilities.
