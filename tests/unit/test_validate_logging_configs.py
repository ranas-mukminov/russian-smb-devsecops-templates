from pathlib import Path

from tools.validate_logging_configs import (
    validate_compose,
    validate_filebeat,
    validate_promtail,
)


def test_promtail_has_labels() -> None:
    path = Path("logging_stack/loki/promtail/promtail-config.yml")
    issues = validate_promtail(path)
    assert issues == []


def test_compose_services_present() -> None:
    loki_compose = Path("logging_stack/loki/docker-compose.loki.yml")
    elk_compose = Path("logging_stack/elk/docker-compose.elk.yml")
    assert validate_compose(loki_compose, ["loki", "promtail", "grafana"]) == []
    assert validate_compose(elk_compose, ["elasticsearch", "logstash", "kibana", "filebeat"]) == []


def test_filebeat_inputs_present() -> None:
    for fb in Path("logging_stack/elk/filebeat").glob("filebeat-*.yml"):
        assert validate_filebeat(fb) == []
