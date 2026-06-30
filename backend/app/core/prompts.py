from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class PromptConfig:
    vision_system: str
    vision_instruction: str
    ocr_system: str
    llm_system: str
    llm_answer_style: str
    grounding_system: str


def get_prompt_config() -> PromptConfig:
    return PromptConfig(
        vision_system=os.getenv(
            "BE_MY_EYE_VISION_SYSTEM_PROMPT",
            "You are an accessibility assistant for blind and low-vision users.",
        ),
        vision_instruction=os.getenv(
            "BE_MY_EYE_VISION_INSTRUCTION_PROMPT",
            "Answer the user's question about the image concisely, clearly, and without unnecessary detail.",
        ),
        ocr_system=os.getenv(
            "BE_MY_EYE_OCR_SYSTEM_PROMPT",
            "Extract the visible text from the image. Preserve line breaks when they help readability. If the text is unreadable, say so briefly.",
        ),
        llm_system=os.getenv(
            "BE_MY_EYE_LLM_SYSTEM_PROMPT",
            "You are an accessibility assistant. Use the user's transcript, the scene summary, OCR text, and conversation history to answer concisely.",
        ),
        llm_answer_style=os.getenv(
            "BE_MY_EYE_LLM_ANSWER_STYLE_PROMPT",
            "Respond in one short, natural sentence. Do not expose internal implementation details.",
        ),
        grounding_system=os.getenv(
            "BE_MY_EYE_GROUNDING_SYSTEM_PROMPT",
            "Identify where a user-referenced object is likely located in the image.",
        ),
    )

