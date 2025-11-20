# router-policy-to-config

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![CI Status](https://github.com/ranas-mukminov/russian-smb-devsecops-templates/actions/workflows/ci.yml/badge.svg)](https://github.com/ranas-mukminov/russian-smb-devsecops-templates/actions/workflows/ci.yml)

## English

### What is this?

`router-policy-to-config` is an **AI-assisted copilot for router configuration** that transforms high-level YAML policies into vendor-specific router configurations. Instead of manually crafting hundreds of low-level CLI commands or navigating complex web interfaces, you describe your network intent in a simple, vendor-agnostic policy format, and the tool generates ready-to-use configurations for:

- **MikroTik RouterOS** (v6/v7) – complete `.rsc` scripts and exports
- **OpenWrt** – UCI configuration files (`/etc/config/network`, `wireless`, `firewall`, etc.)

The tool also provides:
- **Diff engine** – compare generated configs against your existing router configuration
- **Local test lab** – Docker/QEMU-based environment to safely validate configs before deploying to production
- **AI helpers** – convert natural language descriptions into policy YAML, generate additional test scenarios

### Supported platforms

- **RouterOS** (MikroTik routers and CHR)
  - PPPoE, DHCP, static WAN configurations
  - LAN/VLAN setup with bridges
  - Firewall rules and NAT
  - Wireless configuration (for devices with wireless capability)
  - VPN (WireGuard)

- **OpenWrt**
  - Network interfaces and bridges
  - PPPoE, DHCP, static WAN
  - Wireless APs and guest networks
  - Firewall zones, rules, and port forwarding
  - VPN integration

### Why?

Today, most network administrators configure routers via:

- **MikroTik Winbox/CLI** – directly typing RouterOS commands with complex syntax, managing interface names, VLANs, firewall chains manually ([RouterOS documentation](https://help.mikrotik.com/docs/spaces/ROS/pages/328151/First+Time+Configuration))
- **OpenWrt LuCI/UCI** – editing multiple interconnected configuration files with subtle interdependencies ([OpenWrt UCI system](https://openwrt.org/docs/guide-user/base-system/uci))

There is **no widely adopted, vendor-neutral policy format** that can be compiled into configurations for both platforms. This project aims to fill that gap by:

1. Defining a clear, human-readable **YAML policy schema**
2. Implementing **backends** that translate policy into vendor-specific configs
3. Providing **validation and diff tools** to prevent misconfigurations
4. Offering a **safe lab environment** to test changes before production deployment

### Features

✅ **Vendor-agnostic YAML policy**
- Define WAN settings (PPPoE, DHCP, static)
- Configure multiple LANs with DHCP ranges
- Set up guest networks with isolation
- Configure Wi-Fi access points
- Define VPN servers/clients (WireGuard)
- Specify firewall rules in intent-based format

✅ **Multi-vendor code generation**
- RouterOS `.rsc` scripts compatible with v6 and v7
- OpenWrt UCI configuration files ready to import

✅ **Configuration diff and planning**
- Compare generated config against existing router exports
- Show exactly what will change before applying
- Prevent accidental configuration overwrites

✅ **Local test lab**
- Docker Compose topology with RouterOS and OpenWrt nodes
- Automated connectivity tests
- Firewall behavior validation
- Guest network isolation verification
- Internet reachability checks

✅ **AI-powered helpers** (optional)
- Convert natural language descriptions into policy YAML
- Generate additional test scenarios based on your policy
- Suggest optimizations and best practices

### Quick start

#### Requirements

- **Python 3.10+**
- **Docker** and **Docker Compose** (for lab testing)
- **QEMU** (for RouterOS CHR in lab, optional)

#### Installation

```bash
# Clone the repository
git clone https://github.com/ranas-mukminov/russian-smb-devsecops-templates.git
cd russian-smb-devsecops-templates/router-policy-to-config

# Install the package
pip install -e .
```

#### Basic usage

**1. Create a policy file**

You can create one manually or use the interactive wizard:

```bash
router-policy init
```

Or create `policy.yaml` manually:

```yaml
meta:
  name: home-office-router
  description: PPPoE WAN, main LAN, guest Wi-Fi, remote VPN
  target:
    vendor: routeros
    version: v7

wan:
  type: pppoe
  interface: ether1
  username: "YOUR_ISP_USERNAME"
  password_ref: "secret:pppoe_password"

lans:
  - name: main
    subnet: 192.168.10.0/24
    gateway: 192.168.10.1
    dhcp:
      enabled: true
      range: 192.168.10.100-192.168.10.200

  - name: guest
    subnet: 192.168.20.0/24
    gateway: 192.168.20.1
    dhcp:
      enabled: true
      range: 192.168.20.50-192.168.20.150
    isolated_from:
      - main

wifi:
  - name: main-wifi
    lan: main
    ssid: "MyHome"
    mode: ap
    security:
      encryption: wpa2-psk
      password_ref: "secret:wifi_main_password"

  - name: guest-wifi
    lan: guest
    ssid: "MyHome-Guest"
    mode: ap
    security:
      encryption: wpa2-psk
      password_ref: "secret:wifi_guest_password"
    guest: true

firewall:
  rules:
    - name: allow_lan_to_internet
      from: [main]
      to: [wan]
      action: accept
    - name: block_guest_to_main
      from: [guest]
      to: [main]
      action: drop
```

**2. Set up secrets**

Export your secrets as environment variables (never commit them to Git):

```bash
export SECRET_PPPOE_PASSWORD="your_pppoe_password"
export SECRET_WIFI_MAIN_PASSWORD="your_wifi_password"
export SECRET_WIFI_GUEST_PASSWORD="guest_wifi_password"
```

**3. Validate your policy**

```bash
router-policy validate policy.yaml
```

**4. Generate configuration**

For RouterOS:
```bash
router-policy render policy.yaml --target routeros --out routeros-config.rsc
```

For OpenWrt:
```bash
router-policy render policy.yaml --target openwrt --out openwrt-config/
```

**5. Compare with existing config** (optional)

Get a diff to see what would change:

```bash
# For RouterOS
router-policy diff policy.yaml --target routeros --current current-export.rsc

# For OpenWrt
router-policy diff policy.yaml --target openwrt --current /path/to/etc/config
```

**6. Test in lab** (optional)

Run automated tests in a safe lab environment:

```bash
router-policy lab-test policy.yaml
```

**7. Generate policy from natural language** (AI helper)

```bash
router-policy ai-suggest --from-text "ISP via PPPoE on ether1, LAN 192.168.10.0/24, guest Wi-Fi, WireGuard VPN" --out policy.yaml
```

### How it works

```
┌─────────────────────┐
│   YAML Policy       │
│  (intent-based)     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Policy Validator   │
│  - Schema check     │
│  - Semantic rules   │
│  - Subnet overlaps  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Internal Model    │
│   (vendor-neutral)  │
└──────────┬──────────┘
           │
     ┌─────┴─────┐
     ▼           ▼
┌─────────┐ ┌──────────┐
│RouterOS │ │ OpenWrt  │
│Backend  │ │ Backend  │
└────┬────┘ └─────┬────┘
     │            │
     ▼            ▼
┌─────────┐ ┌──────────┐
│.rsc     │ │UCI files │
│script   │ │& commands│
└─────────┘ └──────────┘
```

The **diff engine** compares generated output with your existing router configuration, showing:
- Added commands/sections
- Removed commands/sections
- Modified values

The **lab environment** uses Docker containers and QEMU VMs to run actual RouterOS CHR and OpenWrt instances, allowing you to:
- Apply generated configs safely
- Run automated connectivity tests
- Verify firewall behavior
- Check guest network isolation
- Validate VPN functionality

### Security and limitations

#### What this tool does NOT do

❌ **Does not** automatically connect to or modify remote routers (in v1.0)  
❌ **Does not** scan, exploit, or attack third-party networks  
❌ **Does not** bypass ISP restrictions or provider limitations  
❌ **Does not** store credentials in Git or configuration files  

#### Intended use

✅ Configure routers and networks **you own or administrate**  
✅ Defensive security and operational automation  
✅ Learning and development in safe lab environments  
✅ Documentation and version control of network configurations  

#### Secret management

- Policies use **references** like `password_ref: "secret:key_name"`
- Actual secrets are loaded from:
  - Environment variables (`SECRET_KEY_NAME`)
  - External secret providers (documented in [Secret Management](docs/secrets.md))
  - Never stored in policy YAML files
  - Never committed to version control

#### Legal compliance

- Use only on networks and equipment you legally own or have permission to configure
- Respect MikroTik and OpenWrt licenses and terms of service
- RouterOS and MikroTik are trademarks of MikroTik Ltd.
- OpenWrt is a Linux-based open-source project
- Lab images are for **testing purposes only**, not production use

See [LEGAL.md](LEGAL.md) for detailed legal information.

### Professional services – run-as-daemon.ru

**This project is maintained by the DevSecOps / network engineering team behind [run-as-daemon.ru](https://run-as-daemon.ru).**

If you need help with:

- 🏗️ **Designing RouterOS + OpenWrt networks** "from policy, not CLI"
- 🔄 **Migrating existing routers** to policy-driven configuration management
- 🧪 **Building safe labs and CI pipelines** for router configuration testing
- 🔒 **Security hardening** of MikroTik and OpenWrt deployments
- 📚 **Training your team** on infrastructure-as-code for network devices
- 🚀 **Custom integrations** with your existing DevOps toolchain

**You can request consulting, implementation, and ongoing support at [run-as-daemon.ru](https://run-as-daemon.ru).**

We specialize in:
- Network automation for Russian SMB environments
- DevSecOps practices tailored to local infrastructure
- Russian-language documentation and support
- Compliance with Russian data protection requirements

### Architecture

The project consists of several key components:

1. **Policy schema** (`schema/`) – JSON Schema definitions for validation
2. **Core engine** (`src/router_policy_to_config/`)
   - Data models (Python dataclasses)
   - Policy loader and validator
   - Vendor backends (RouterOS, OpenWrt)
   - Diff engine
   - CLI interface
3. **AI providers** (`ai_providers/`) – pluggable AI integrations
4. **Lab environment** (`lab/`) – Docker Compose test topology
5. **Tests** (`tests/`) – comprehensive unit and integration tests
6. **Scripts** (`scripts/`) – automation for linting, security, performance

### Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Code style guidelines (Black, Ruff, isort)
- How to add new policy fields
- How to implement new vendor backends
- Testing requirements
- Pull request process

### Development setup

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linters
./scripts/lint.sh

# Run security checks
./scripts/security_scan.sh

# Format code
./scripts/format.sh
```

### Examples

See the `examples/` directory for sample policies:

- `examples/home-office.yaml` – Basic home office setup
- `examples/small-business.yaml` – Small business with multiple VLANs
- `examples/guest-wifi.yaml` – Guest Wi-Fi with isolation
- `examples/vpn-server.yaml` – WireGuard VPN server
- `examples/multi-wan.yaml` – Dual WAN with failover

### Roadmap

- [x] v0.1.0 – Initial release with RouterOS and OpenWrt support
- [ ] v0.2.0 – Enhanced VPN support (IPsec, OpenVPN)
- [ ] v0.3.0 – QoS and traffic shaping policies
- [ ] v0.4.0 – Multi-WAN and failover
- [ ] v0.5.0 – Remote router API integration
- [ ] v1.0.0 – Production-ready with full test coverage

### License

This project is licensed under the **Apache License 2.0**. See [LICENSE](../LICENSE) for details.

### Links

- **Project home**: [GitHub](https://github.com/ranas-mukminov/russian-smb-devsecops-templates)
- **Professional services**: [run-as-daemon.ru](https://run-as-daemon.ru)
- **Documentation**: [docs/](docs/)
- **Issue tracker**: [GitHub Issues](https://github.com/ranas-mukminov/russian-smb-devsecops-templates/issues)

---

## Русский (кратко)

### Что это?

`router-policy-to-config` — это **AI-помощник для настройки роутеров**, который превращает высокоуровневые YAML-политики в готовые конфигурации для MikroTik RouterOS и OpenWrt.

### Основные возможности

✅ **YAML-политика** – описываете намерение (PPPoE, LAN, гостевой Wi-Fi, VPN), а не команды  
✅ **Генерация конфигураций** – RouterOS `.rsc` скрипты и OpenWrt UCI файлы  
✅ **Diff с текущей конфигурацией** – показывает, что изменится перед применением  
✅ **Локальная лаборатория** – тестируйте конфиги в Docker/QEMU перед применением на реальных роутерах  
✅ **AI-помощники** – генерация политик из текста, предложение дополнительных тестов  

### Быстрый старт

```bash
# Установка
pip install -e .

# Создание политики
router-policy init

# Валидация
router-policy validate policy.yaml

# Генерация конфигурации
router-policy render policy.yaml --target routeros --out routeros-config.rsc

# Сравнение с текущей конфигурацией
router-policy diff policy.yaml --target routeros --current current-export.rsc

# Тестирование в лаборатории
router-policy lab-test policy.yaml
```

### Безопасность и законность

- ✅ Используйте только на своих роутерах и сетях
- ✅ Секреты хранятся в переменных окружения, не в Git
- ✅ Лабораторные образы только для тестирования
- ❌ Не предназначен для взлома или атак на чужие роутеры
- ❌ Не обходит ограничения провайдеров

Подробности в [LEGAL.md](LEGAL.md).

### Профессиональные услуги – run-as-daemon.ru

**Проект развивается командой DevSecOps-инженеров с сайта [run-as-daemon.ru](https://run-as-daemon.ru).**

Если вам нужно:

- 🏗️ **Спроектировать сети RouterOS + OpenWrt** "из политик, а не из CLI"
- 🔄 **Перевести существующие роутеры** на управление через политики
- 🧪 **Построить безопасные лаборатории и CI-пайплайны** для тестирования конфигов
- 🔒 **Усилить защиту** MikroTik и OpenWrt
- 📚 **Обучить команду** инфраструктуре-как-коду для сетевого оборудования
- 🚀 **Интегрировать** с вашими DevOps-инструментами

**Заказать консалтинг, внедрение и поддержку можно на [run-as-daemon.ru](https://run-as-daemon.ru).**

Мы специализируемся на:
- Автоматизации сетей для российского малого бизнеса
- DevSecOps-практиках для локальной инфраструктуры
- Документации и поддержке на русском языке
- Соответствии требованиям защиты данных в РФ

### Лицензия

Проект распространяется под лицензией **Apache 2.0**. См. [LICENSE](../LICENSE).

### Ссылки

- **Проект**: [GitHub](https://github.com/ranas-mukminov/russian-smb-devsecops-templates)
- **Услуги**: [run-as-daemon.ru](https://run-as-daemon.ru)
- **Документация**: [docs/](docs/)
