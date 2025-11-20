from __future__ import annotations

import sys
from pathlib import Path
from typing import List

import yaml

ROOT = Path(__file__).resolve().parents[1]
LOGGING_ROOT = ROOT / "logging_stack"


def _load_yaml(path: Path):
    try:
        return yaml.safe_load(path.read_text())
    except Exception as exc:  # pragma: no cover
        raise ValueError(f"{path}: YAML parse error: {exc}") from exc


def validate_promtail(path: Path) -> List[str]:
    issues: List[str] = []
    data = _load_yaml(path)
    scrape_configs = data.get("scrape_configs", []) if isinstance(data, dict) else []
    if not scrape_configs:
        issues.append(f"{path}: empty scrape_configs")
    for cfg in scrape_configs:
        labels = cfg.get("static_configs", [{}])[0].get("labels", {})
        for key in ["job", "service", "env"]:
            if not labels.get(key):
                issues.append(f"{path}: missing label {key} in {cfg.get('job_name')}")
    return issues


def validate_compose(path: Path, expected_services: List[str]) -> List[str]:
    issues: List[str] = []
    data = _load_yaml(path)
    services = data.get("services", {}) if isinstance(data, dict) else {}
    for name in expected_services:
        if name not in services:
            issues.append(f"{path}: service {name} missing")
    return issues


def validate_filebeat(path: Path) -> List[str]:
    issues: List[str] = []
    data = _load_yaml(path)
    inputs = data.get("filebeat.inputs", []) if isinstance(data, dict) else []
    if not inputs:
        issues.append(f"{path}: filebeat.inputs is empty")
    for item in inputs:
        if not item.get("paths"):
            issues.append(f"{path}: missing paths in input {item.get('id')}")
    return issues


def main() -> int:
    issues: List[str] = []
    issues += validate_compose(LOGGING_ROOT / "loki" / "docker-compose.loki.yml", ["loki", "promtail", "grafana"])
    issues += validate_compose(LOGGING_ROOT / "elk" / "docker-compose.elk.yml", ["elasticsearch", "logstash", "kibana", "filebeat"])
    issues += validate_promtail(LOGGING_ROOT / "loki" / "promtail" / "promtail-config.yml")
    for fb in (LOGGING_ROOT / "elk" / "filebeat").glob("filebeat-*.yml"):
        issues += validate_filebeat(fb)
    if issues:
        sys.stderr.write("\n".join(issues) + "\n")
        return 1
    print("Logging configs validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())

