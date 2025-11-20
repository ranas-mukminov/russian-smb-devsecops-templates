from __future__ import annotations

from typing import List

from .base import AIProvider


def build_incident_description(events: List[dict], provider: AIProvider, language: str = "ru") -> str:
    """Генерирует краткое описание инцидента из списка событий.

    events: список словарей с ключами вроде "timestamp", "service", "message".
    language: 'ru' или 'en'.
    """

    joined = "\n".join([f"{e.get('timestamp')} {e.get('service')} {e.get('message')}" for e in events])
    prompt = (
        "Сформируй краткое описание инцидента и гипотезу RCA. "
        f"Язык: {language}. События:\n{joined}\n"
        "Дай рекомендации по следующим шагам: эскалация, сбор доп. логов, метрики."
    )
    return provider.complete(prompt)

