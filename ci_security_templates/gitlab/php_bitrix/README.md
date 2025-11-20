# GitLab CI — PHP/Bitrix

- Стадии: test, lint, sast, deps, container_scan, deploy (опционально).
- Подключает общие includes для SAST, dependency scan и container scan.
- Использует composer install, phpstan, composer audit, Trivy для образа.
- Настройте `CI_REGISTRY_IMAGE` и логин к реестру через CI variables.
