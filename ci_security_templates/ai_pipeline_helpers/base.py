from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List


class AIProvider(ABC):
    """Interface for pluggable AI providers. No secrets stored in code."""

    @abstractmethod
    def complete(self, prompt: str, *, temperature: float = 0.3, max_tokens: int = 512) -> str:
        raise NotImplementedError

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], *, temperature: float = 0.3, max_tokens: int = 512) -> str:
        raise NotImplementedError


class MockProvider(AIProvider):
    def complete(self, prompt: str, *, temperature: float = 0.3, max_tokens: int = 512) -> str:
        return f"mock-draft: {prompt[:80]}..."

    def chat(self, messages: List[Dict[str, str]], *, temperature: float = 0.3, max_tokens: int = 512) -> str:
        content = " | ".join([m.get("content", "") for m in messages])
        return f"mock-chat: {content[:120]}..."
