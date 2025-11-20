# 1С журнал регистрации

Пример экспортированной строки:
```
20.11.2023 10:01:22 INFO Event=UserLogin;user='ivanov';computer='ws-01';sess='123';app='thick';dur=42
```
Поля: `datetime`, `level`, `event`, `user`, `computer`, `session`, `app`, `duration_ms`. Лейблы: `service=onec`, `env`, `instance`.
