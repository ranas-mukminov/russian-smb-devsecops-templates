# GitLab CI — Python

- Stages: test, lint, sast, deps, container_scan.
- Tools: pytest, ruff, bandit, pip-audit, Trivy.
- Зависимости ставятся из `requirements.txt`; при отсутствии файл шаги пропускаются.
- Контейнерный скан использует DinD, убедитесь, что проекту разрешено пользоваться сервисом docker.
