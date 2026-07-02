# DECISIONS

## D-001: Use a Modular Monolith Architecture

**Decision**

Build the system as a single backend application with clearly separated internal components.

**Reason**

The POC does not need microservices. A modular monolith keeps development fast while preserving clean boundaries.

---

## D-002: Backend as the Orchestrator

**Decision**

The backend controls the workflow and decides which capabilities are required.

The LLM is responsible for reasoning and generating responses, not for controlling application flow.

**Reason**

Deterministic orchestration is easier to debug, test, and optimize during the POC.

---

## D-003: Provider-Based AI Architecture

**Decision**

All AI capabilities must be accessed through provider interfaces.

Examples:

* Vision Provider
* OCR Provider
* LLM Provider
* ASR Provider
* TTS Provider

**Reason**

Models and external APIs should be replaceable without affecting application logic.

---

## D-004: Single Mobile-to-Backend Endpoint

**Decision**

The mobile application communicates through one main endpoint:

`POST /conversation`

**Reason**

The user interacts with an assistant, not individual AI services. Provider selection should remain hidden from the client.

---

## D-005: Backend Handles All AI Processing

**Decision**

The mobile application only handles:

* Camera capture
* Audio recording
* Audio playback
* User interaction

AI inference happens on the backend.

**Reason**

Keeps the mobile app lightweight and allows faster iteration on AI components.

---

## D-006: On-Demand Vision Processing

**Decision**

The system analyzes the latest camera frame only when the user asks a question.

**Reason**

Continuous perception adds complexity and unnecessary cost for the POC.

---

## D-007: Conversation Memory Is Required

**Decision**

The assistant maintains short-term conversation history.

**Reason**

Natural interactions require multi-turn understanding.

Example:

User:
"What is this?"

User:
"What color is it?"

The second question depends on previous context.

---

## D-008: VLM-First Visual Understanding for POC

**Decision**

The initial implementation relies heavily on the Vision-Language Model.

Dedicated perception modules are postponed.

**Future Extensions**

* Grounding Provider
* Depth Provider

**Reason**

A VLM provides enough capability for the initial demo while keeping implementation simple.

---

## D-009: OCR as a Separate Capability

**Decision**

OCR is represented as its own provider even if initially implemented through the VLM.

**Reason**

Reading text is a distinct accessibility capability and may later use specialized models.

---

## D-010: Avoid Early Agentic Tool Calling

**Decision**

Do not let the LLM dynamically decide which tools/providers to call in the POC.

**Reason**

Agentic orchestration introduces complexity before the core experience is validated.

The architecture should support it later.

---

## D-011: Flutter for Mobile Application

**Decision**

Use Flutter for the mobile client.

**Reason**

Provides a fast cross-platform development path with good camera and audio support.

---

## D-012: Cloud-Based Inference

**Decision**

Use external AI providers/backend inference instead of running models locally.

**Reason**

The available hardware and timeline favor rapid development over local optimization.

---

## D-013: Design for Future Spatial Understanding

**Decision**

Keep placeholders for:

* Grounding
* Depth estimation
* Navigation

**Reason**

Spatial understanding is important for the long-term vision but outside the POC scope.

---

## D-014: Scoped `.gitignore` Files Per Language Root

**Decision**

Use a minimal root `.gitignore` for cross-cutting, OS/editor/secret patterns only. Each
language root (`backend/`, `mobile/`) owns a `.gitignore` scoped to its own toolchain.

**Reason**

The original root `.gitignore` was a Python template. Its `lib/` pattern silently matched
Flutter's `mobile/lib/` source root, causing every historical mobile commit to exclude the
actual app code. A single shared ignore file across a polyglot monorepo is a recurring
footgun; scoping ignore files to their language root prevents one toolchain's conventions
from silently deleting another's source tree.

---

## D-016: Deploy the Backend on Vercel via `[tool.vercel]` Entrypoint

**Decision**

Deploy the FastAPI backend on Vercel's Python runtime (Fluid Compute). Point Vercel at the
existing `app.main:app` instance through `[tool.vercel] entrypoint` in `pyproject.toml`
rather than creating a wrapper file or moving the app under an `api/` directory.

**Reason**

Vercel's FastAPI framework detection supports a configurable entrypoint, so the existing
package layout (`app/main.py`, `app/api/`, `app/services/`, `app/providers/`) stays
untouched. Fluid Compute's 300s ceiling comfortably covers the ASR → Vision → OCR → LLM →
TTS chain, and Vercel's Git-integration deploys give preview URLs on every PR for free.
