# nginx access/error log pattern

Пример строки access:
```
192.168.0.10 - - [20/Nov/2023:10:15:22 +0300] "GET /health HTTP/1.1" 200 12 "-" "curl/7.68.0" 0.003
```
Ключевые поля: `remote_addr`, `time_local`, `request`, `status`, `body_bytes_sent`, `http_referer`, `http_user_agent`, `request_time`.
Рекомендуемые лейблы: `job=nginx`, `service=web`, `env`, `instance`.
