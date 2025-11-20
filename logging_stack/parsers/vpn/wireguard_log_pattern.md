# WireGuard log pattern

Пример:
```
2023-11-20 10:40:11 [NET] peer(ABCD=) - Handshake did not complete within 5 seconds, retrying
```
Поля: `datetime`, `level`, `peer`, `message`, дополнительно `event` (handshake failure/established).
