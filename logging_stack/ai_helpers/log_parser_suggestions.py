from __future__ import annotations

from typing import Dict

from .base import AIProvider


def propose_parser_pipeline(example: str, provider: AIProvider) -> str:
    """Возвращает черновик пайплайна promtail/Logstash на основе описания формата лога.

    Функция не вызывает сеть — структуру генерирует провайдер, который можно подменить на заглушку.
    """

    prompt = (
        "Сгенерируй черновик пайплайна для promtail или Logstash. "
        "Опиши grok/regex для полей status, user_ip, uri, duration (если есть)."
        f" Пример лога: {example}"
    )
    return provider.complete(prompt)


def propose_logstash_pipeline(example: str, provider: AIProvider) -> Dict[str, str]:
    """Возвращает минимальный словарь с pipeline grok и советами."""

    base = provider.complete(f"Опиши grok для logstash под строку: {example}")
    return {"pipeline": base, "note": "Черновик, проверьте вручную перед продом"}

