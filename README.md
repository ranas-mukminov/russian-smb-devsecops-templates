# DevSecOps templates for Russian SMB / DevSecOps шаблоны для малого бизнеса в РФ

[![CI](https://github.com/run-as-daemon/russian-smb-devsecops-templates/actions/workflows/ci.yml/badge.svg)](https://github.com/run-as-daemon/russian-smb-devsecops-templates/actions/workflows/ci.yml)
[![Security](https://github.com/run-as-daemon/russian-smb-devsecops-templates/actions/workflows/security.yml/badge.svg)](https://github.com/run-as-daemon/russian-smb-devsecops-templates/actions/workflows/security.yml)

## English

Open templates for Russian SMB teams who need logging and secure CI/CD without vendor lock-in. The repo ships two subsystems:
- `russian-smb-logging-stack`: turnkey Loki-first logging with ELK alternative, parsers for nginx, Bitrix/1C, mail, VPN, and ready Grafana/Kibana dashboards.
- `russian-smb-ci-security-templates`: GitHub Actions and GitLab CI pipelines with unit tests, linters, SAST, dependency and container scanning.

Getting started (short):
- Logging: `cd logging_stack/loki && docker compose -f docker-compose.loki.yml up -d`
- GitHub Actions: copy `ci_security_templates/github/<stack>/ci.yml` into `.github/workflows/`
- GitLab CI: include `ci_security_templates/gitlab/<stack>/.gitlab-ci.yml` in your project root.

More Russian context lives in the section below and in `README.ru.md`.

---

## Русский

Набор открытых DevSecOps-шаблонов для малого бизнеса в РФ. Две подсистемы:
- `russian-smb-logging-stack`: Loki как основной стек, ELK как альтернатива; парсеры под nginx, 1С, 1C-Bitrix, почту, VPN; готовые дашборды Grafana/Kibana и базовые алерты.
- `russian-smb-ci-security-templates`: готовые GitHub Actions и GitLab CI пайплайны с тестами, линтерами, SAST, сканированием зависимостей и контейнеров.

### Как использовать
- Запуск логирования: `cd logging_stack/loki && docker compose -f docker-compose.loki.yml up -d` (для ELK аналогично в `logging_stack/elk`).
- Подключение GitHub Actions: скопируйте нужный `ci.yml` в `.github/workflows/` своего проекта и настройте секреты (токены, реестры, URL).
- Подключение GitLab CI: возьмите `.gitlab-ci.yml` из папки вашего стека и подправьте переменные/регистры. Общие includes лежат в `ci_security_templates/gitlab/shared/includes/`.

### Профессиональные услуги – run-as-daemon.ru
Этот репозиторий развивается инженером DevOps/SRE с сайта [run-as-daemon.ru](https://run-as-daemon.ru).

Если вам нужно:
- внедрить централизованное логирование (nginx, 1С, Bitrix, почта, VPN);
- настроить безопасный CI/CD (тесты, линтеры, SAST, сканирование зависимостей и контейнеров);
- построить DevSecOps-процессы и обучить команду;

вы можете заказать консалтинг, внедрение и поддержку.

### Юр. оговорка
Шаблоны — ориентир, а не юридическая консультация. См. `LEGAL.md` для деталей использования и ограничений.

