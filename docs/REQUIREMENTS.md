# REQUIREMENTS

## Functional Requirements

### FR-1. Visual Scene Understanding

The system shall analyze the latest camera frame and answer user questions about the observed scene.

### FR-2. Voice Interaction

The system shall accept spoken user input through Automatic Speech Recognition (ASR).

### FR-3. Conversational Reasoning

The system shall combine the user's request, visual context, and conversation history to generate a natural-language response.

### FR-4. Conversation Memory

The system shall maintain short-term conversation history to support multi-turn interactions.

### FR-5. Speech Output

The system shall convert generated responses into speech using Text-to-Speech (TTS).

### FR-6. Optical Character Recognition (OCR)

The system shall read and interpret visible text in the scene when requested by the user.

### FR-7. On-Demand Processing

The system shall analyze the current scene only when initiated by a user request.

### FR-8. Provider-Based Architecture

All AI capabilities shall be accessed through provider interfaces rather than directly through model implementations.

---

## Non-Functional Requirements

### NFR-1. Modular Design

The system shall consist of independent components with well-defined responsibilities.

### NFR-2. Provider Agnostic

AI providers shall be interchangeable without affecting the application logic.

### NFR-3. Extensible Architecture

The architecture shall support future capabilities such as object grounding, depth estimation, navigation assistance, and additional perception modules.

### NFR-4. Mobile-First

The primary user interface shall be a mobile application.

### NFR-5. Cloud-Based Inference

The POC shall perform AI inference using backend services and external model providers.

### NFR-6. Low Latency

The system should respond quickly enough to support natural conversations.

### NFR-7. Maintainability

The codebase shall prioritize readability, modularity, and ease of extension over implementation complexity.

---

## Out of Scope (POC)

The following capabilities are intentionally excluded from the initial implementation:

* Continuous scene monitoring.
* Autonomous or unsolicited notifications.
* Offline inference.
* Dedicated grounding models.
* Dedicated depth estimation models.
* Navigation and obstacle avoidance.
* User authentication and cloud accounts.
* Persistent long-term memory.

These capabilities are considered future extensions and should already be accommodated by the system architecture where appropriate.
