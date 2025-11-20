from pathlib import Path

import pytest

from tools.validate_ci_templates import validate_ci_file


@pytest.mark.parametrize("path", list(Path("ci_security_templates").rglob("*.yml")))
def test_ci_templates_yaml_is_valid(path: Path) -> None:
    issues = validate_ci_file(path)
    assert issues == [], f"{path} has issues: {issues}"
