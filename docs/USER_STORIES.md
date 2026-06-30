# USER_STORIES

## US-1. Scene Understanding

**Story**

As a blind user, I want the assistant to describe my surroundings so that I can understand what is in front of me.

**Example**

> User: "What is in front of me?"

> Assistant: "You're looking at a wooden desk with a laptop, a notebook, and a coffee mug."

**Acceptance Criteria**

* Uses the latest camera frame.
* Produces a concise and natural response.
* Responds through speech.

---

## US-2. Object Questions

**Story**

As a blind user, I want to ask questions about objects in my surroundings.

**Example**

> User: "Can I drink this?"

> Assistant: "It appears to be a sealed bottle of water."

**Acceptance Criteria**

* Understands the user's intent.
* Answers based on the current scene.
* Avoids unnecessary scene descriptions.

---

## US-3. Reading Text

**Story**

As a blind user, I want the assistant to read visible text aloud.

**Example**

> User: "Read this page."

> Assistant: *(Reads the visible text.)*

**Acceptance Criteria**

* Extracts text from the image.
* Reads the detected text naturally.
* Indicates if the text is unreadable.

---

## US-4. Conversation Memory

**Story**

As a blind user, I want the assistant to remember previous questions so I can speak naturally.

**Example**

> User: "What is this?"

> Assistant: "It's a bottle of orange juice."

> User: "Is it open?"

> Assistant: "No, it appears to be sealed."

**Acceptance Criteria**

* Maintains short-term conversation history.
* Resolves references from previous turns.

---

## US-5. Natural Voice Interaction

**Story**

As a blind user, I want to communicate entirely by voice.

**Example**

The user speaks naturally without interacting with on-screen controls beyond starting the conversation.

**Acceptance Criteria**

* Accepts spoken input.
* Returns spoken responses.
* Does not require typing.

---

## Future Stories

The following stories are intentionally outside the POC scope:

* Locate specific objects ("Where are my keys?")
* Estimate object distance ("How far is the chair?")
* Navigation assistance.
* Obstacle awareness.
* Continuous environmental monitoring.
