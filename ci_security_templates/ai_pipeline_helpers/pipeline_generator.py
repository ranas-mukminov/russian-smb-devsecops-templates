from __future__ import annotations

from typing import Dict

from .base import AIProvider


def _render_metadata(metadata: Dict[str, str]) -> str:
    return ", ".join(f"{k}={v}" for k, v in metadata.items())


def generate_github_pipeline(project_metadata: Dict[str, str], provider: AIProvider) -> str:
    """Generate a YAML draft for GitHub Actions based on project metadata."""

    prompt = (
        "Предложи GitHub Actions workflow для безопасного CI. "
        "Включи тесты, линтер, SAST, dependency scan и Trivy. "
        f"Метаданные: {_render_metadata(project_metadata)}"
    )
    return provider.complete(prompt)


def generate_gitlab_pipeline(project_metadata: Dict[str, str], provider: AIProvider) -> str:
    """Generate a YAML draft for GitLab CI based on project metadata."""

    prompt = (
        "Сгенерируй .gitlab-ci.yml черновик. Стадии: test, lint, sast, deps, container_scan. "
        f"Учти язык/фреймворк: {_render_metadata(project_metadata)}"
    )
    return provider.complete(prompt)

