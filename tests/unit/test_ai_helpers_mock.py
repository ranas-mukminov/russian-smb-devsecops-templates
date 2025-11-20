from logging_stack.ai_helpers.base import MockProvider
from logging_stack.ai_helpers.log_parser_suggestions import propose_parser_pipeline
from logging_stack.ai_helpers.incident_description import build_incident_description
from ci_security_templates.ai_pipeline_helpers.pipeline_generator import (
    generate_github_pipeline,
    generate_gitlab_pipeline,
)


def test_mock_provider_generates_strings() -> None:
    provider = MockProvider()
    parser = propose_parser_pipeline("10.0.0.1 - - [date] \"GET /\" 200", provider)
    assert isinstance(parser, str)
    incident = build_incident_description([
        {"timestamp": "now", "service": "web", "message": "500 spike"}
    ], provider)
    assert "mock" in incident


def test_pipeline_generators_return_yaml_string() -> None:
    provider = MockProvider()
    gh = generate_github_pipeline({"language": "python"}, provider)
    gl = generate_gitlab_pipeline({"language": "php"}, provider)
    assert gh.startswith("mock") and gl.startswith("mock")
