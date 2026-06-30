# API_SPEC

## Overview

The mobile application communicates with the backend through a single endpoint.

The backend is responsible for orchestrating the complete request lifecycle, including provider selection, reasoning, and response generation.

The client remains unaware of which AI providers are used to answer a request.

---

## Endpoint

### POST `/conversation`

Processes a single conversational interaction between the user and the assistant.

---

## Request

The client sends:

* Current camera frame
* Recorded user audio
* Session ID

The request represents the user's current interaction with the assistant.

---

## Backend Workflow

Upon receiving a request, the backend:

1. Transcribes the user's speech.
2. Retrieves the conversation history.
3. Determines the required AI providers.
4. Invokes the selected providers.
5. Aggregates provider outputs.
6. Generates the final response using the LLM.
7. Synthesizes the response into speech.
8. Returns the response to the client.

---

## Response

The backend returns:

* Generated response text
* Synthesized speech
* Optional metadata (development/debug mode only)

The mobile application is responsible only for presenting the response to the user.

---

## Session Management

Each request belongs to a conversation session.

The Session ID allows the backend to retrieve and update the conversation history for multi-turn interactions.

---

## Error Handling

The backend should return structured errors for situations such as:

* Invalid request format.
* Missing image or audio.
* Provider failures.
* Internal server errors.

Whenever possible, the assistant should return a meaningful spoken error message instead of failing silently.

---

## Design Principles

* A single endpoint represents the entire conversation.
* The client never communicates directly with AI providers.
* Provider selection is an internal backend concern.
* New AI capabilities must not require changes to the mobile API.
* The API should remain stable as providers evolve.
