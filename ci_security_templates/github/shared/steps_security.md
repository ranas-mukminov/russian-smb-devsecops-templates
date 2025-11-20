# Безопасные шаги CI/CD (GitHub Actions)

- Тесты и линтеры запускаются перед SAST и сканерами зависимостей, чтобы быстро ловить базовые ошибки.
- SAST: используйте язык-специфичные анализаторы (phpstan/psalm, bandit, eslint security plugins).
- Dependency scanning: `pip-audit`, `npm audit --production`, `composer audit`.
- Container scanning: Trivy образа приложения и Dockerfile. Кэшируйте базы через volume или `--cache-dir`.
- Secrets: используйте `secrets.GITHUB_TOKEN` и собственные Secrets для приватных реестров. Не логируйте секреты.
- Порядок зависит от `needs`: сканы идут после успешных тестов, чтобы не тратить ресурсы на упавшие сборки.
