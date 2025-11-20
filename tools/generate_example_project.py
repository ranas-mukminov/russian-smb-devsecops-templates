from __future__ import annotations

"""Пример генератора проектов.

Этот скрипт не создаёт реальный код приложения, а показывает как можно
автоматически собирать примеры конфигов с помощью AI-провайдеров или шаблонов.
"""

import argparse
from pathlib import Path
from typing import Dict

from logging_stack.ai_helpers.base import MockProvider
from logging_stack.ai_helpers.log_parser_suggestions import propose_parser_pipeline
from ci_security_templates.ai_pipeline_helpers.pipeline_generator import (
    generate_github_pipeline,
    generate_gitlab_pipeline,
)


def generate_bundle(output_dir: Path, metadata: Dict[str, str]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    provider = MockProvider()
    (output_dir / "promtail_pipeline.txt").write_text(
        propose_parser_pipeline("sample log line", provider)
    )
    (output_dir / "github_ci.yml").write_text(
        generate_github_pipeline(metadata, provider)
    )
    (output_dir / "gitlab_ci.yml").write_text(
        generate_gitlab_pipeline(metadata, provider)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate example DevSecOps configs")
    parser.add_argument("--output", type=Path, default=Path("./example_bundle"))
    parser.add_argument("--language", default="python")
    parser.add_argument("--framework", default="fastapi")
    args = parser.parse_args()

    metadata = {"language": args.language, "framework": args.framework}
    generate_bundle(args.output, metadata)
    print(f"Generated bundle in {args.output}")


if __name__ == "__main__":
    main()

