from __future__ import annotations


class IntentRouter:
    OCR_KEYWORDS = (
        "read",
        "text",
        "document",
        "sign",
        "label",
        "receipt",
        "menu",
        "page",
    )

    def select_providers(self, user_message: str) -> list[str]:
        normalized = user_message.lower()
        selected = ["vision"]
        if any(keyword in normalized for keyword in self.OCR_KEYWORDS):
            selected.append("ocr")
        return selected

