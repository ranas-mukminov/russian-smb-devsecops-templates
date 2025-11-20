# Postfix log pattern

Пример:
```
Nov 20 10:22:11 mail postfix/smtp[1523]: 7B4A51024: from=<noreply@example.ru>, to=<user@corp.ru>, relay=mx.corp.ru[10.0.0.5]:25, dsn=2.0.0, status=sent (250 OK)
```
Ключевые поля: `month`, `day`, `time`, `queue_id`, `from`, `to`, `relay`, `dsn`, `status`. Лейблы: `service=mail`, `env`, `instance`.
