# 🛡️ DevSecOps Templates for Russian SMB

[![CI](https://github.com/ranas-mukminov/russian-smb-devsecops-templates/actions/workflows/ci.yml/badge.svg)](https://github.com/ranas-mukminov/russian-smb-devsecops-templates/actions/workflows/ci.yml)
[![Security](https://github.com/ranas-mukminov/russian-smb-devsecops-templates/actions/workflows/security.yml/badge.svg)](https://github.com/ranas-mukminov/russian-smb-devsecops-templates/actions/workflows/security.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

🇬🇧 English | 🇷🇺 [Русская версия](README.ru.md)

## Overview

Production-ready DevSecOps templates designed specifically for small and medium business (SMB) teams in Russia. This repository provides two core subsystems: a comprehensive logging stack tailored for common Russian business software (nginx, 1C, 1C-Bitrix, mail servers, VPN), and secure CI/CD pipeline templates with built-in security scanning. Both subsystems are vendor-neutral, open-source, and require no proprietary licenses or cloud vendor lock-in.

The project addresses the real-world challenges Russian SMB DevOps teams face: centralized logging for heterogeneous stacks, compliance-ready audit trails, and automated security testing without expensive commercial tools.

## Key Features

- **Turnkey logging with Loki or ELK**: Docker Compose stacks for Loki+Promtail+Grafana or Elasticsearch+Logstash+Kibana+Filebeat
- **Russian business software parsers**: Pre-configured log pipelines for nginx, 1C, 1C-Bitrix, Postfix/Dovecot mail servers, and OpenVPN
- **Production-ready Grafana dashboards**: Visualizations with Russian labels for web traffic, errors, auth failures, VPN sessions, and 1C performance
- **Secure CI/CD templates**: GitHub Actions and GitLab CI pipelines with unit tests, linters, SAST (Bandit, Semgrep), dependency scanning (pip-audit, npm audit), and container security (Trivy)
- **Multi-language support**: Templates for PHP/1C-Bitrix, Python, and Node.js projects
- **Vendor-neutral architecture**: No cloud platform dependencies; run on-premises or any cloud provider
- **AI-assisted configuration helpers**: Optional interfaces for generating custom parsers and pipelines using external AI APIs (bring your own API key)
- **Bilingual documentation**: All configs and dashboards include Russian comments and labels

## Architecture / Components

The repository consists of two independent subsystems that can be deployed separately or together:

### Logging Stack (`logging_stack/`)

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Log Sources   │────▶│  Loki/ELK Stack │────▶│  Grafana/Kibana │
│ (nginx, 1C,     │     │  (Promtail/     │     │   (Dashboards)  │
│  Bitrix, VPN)   │     │   Filebeat)     │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

- **Loki variant**: Grafana Loki 2.9.4, Promtail 2.9.4, Grafana 10.1.5
- **ELK variant**: Elasticsearch 8.x, Logstash 8.x, Kibana 8.x, Filebeat 8.x
- **Parsers**: Grok/LogQL pipelines for access logs, error logs, application logs
- **Dashboards**: Pre-built visualizations for traffic analysis, error tracking, security events

### CI Security Templates (`ci_security_templates/`)

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Source Code    │────▶│  CI Pipeline    │────▶│  Secure Build   │
│  (PHP/Py/Node)  │     │ (Tests, SAST,   │     │  + Container    │
│                 │     │  Dependency     │     │  Registry       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

- **GitHub Actions workflows**: Composite actions and reusable workflows for PHP/Bitrix, Python, Node.js
- **GitLab CI templates**: `.gitlab-ci.yml` examples and shared includes for multi-stage pipelines
- **Security stages**: Static analysis (Bandit, Semgrep), dependency auditing (pip-audit, npm audit), container scanning (Trivy)
- **Quality checks**: Code linting (Ruff, ESLint, PHPStan), unit tests (PHPUnit, pytest, Jest)

Both subsystems use Docker Compose for local/on-premises deployment and require no external SaaS dependencies.

## Requirements

### Operating System
- **Linux distributions**: Ubuntu 20.04/22.04 LTS, Debian 11/12, RHEL 8/9, Rocky Linux 8/9, Alma Linux 8/9
- **Kernel**: 4.15+ (for container support)
- **Architecture**: x86_64 (amd64)

### System Resources
- **CPU**: Minimum 2 cores (4+ recommended for ELK stack)
- **RAM**: 
  - Loki stack: 4 GB minimum, 8 GB recommended
  - ELK stack: 8 GB minimum, 16 GB recommended
- **Disk**: 50 GB free space minimum for log retention (adjust based on retention policy)

### Software Dependencies
- **Docker**: 20.10+ 
- **Docker Compose**: 2.0+ (bundled with Docker Desktop or install separately)
- **Python**: 3.10+ (for validation and helper tools)
- **Git**: 2.30+ (for cloning repository)

### Network & Access
- **Ports**: 3000 (Grafana), 3100 (Loki), 5601 (Kibana), 9200 (Elasticsearch)
- **Permissions**: sudo/root access for Docker installation and log directory mounts
- **Internet access**: Required for pulling Docker images from Docker Hub and Grafana registry

### Optional for CI/CD Templates
- **GitHub account** or **GitLab instance** (self-hosted or GitLab.com)
- **Container registry**: Docker Hub, GitHub Container Registry, GitLab Registry, or private registry

## Quick Start (TL;DR)

### Logging Stack (Loki + Grafana)

```bash
# 1. Clone the repository
git clone https://github.com/ranas-mukminov/russian-smb-devsecops-templates.git
cd russian-smb-devsecops-templates

# 2. Navigate to Loki stack
cd logging_stack/loki

# 3. Create log directories (or adjust paths in docker-compose.loki.yml)
sudo mkdir -p /var/log/{nginx,bitrix,onec,mail,vpn}
sudo chmod 755 /var/log/{nginx,bitrix,onec,mail,vpn}

# 4. Start the stack
docker compose -f docker-compose.loki.yml up -d

# 5. Access Grafana
# Open http://localhost:3000 in browser
# Default credentials: admin / admin (change immediately!)
```

### CI/CD Pipeline (GitHub Actions)

```bash
# 1. Copy the appropriate workflow template to your project
cp ci_security_templates/github/python/ci.yml <YOUR_PROJECT>/.github/workflows/

# 2. Configure GitHub Secrets in your repository settings:
# - PYPI_TOKEN (if publishing packages)
# - DOCKER_USERNAME, DOCKER_PASSWORD (for container builds)
# - Any custom secrets for your infrastructure

# 3. Push to GitHub - the workflow runs automatically on push/PR
git add .github/workflows/ci.yml
git commit -m "Add secure CI pipeline"
git push
```

### CI/CD Pipeline (GitLab CI)

```bash
# 1. Copy the appropriate template to your project root
cp ci_security_templates/gitlab/python/.gitlab-ci.yml <YOUR_PROJECT>/

# 2. Configure GitLab CI/CD Variables in project settings:
# - CI_REGISTRY_USER, CI_REGISTRY_PASSWORD (for container builds)
# - Any custom variables for your infrastructure

# 3. Push to GitLab - the pipeline runs automatically
git add .gitlab-ci.yml
git commit -m "Add secure CI pipeline"
git push
```

## Detailed Installation

### Install Logging Stack on Ubuntu / Debian

#### Prerequisites

```bash
# Update package index
sudo apt update

# Install Docker
sudo apt install -y docker.io docker-compose-plugin

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group (logout/login required)
sudo usermod -aG docker $USER
```

#### Deploy Loki Stack

```bash
# Clone repository
git clone https://github.com/ranas-mukminov/russian-smb-devsecops-templates.git
cd russian-smb-devsecops-templates/logging_stack/loki

# Review and customize docker-compose.loki.yml
# - Adjust log source paths (/var/log/nginx, /var/log/bitrix, etc.)
# - Change default Grafana admin password in environment section
# - Configure volume mounts for your infrastructure

# Create required log directories
sudo mkdir -p /var/log/{nginx,bitrix,onec,mail,vpn}
sudo chmod -R 755 /var/log/{nginx,bitrix,onec,mail,vpn}

# Start the stack
docker compose -f docker-compose.loki.yml up -d

# Verify all containers are running
docker compose -f docker-compose.loki.yml ps

# Check logs for any errors
docker compose -f docker-compose.loki.yml logs
```

#### Deploy ELK Stack (Alternative)

```bash
cd logging_stack/elk

# Increase vm.max_map_count for Elasticsearch (required)
sudo sysctl -w vm.max_map_count=262144
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf

# Review and customize docker-compose.elk.yml
# Start the stack
docker compose -f docker-compose.elk.yml up -d

# Wait for Elasticsearch to initialize (check with docker logs)
docker compose -f docker-compose.elk.yml logs elasticsearch

# Access Kibana at http://localhost:5601
```

### Install on RHEL / Rocky / Alma Linux

```bash
# Install Docker
sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER

# Continue with Loki or ELK deployment as above
```

### Install CI/CD Templates

CI/CD templates do not require installation - they are copied directly into your project repository. See Configuration section for details on customizing templates.

## Configuration

### Logging Stack Configuration

#### Loki + Promtail

Edit `logging_stack/loki/promtail/promtail-config.yml` to configure log sources:

```yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  # Nginx access logs
  - job_name: nginx-access
    static_configs:
      - targets:
          - localhost
        labels:
          job: nginx
          __path__: /var/log/nginx/access.log
    pipeline_stages:
      - match:
          selector: '{job="nginx"}'
          stages:
            - regex:
                expression: '^(?P<remote_addr>[\w\.]+) - (?P<remote_user>.*) \[(?P<time_local>.*)\] "(?P<method>\w+) (?P<request>.*) (?P<protocol>.*)" (?P<status>\d+) (?P<body_bytes_sent>\d+) "(?P<http_referer>.*)" "(?P<http_user_agent>.*)"'
            - labels:
                method:
                status:
```

Adjust `__path__` to match your actual log file locations.

#### Grafana Datasources

Loki is automatically configured as a datasource. To add custom datasources, edit `logging_stack/grafana/provisioning/datasources/loki.yml`.

#### Environment Variables

Key configuration via `docker-compose.loki.yml`:

```yaml
# Grafana admin credentials (CHANGE IMMEDIATELY)
GF_SECURITY_ADMIN_USER: admin
GF_SECURITY_ADMIN_PASSWORD: <YOUR_SECURE_PASSWORD>

# Optional: SMTP for alerting
# GF_SMTP_ENABLED: true
# GF_SMTP_HOST: <YOUR_SMTP_SERVER>:587
# GF_SMTP_USER: <YOUR_SMTP_USER>
# GF_SMTP_PASSWORD: <YOUR_SMTP_PASSWORD>
```

### CI/CD Templates Configuration

#### GitHub Actions (Python Example)

Edit `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: ["main", "master"]
  pull_request:
    branches: ["main", "master"]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install ruff bandit
      - name: Run Ruff
        run: ruff check .
      - name: Run Bandit (SAST)
        run: bandit -r src/

  test:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -e .
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest --cov=src tests/

  security:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Dependency audit
        run: |
          pip install pip-audit
          pip-audit
```

Required secrets (configure in GitHub repository settings):
- `PYPI_TOKEN` - for publishing packages
- `DOCKER_USERNAME`, `DOCKER_PASSWORD` - for container registry authentication

#### GitLab CI (Python Example)

Edit `.gitlab-ci.yml`:

```yaml
stages:
  - lint
  - test
  - security
  - build

variables:
  PYTHON_VERSION: "3.11"

lint:
  stage: lint
  image: python:${PYTHON_VERSION}
  script:
    - pip install ruff
    - ruff check .

test:
  stage: test
  image: python:${PYTHON_VERSION}
  script:
    - pip install -e .
    - pip install pytest pytest-cov
    - pytest --cov=src tests/

security:sast:
  stage: security
  image: python:${PYTHON_VERSION}
  script:
    - pip install bandit
    - bandit -r src/

security:dependencies:
  stage: security
  image: python:${PYTHON_VERSION}
  script:
    - pip install pip-audit
    - pip-audit

security:container:
  stage: security
  image: aquasec/trivy:latest
  script:
    - trivy image <YOUR_IMAGE_NAME>
```

Required GitLab CI/CD variables:
- `CI_REGISTRY_USER`, `CI_REGISTRY_PASSWORD` - for GitLab Container Registry
- Custom variables for your infrastructure

## Usage & Common Tasks

### Accessing Web Interfaces

#### Grafana (Loki Stack)
- **URL**: `http://<YOUR_SERVER_IP>:3000`
- **Default credentials**: `admin` / `admin` (change on first login)
- **Dashboards**: Navigate to "Dashboards" → "Browse" → Select pre-imported dashboards

#### Kibana (ELK Stack)
- **URL**: `http://<YOUR_SERVER_IP>:5601`
- **No authentication by default** (configure X-Pack security for production)
- **Index patterns**: Auto-created for `logstash-*` indices

### Managing Logging Stack

#### Start/Stop Services

```bash
# Start Loki stack
cd logging_stack/loki
docker compose -f docker-compose.loki.yml up -d

# Stop Loki stack
docker compose -f docker-compose.loki.yml down

# Restart a specific service
docker compose -f docker-compose.loki.yml restart grafana

# View service logs
docker compose -f docker-compose.loki.yml logs -f promtail
```

#### Import Custom Grafana Dashboards

```bash
# Place dashboard JSON in logging_stack/grafana/dashboards/
cp my-custom-dashboard.json logging_stack/grafana/dashboards/

# Restart Grafana to load dashboard
docker compose -f docker-compose.loki.yml restart grafana

# Or import via Grafana UI: Dashboards → Import → Upload JSON file
```

#### Query Logs with LogQL (Loki)

Access Grafana → Explore, then use LogQL queries:

```logql
# All nginx 5xx errors in last hour
{job="nginx"} |= "status=5" | logfmt | status >= 500

# Failed SSH login attempts
{job="auth"} |= "Failed password"

# 1C errors
{job="onec"} |~ "error|exception" | line_format "{{.timestamp}} {{.message}}"
```

### Using CI/CD Templates

#### Running Workflows Locally (GitHub Actions)

```bash
# Install act (GitHub Actions local runner)
# https://github.com/nektos/act
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Run workflow locally
cd <YOUR_PROJECT>
act -j lint  # Run specific job
```

#### Testing GitLab CI Locally

```bash
# Install gitlab-runner
# https://docs.gitlab.com/runner/install/
curl -L https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh | sudo bash
sudo apt install gitlab-runner

# Validate .gitlab-ci.yml syntax
gitlab-runner exec shell lint
```

#### Customizing Security Scans

Add custom Bandit configuration (`.bandit`):

```ini
[bandit]
exclude_dirs = /test,/tests,/venv
skips = B404,B603
```

Add Trivy ignore file (`.trivyignore`):

```text
# Ignore specific CVEs
CVE-2023-12345

# Ignore low severity
LOW
```

## Update / Upgrade

### Updating Logging Stack

```bash
cd logging_stack/loki

# Pull latest images
docker compose -f docker-compose.loki.yml pull

# Recreate containers with new images
docker compose -f docker-compose.loki.yml up -d

# Verify all services are healthy
docker compose -f docker-compose.loki.yml ps
```

### Updating CI/CD Templates

```bash
# Pull latest template repository
cd russian-smb-devsecops-templates
git pull origin main

# Review changes
git log --oneline

# Copy updated templates to your project
# REVIEW CHANGES BEFORE OVERWRITING
diff ci_security_templates/github/python/ci.yml <YOUR_PROJECT>/.github/workflows/ci.yml

# Manually merge changes or replace template
cp ci_security_templates/github/python/ci.yml <YOUR_PROJECT>/.github/workflows/
```

### Breaking Changes

Check `CHANGELOG.md` for breaking changes between versions. Major updates may require:
- Configuration file migrations
- Database schema updates (for ELK stack)
- Secret key regeneration
- Dashboard re-imports

## Logs, Monitoring, Troubleshooting

### Viewing Logs

#### Docker Logs

```bash
# View all container logs
docker compose -f docker-compose.loki.yml logs

# Follow specific service logs
docker compose -f docker-compose.loki.yml logs -f promtail

# View last 100 lines
docker compose -f docker-compose.loki.yml logs --tail=100 loki
```

#### Systemd Logs (if running Docker via systemd)

```bash
# Docker daemon logs
sudo journalctl -u docker -f

# Check Docker service status
sudo systemctl status docker
```

### Common Issues & Solutions

#### Grafana: "Data source not found"

**Problem**: Loki datasource is not auto-configured.

**Solution**:
```bash
# Check Loki is running and accessible
curl http://localhost:3100/ready

# Manually add datasource: Grafana UI → Configuration → Data Sources → Add Loki
# URL: http://loki:3100
```

#### Promtail: "permission denied" reading log files

**Problem**: Promtail container cannot access host log files.

**Solution**:
```bash
# Fix log file permissions
sudo chmod 644 /var/log/nginx/*.log

# Or add Promtail user to log group
sudo usermod -aG adm <PROMTAIL_USER>

# Adjust SELinux context (RHEL/CentOS)
sudo chcon -R -t svirt_sandbox_file_t /var/log/nginx/
```

#### Port 3000 already in use

**Problem**: Another service is using Grafana's port.

**Solution**:
```bash
# Identify process using port 3000
sudo lsof -i :3000

# Kill conflicting process or change Grafana port in docker-compose.loki.yml:
# ports:
#   - "3001:3000"  # Map to host port 3001 instead
```

#### Elasticsearch fails to start: "max virtual memory areas too low"

**Problem**: Linux kernel vm.max_map_count is too low.

**Solution**:
```bash
sudo sysctl -w vm.max_map_count=262144
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
```

#### CI pipeline fails with "pip-audit not found"

**Problem**: pip-audit not installed in CI environment.

**Solution**: Ensure installation step exists in workflow:
```yaml
- name: Install pip-audit
  run: pip install pip-audit
```

#### No data in Grafana dashboards

**Problem**: Logs are not being ingested.

**Solution**:
```bash
# Check Promtail targets are active
curl http://localhost:9080/targets  # Promtail metrics endpoint

# Verify log files exist and are readable
ls -la /var/log/nginx/

# Check Promtail logs for errors
docker compose -f docker-compose.loki.yml logs promtail | grep -i error
```

## Security Notes

### Essential Security Checklist

- [ ] **Change default passwords**: Grafana admin password must be changed immediately after first login
- [ ] **Restrict network access**: Use firewall rules (ufw, firewalld) to limit access to ports 3000, 3100, 5601, 9200 to trusted IPs only
- [ ] **Enable HTTPS**: Use reverse proxy (nginx, Traefik) with Let's Encrypt SSL certificates for web interfaces
- [ ] **Secure Docker socket**: Do not expose Docker socket (/var/run/docker.sock) to containers unless absolutely necessary
- [ ] **Secrets management**: Never commit passwords, API keys, or tokens to Git; use environment variables or CI/CD secrets
- [ ] **Log access control**: Ensure log files on host contain no sensitive data (credit cards, passwords); use parsers to redact if needed
- [ ] **Regular updates**: Keep Docker images updated; subscribe to security advisories for Grafana, Loki, Elasticsearch
- [ ] **Audit logs**: Enable audit logging in Grafana and review access patterns regularly
- [ ] **VPN or private network**: For production, run logging stack on internal network or behind VPN, not exposed to public internet

### Recommendations for Production

- Use strong, unique passwords for all services (minimum 16 characters, alphanumeric + symbols)
- Configure Grafana authentication with LDAP or OAuth (GitHub, GitLab, Google) instead of local users
- Enable Grafana anonymous access restriction and role-based access control (RBAC)
- For ELK stack, configure X-Pack security (basic auth, TLS, audit logs) - see Elasticsearch documentation
- Regularly rotate API tokens and credentials used in CI/CD pipelines
- Set log retention policies to comply with local data protection regulations (GDPR, Russian Federal Law 152-FZ)
- Backup Grafana dashboards and Loki/Elasticsearch data to separate storage
- Monitor resource usage and set up disk space alerts to prevent log disk exhaustion

## Project Structure

```
russian-smb-devsecops-templates/
├── ci_security_templates/          # CI/CD security pipeline templates
│   ├── github/                     # GitHub Actions workflows
│   │   ├── php_bitrix/             # 1C-Bitrix PHP projects
│   │   ├── python/                 # Python projects
│   │   └── node/                   # Node.js projects
│   ├── gitlab/                     # GitLab CI templates
│   │   ├── php_bitrix/
│   │   ├── python/
│   │   └── node/
│   └── ai_pipeline_helpers/        # AI-assisted pipeline generation tools
├── logging_stack/                  # Centralized logging infrastructure
│   ├── loki/                       # Loki + Promtail + Grafana
│   │   ├── docker-compose.loki.yml
│   │   ├── promtail/               # Promtail config and pipelines
│   │   └── grafana/                # Dashboards and datasources
│   ├── elk/                        # Elasticsearch + Logstash + Kibana
│   │   ├── docker-compose.elk.yml
│   │   ├── logstash/               # Logstash pipelines
│   │   └── kibana/                 # Kibana dashboards
│   ├── parsers/                    # Log parser configurations (nginx, 1C, Bitrix, VPN)
│   └── ai_helpers/                 # AI-assisted parser generation
├── tools/                          # Validation and generation utilities
│   ├── validate_ci_templates.py    # Validates CI template syntax
│   ├── validate_logging_configs.py # Validates logging configurations
│   └── generate_example_project.py # Scaffolds example project
├── scripts/                        # Helper scripts
│   ├── lint.sh                     # Runs linters on repository
│   ├── security_scan.sh            # Runs Bandit security scan
│   └── perf_check.sh               # Performance validation
├── tests/                          # Unit and integration tests
│   ├── unit/                       # Unit tests for tools
│   └── integration/                # Integration tests for templates
├── README.md                       # This file (English)
├── README.ru.md                    # Russian version
├── LICENSE                         # Apache 2.0 license
├── CONTRIBUTING.md                 # Contribution guidelines
├── LEGAL.md                        # Legal disclaimer and usage terms
└── CHANGELOG.md                    # Version history
```

## Roadmap / Plans

- [ ] Add support for Vector.dev as alternative log collector
- [ ] Windows Server log collection templates (Event Log, IIS)
- [ ] Kubernetes/k3s deployment manifests (Helm charts)
- [ ] Pre-built alert rules for common incidents (disk space, authentication failures, service downtime)
- [ ] Integration examples with Zabbix and Prometheus monitoring
- [ ] Terraform modules for automated infrastructure deployment
- [ ] Support for additional Russian business software (e.g., Terraform, LDAP/FreeIPA)
- [ ] GitOps workflow examples with ArgoCD/Flux

Contributions to these roadmap items are welcome! See `CONTRIBUTING.md`.

## Contributing

We welcome contributions from the community! Here's how you can help:

### Reporting Issues

- Use GitHub Issues to report bugs or request features
- Provide detailed information: OS version, Docker version, error logs, steps to reproduce
- Check existing issues to avoid duplicates

### Submitting Pull Requests

1. Fork the repository and create a feature branch:
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. Make changes following code style guidelines:
   - **Python**: Use type hints, follow PEP 8, use `ruff` for linting
   - **YAML/JSON**: 2-space indentation, consistent key naming
   - **Shell scripts**: POSIX-compatible bash, use ShellCheck

3. Test your changes:
   ```bash
   # Run linter
   ./scripts/lint.sh

   # Run security scanner
   ./scripts/security_scan.sh

   # Run tests
   pytest
   ```

4. Update documentation (README.md, README.ru.md) and CHANGELOG.md

5. Open a pull request with clear description of changes and rationale

### Code Style

- Keep configurations free of secrets (use placeholders like `<YOUR_TOKEN>`)
- Include Russian comments for configs targeting Russian software (1C, Bitrix)
- Add English comments for broad applicability
- Write unit tests for new Python tools and validators

## License

This project is licensed under the **Apache License 2.0**. See [LICENSE](LICENSE) file for details.

Key points:
- Free to use, modify, and distribute
- Must preserve copyright and license notices
- Provided "as is" without warranties
- Contributors grant patent license for their contributions

## Author and Commercial Support

**Author**: [Ranas Mukminov](https://github.com/ranas-mukminov)  
**Website**: [run-as-daemon.ru](https://run-as-daemon.ru)

### Commercial Services

For production-grade setup, customization, and ongoing support, professional DevOps/SRE services are available:

- **Logging infrastructure deployment**: Full setup of centralized logging for nginx, 1C, 1C-Bitrix, mail servers, VPN with custom parsers and dashboards
- **Secure CI/CD implementation**: End-to-end pipeline setup with testing, SAST, dependency scanning, container security scanning, and deployment automation
- **Infrastructure audit**: Security and performance review of existing DevOps infrastructure
- **Team training**: Workshops on DevSecOps best practices, logging analysis, CI/CD security
- **Custom development**: Tailored parsers, dashboards, alerting rules, and integrations for your specific stack

Contact via [run-as-daemon.ru](https://run-as-daemon.ru) (Russian) or GitHub profile for inquiries.

---

**Disclaimer**: This project is not officially affiliated with or endorsed by 1C, 1C-Bitrix, GitHub, GitLab, Grafana Labs, Elastic NV, or any other mentioned companies. All trademarks belong to their respective owners.
