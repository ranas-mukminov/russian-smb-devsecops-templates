# GitHub Actions — PHP/Bitrix

Русский:
- Jobs: `php-tests`, `php-lint`, `php-sast`, `dependencies-scan`, `container-scan`.
- Порядок: тесты -> линт/SAST/зависимости -> контейнерный скан (Trivy) после успешных проверок.
- Требуются: `composer.json`, при необходимости docker build-контекст.

English (short):
- Provides basic CI with tests, lint, SAST (phpstan/psalm), dependency audit and Trivy image scan.
- Use GitHub Secrets for private registries (e.g., `REGISTRY_USER`, `REGISTRY_PASSWORD`).
