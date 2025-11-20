# GitHub Actions — Node.js

Jobs: `tests`, `lint`, `deps-scan`, `container-scan`. Все идут после тестов, чтобы экономить время. Используются `npm ci`, `npm audit --production`, ESLint и Trivy.

Параметры:
- `node-version` можно менять в workflow.
- Для приватных реестров настройте `NPM_TOKEN` в Secrets.
