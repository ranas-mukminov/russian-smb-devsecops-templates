# GitLab CI — Node.js

- Стадии: test, lint, deps, container_scan.
- Инструменты: npm test, ESLint, npm audit, Trivy.
- Для приватного реестра используйте переменные `CI_REGISTRY_USER`/`CI_REGISTRY_PASSWORD`.
