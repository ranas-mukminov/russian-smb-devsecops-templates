# Changelog

All notable changes to router-policy-to-config will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of router-policy-to-config
- YAML-based policy schema for vendor-agnostic router configuration
- RouterOS backend for generating MikroTik configurations (.rsc scripts)
- OpenWrt backend for generating UCI configurations
- Policy validation (schema and semantic)
- Diff engine for comparing generated vs current configurations
- CLI with subcommands: init, validate, render, diff, ai-suggest, lab-test
- AI helpers for policy generation from natural language
- Test case generator for lab validation
- Comprehensive documentation and examples
- Example policies (home-office, guest-wifi)
- Unit and integration tests
- Automation scripts (lint, format, security scan)

### Security
- Secret management via environment variables
- No secrets stored in policy files
- Input validation to prevent injection attacks

## [0.1.0] - 2025-11-20

### Added
- Initial project structure
- Core data models
- Policy loader and validator
- RouterOS and OpenWrt backends
- Diff modules
- CLI interface
- AI provider infrastructure
- Example policies
- Documentation (README, LEGAL, CONTRIBUTING)

[Unreleased]: https://github.com/ranas-mukminov/russian-smb-devsecops-templates/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ranas-mukminov/russian-smb-devsecops-templates/releases/tag/v0.1.0
