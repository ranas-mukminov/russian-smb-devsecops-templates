# Bitrix PHP-FPM log pattern

Пример:
```
[2023/11/20 09:12:45] [ERROR] pid 1234: PHP Fatal error: Call to undefined function in /var/www/bitrix/index.php on line 42 client: 10.0.0.1
```
Поля: `datetime`, `level`, `pid`, `message`, `client_ip`. Дополнительно выделяйте `script`, `line` при помощи grok/regex при необходимости.
