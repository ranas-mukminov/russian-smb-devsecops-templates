# GitHub Actions — Python

- Jobs: `tests`, `lint` (ruff), `sast` (bandit), `deps-scan` (pip-audit), `container-scan` (Trivy).
- `needs` гарантирует запуск сканов только после успешных тестов.
- Настройте приватные индексы через `PIP_EXTRA_INDEX_URL` в Secrets при необходимости.
