from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml

ROOT = Path(__file__).resolve().parents[1]
CI_ROOT = ROOT / "ci_security_templates"


def _contains_explicit_secret(value: Any) -> bool:
    if isinstance(value, str):
        lowered = value.lower()
        if any(word in lowered for word in ["token", "secret", "password"]):
            return "$" not in value and "${{" not in value
    if isinstance(value, dict):
        return any(_contains_explicit_secret(v) for v in value.values())
    if isinstance(value, list):
        return any(_contains_explicit_secret(v) for v in value)
    return False


def validate_ci_file(path: Path) -> List[str]:
    issues: List[str] = []
    try:
        data = yaml.safe_load(path.read_text())
    except Exception as exc:  # pragma: no cover - error details useful in CLI
        return [f"{path}: YAML parse error: {exc}"]

    if not isinstance(data, dict):
        return [f"{path}: unexpected YAML structure"]

    # Simple schema expectations
    if "github" in str(path):
        if "jobs" not in data:
            issues.append(f"{path}: missing jobs section")
    if path.name.startswith(".gitlab-ci") or "gitlab" in str(path):
        if "stages" not in data:
            issues.append(f"{path}: missing stages")

    if _contains_explicit_secret(data):
        issues.append(f"{path}: potential hardcoded secret detected")
    return issues


def main() -> int:
    yaml_files = list(CI_ROOT.rglob("*.yml")) + list(CI_ROOT.rglob("*.yaml"))
    all_issues: List[str] = []
    for file in yaml_files:
        all_issues.extend(validate_ci_file(file))
    if all_issues:
        sys.stderr.write("\n".join(all_issues) + "\n")
        return 1
    print(f"Validated {len(yaml_files)} CI template files")
    return 0


if __name__ == "__main__":
    sys.exit(main())

