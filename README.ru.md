# DevSecOps шаблоны для малого бизнеса в РФ

Репозиторий `russian-smb-devsecops-templates` — открытая коллекция логирования и безопасных CI/CD пайплайнов под российские реалии (nginx, 1С, 1C-Bitrix, почта, VPN).

## Состав
- `russian-smb-logging-stack`: Loki (основной) + ELK (альтернатива), парсеры и дашборды.
- `russian-smb-ci-security-templates`: GitHub Actions и GitLab CI для PHP/Bitrix, Python, Node с тестами, линтерами, SAST, dependency scan, container scan.
- `tools/`, `tests/`, `scripts/`: валидация конфигов, проверки безопасности и производительности для самого репозитория.

## Быстрый старт
1. Логирование (Loki):
   ```bash
   cd logging_stack/loki
   docker compose -f docker-compose.loki.yml up -d
   ```
   Grafana доступна на `http://localhost:3000` (логин/пароль по умолчанию admin/admin; поменяйте сразу).

2. GitHub Actions:
   - Скопируйте `ci_security_templates/github/<язык>/ci.yml` в `.github/workflows/` вашего проекта.
   - Настройте секреты (токены, реестры, приватные зависимости) через GitHub Secrets.

3. GitLab CI:
   - Возьмите `.gitlab-ci.yml` из `ci_security_templates/gitlab/<язык>/`.
   - При необходимости подключите include из `ci_security_templates/gitlab/shared/includes/`.

## Особенности
- Все комментарии и документация содержат русские пояснения.
- Стек не содержит закрытых ключей или токенов; используйте переменные окружения/Secrets.
- AI-helpers — интерфейсы без привязки к провайдеру, пригодные для генерации черновиков парсеров и пайплайнов.

## Услуги — run-as-daemon.ru
Проект поддерживается инженером DevOps/SRE с сайта [run-as-daemon.ru](https://run-as-daemon.ru). Если нужно внедрение логирования, настройка безопасного CI/CD или обучение команды — обращайтесь.

## Юр. сведения
Шаблоны предоставляются «как есть» по Apache-2.0. Проект не является официальным продуктом 1С, 1C-Bitrix, GitHub, GitLab, Elastic, Grafana и др. Подробнее в `LEGAL.md`.

