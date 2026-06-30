# VISION

## Mission

Build an AI-powered mobile assistant that helps blind and low-vision users understand and interact with their surroundings through natural voice conversations.

## Project Goal

Deliver a working proof of concept (POC) that allows a user to point their phone camera at a scene, ask questions about it, and receive accurate spoken responses.

The assistant should answer questions such as:

* "What is in front of me?"
* "Can I drink this?"
* "Read this document."
* "Where are my keys?"
* "Is someone standing in front of me?"

## POC Scope

The assistant operates **on demand**. It analyzes the latest camera frame only when the user asks a question.

The POC includes:

* Live camera feed
* Voice input
* Scene understanding using a Vision-Language Model (VLM)
* Reasoning using an LLM
* Conversational memory
* Spoken responses through Text-to-Speech (TTS)

The POC is intentionally dependent on the VLM for most visual reasoning. Specialized perception modules (e.g., Grounding, Depth Estimation) are planned as future extensions and are represented as architectural placeholders.

## Design Principles

* Accessibility first.
* Conversation over image captioning.
* Answer the user's intent, not just describe the scene.
* Modular, provider-agnostic architecture.
* Design for extensibility while keeping the POC simple.
* Keep AI models interchangeable through provider interfaces.

## Success Criteria

A successful POC delivers a natural conversational experience that demonstrates agentic orchestration through a modular architecture, even if some future capabilities are represented by placeholders.

The project should serve as a solid foundation for future capabilities such as object grounding, depth estimation, OCR, navigation assistance, and additional perception tools.
