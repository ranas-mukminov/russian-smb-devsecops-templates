import yaml
from pathlib import Path


def test_github_php_bitrix_jobs_structure() -> None:
    data = yaml.safe_load(Path("ci_security_templates/github/php_bitrix/ci.yml").read_text())
    jobs = data.get("jobs", {})
    for job in ["php-tests", "php-lint", "php-sast", "dependencies-scan", "container-scan"]:
        assert job in jobs
    # container-scan should depend on previous checks
    needs = jobs["container-scan"].get("needs", [])
    assert set(needs) >= {"php-tests", "php-lint", "php-sast", "dependencies-scan"}
