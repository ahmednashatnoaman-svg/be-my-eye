# AGENT_CONTEXT

## Project Overview

Be My Eye is an AI-powered mobile assistant that helps blind and low-vision users understand and interact with their surroundings through voice conversations.

The user provides a camera view and a spoken request. The system analyzes the scene, reasons about the request, and responds through speech.

The project is currently a proof of concept focused on delivering a working end-to-end experience.

---

## Core Architecture

The system follows a modular monolith architecture.

Main components:

* Mobile Application
* Backend API
* Conversation Service
* AI Providers

The backend is responsible for orchestration.

The LLM is responsible for reasoning and response generation, not deciding application workflow.

---

## Important Design Decisions

### Provider-Based Architecture

All AI capabilities must be accessed through provider interfaces.

Examples:

* Vision Provider
* OCR Provider
* LLM Provider
* ASR Provider
* TTS Provider

Do not tightly couple application logic to a specific model or API.

---

### Single Conversation Endpoint

The mobile application communicates with the backend through a single conversational interface.

The mobile app should not know which AI capabilities are used internally.

---

### Backend Orchestration

Provider selection and workflow logic belong to the backend.

Avoid implementing agentic tool-calling logic inside the LLM for the POC.

---

## Coding Principles

When implementing new features:

* Prefer simple solutions.
* Avoid unnecessary abstractions.
* Keep components focused on one responsibility.
* Preserve provider boundaries.
* Avoid duplicating business logic.
* Write code that is easy to replace or extend.

---

## Current Scope

The POC should support:

* Camera input.
* Voice input.
* Scene understanding.
* OCR.
* Conversational memory.
* Spoken responses.

Future capabilities such as:

* Object grounding.
* Depth estimation.
* Navigation.
* Continuous monitoring.

should be considered during design but not implemented unless explicitly requested.

---

## Before Making Changes

Always check:

1. Which component owns this responsibility?
2. Can this be implemented through an existing provider?
3. Does this change violate provider independence?
4. Does this introduce unnecessary complexity?
5. Does the change affect the API contract?

---

## Source of Truth

When making implementation decisions, refer to:

1. ARCHITECTURE.md
2. COMPONENTS.md
3. PROVIDERS.md
4. REQUIREMENTS.md
5. API_SPEC.md

If a new decision changes the architecture, update the relevant documentation.

---

## Development Mindset

The goal is not to build the most complex AI system.

The goal is to build a reliable, extensible accessibility assistant with a clean foundation that can grow beyond the POC.
