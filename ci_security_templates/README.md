# CI/CD security templates

Готовые пайплайны GitHub Actions и GitLab CI для PHP/Bitrix, Python, Node. Все шаблоны включают тесты, линтеры, SAST, проверку зависимостей и Trivy для контейнеров. Подробности в README внутри каждой папки.

## Состав
- `github/` — workflows и composite actions.
- `gitlab/` — примеры .gitlab-ci.yml и shared includes.
- `ai_pipeline_helpers/` — интерфейсы для генерации черновиков пайплайнов с помощью внешнего ИИ (без ключей!).

Используйте секреты/переменные CI для токенов/регистров. Не храните ключи в репозитории.
