# COMPONENTS

## Overview

Be My Eye is implemented as a modular monolith. Each component has a single responsibility and communicates with other components through well-defined interfaces.

The backend remains a single application while keeping internal responsibilities clearly separated.

---

## Mobile Application

**Responsibility**

* Capture camera frames.
* Record user speech.
* Send requests to the backend.
* Play synthesized responses.
* Display optional visual feedback for debugging.

---

## Backend API

**Responsibility**

Entry point for all client requests.

Responsibilities include:

* Receiving images and audio.
* Managing request lifecycle.
* Returning text and speech responses.

The API contains no business logic.

---

## Conversation Service

**Responsibility**

The central orchestrator of the application.

Responsibilities:

* Maintain conversation history.
* Determine which providers are required.
* Invoke providers.
* Aggregate provider outputs.
* Request the final response from the LLM.

The Conversation Service owns the application workflow.

---

## Provider Layer

**Responsibility**

Provide all AI capabilities through interchangeable provider interfaces.

Current providers:

* Vision
* OCR
* LLM
* ASR
* TTS

Future providers:

* Grounding
* Depth

---

## Prompt Manager

**Responsibility**

Store and manage all prompts used throughout the application.

Examples include:

* Vision prompts.
* OCR prompts.
* LLM system prompts.
* Response formatting instructions.

Prompts should remain outside application logic whenever possible.

---

## Configuration

**Responsibility**

Centralize application configuration.

Examples:

* Model providers.
* API keys.
* Runtime parameters.
* Feature flags.

Configuration should be independent of business logic.

---

## Future Components

The following components may be introduced as the project evolves:

* Provider Registry
* Navigation Service
* Scene Memory
* Background Perception Engine
* Planning Agent

These are intentionally excluded from the initial POC.
