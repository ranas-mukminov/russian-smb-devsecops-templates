# Russian SMB Logging Stack

Готовый стек логирования «из коробки» для малого бизнеса в РФ. Основной вариант — Loki+Promtail+Grafana, альтернатива — ELK (Elasticsearch, Logstash, Kibana, Filebeat).

## Что входит
- docker-compose для Loki (`docker-compose.loki.yml`) и ELK (`docker-compose.elk.yml`).
- Конфиги Promtail/Filebeat/Logstash с пайплайнами под nginx, Bitrix, 1С, почту, VPN.
- Дашборды Grafana и объекты Kibana с русскими заголовками.
- Базовые алерты по типичным инцидентам (рост 5xx, ошибки авторизации, проблемы VPN/1С).

## Быстрый старт (Loki)
```bash
cd logging_stack/loki
docker compose -f docker-compose.loki.yml up -d
```
Ожидается, что логи nginx/Bitrix/1C/mail/VPN смонтированы в контейнер Promtail и размечены лейблами `job`, `app`, `instance`, `service`, `env`.

## Альтернатива ELK
```bash
cd logging_stack/elk
docker compose -f docker-compose.elk.yml up -d
```
Filebeat читает те же пути логов и отправляет их в Logstash, который нормализует поля и пишет в Elasticsearch.

