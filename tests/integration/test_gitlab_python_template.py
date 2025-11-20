import yaml
from pathlib import Path


def test_gitlab_python_structure() -> None:
    data = yaml.safe_load(Path("ci_security_templates/gitlab/python/.gitlab-ci.yml").read_text())
    stages = data.get("stages")
    assert stages == ["test", "lint", "sast", "deps", "container_scan"]

    for job in ["python_tests", "python_lint", "python_sast", "python_deps_scan", "python_container_scan"]:
        assert job in data

    needs = data["python_container_scan"].get("needs", [])
    assert "python_tests" in needs
    assert "python_lint" in needs
    assert "python_sast" in needs
    assert "python_deps_scan" in needs
