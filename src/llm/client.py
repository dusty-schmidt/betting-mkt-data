"""Thin wrapper around an LLM service.

At the moment this is a stub that returns a deterministic placeholder.
Replace the implementation with OpenAI/Anthropic/etc. when you are ready.
"""

from typing import Any

class LLMClient:
    """Simple LLM client – swap out `call` for a real provider later."""
    def __init__(self, model: str = "stub"):
        self.model = model

    def call(self, prompt: str) -> str:
        """Send a prompt and get a response.

        For the stub we just echo the prompt with a short note.
        """
        placeholder = (
            "🧩 [LLM‑STUB] I received the prompt but am not connected to a real model yet.\n"
            f"Prompt length: {len(prompt)} characters."
        )
        return placeholder
