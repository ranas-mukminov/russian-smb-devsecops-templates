from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class AIProvider(ABC):
    """Абстрактный интерфейс для подключения стороннего ИИ-провайдера.

    Реализация должна инкапсулировать сетевые вызовы и не хранить секреты в коде.
    """

    @abstractmethod
    def complete(self, prompt: str, *, temperature: float = 0.2, max_tokens: int = 512) -> str:
        raise NotImplementedError

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], *, temperature: float = 0.2, max_tokens: int = 512) -> str:
        raise NotImplementedError

    def name(self) -> str:
        return self.__class__.__name__


class MockProvider(AIProvider):
    """Простая заглушка, которую можно использовать в тестах."""

    def complete(self, prompt: str, *, temperature: float = 0.2, max_tokens: int = 512) -> str:
        return f"[mock:{self.name()}] {prompt[:64]}..."

    def chat(self, messages: List[Dict[str, str]], *, temperature: float = 0.2, max_tokens: int = 512) -> str:
        joined = " | ".join([m.get("content", "") for m in messages])
        return f"[mock:{self.name()}] {joined[:128]}..."

