# Contributing

Thank you for considering a contribution! All changes are welcome as long as they help Russian SMB teams adopt logging and secure CI/CD faster.

## Ground rules
- Keep configs free from secrets; use placeholders and document required variables.
- Prefer Russian comments alongside concise English where it helps understanding.
- Avoid copying vendor templates verbatim; adapt best practices.
- Add or update tests under `tests/` when changing tools or CI templates.

## Workflow
1. Fork the repo and create a feature branch.
2. Run `scripts/lint.sh` and `scripts/security_scan.sh` locally if possible.
3. Open a pull request with a clear description of changes and rationale.
4. For new templates/configs, add notes to `CHANGELOG.md`.

## Code style
- Python: type hints, `ruff` friendly, prefer pure functions in tools.
- YAML/JSON: indent with two spaces, keep labels/service names consistent.
- Shell: POSIX-compatible where feasible.

Спасибо!

