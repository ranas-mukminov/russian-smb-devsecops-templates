# OpenVPN log pattern

Пример:
```
2023-11-20 10:33:55 TLS: tls_process: killed expiring key
2023-11-20 10:34:01 MANAGEMENT: Client connected from /var/run/openvpn.sock
2023-11-20 10:34:05 user1/203.0.113.10:55821 MULTI_sva: pool returned IPv4=10.8.0.10
```
Поля: `datetime`, `level`, `peer/user`, `remote_ip`, `message`, `event` (например, подключение, разрыв, повторное подключение).
