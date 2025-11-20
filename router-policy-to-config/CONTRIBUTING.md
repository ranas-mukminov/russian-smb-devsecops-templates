# Contributing to router-policy-to-config

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

Be respectful, professional, and constructive in all interactions.

## How to Contribute

### Reporting Issues

- Check if the issue already exists
- Provide clear reproduction steps
- Include relevant logs, error messages, and configurations (redact any secrets!)
- Specify your environment (OS, Python version, vendor target)

### Suggesting Features

- Open an issue with the "enhancement" label
- Describe the use case and expected behavior
- Discuss implementation approach if you have ideas

### Pull Requests

1. **Fork the repository** and create a feature branch
2. **Follow the code style** (Black, Ruff, isort)
3. **Write tests** for new functionality
4. **Update documentation** if needed
5. **Run all checks** before submitting:
   ```bash
   ./scripts/format.sh
   ./scripts/lint.sh
   pytest
   ```
6. **Submit PR** with clear description of changes

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/russian-smb-devsecops-templates.git
cd russian-smb-devsecops-templates/router-policy-to-config

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
./scripts/format.sh

# Check code
./scripts/lint.sh
```

## Code Style

- **Python 3.10+** features are allowed
- Use **type hints** where appropriate
- Follow **PEP 8** via Black (line length: 120)
- Use **dataclasses** for data structures
- Write **docstrings** for public APIs

## Adding New Policy Fields

1. Update `schema/policy-schema.yaml`
2. Add field to relevant dataclass in `model.py`
3. Update `policy_loader.py` to parse the field
4. Add validation in `policy_validator.py` if needed
5. Update backends to handle the new field
6. Write tests
7. Update documentation

## Adding New Vendor Backends

1. Create `src/router_policy_to_config/backends/VENDOR_backend.py`
2. Implement backend class with `generate()` method
3. Create corresponding diff module in `diff/VENDOR_diff.py`
4. Add vendor to CLI `--target` options
5. Write comprehensive tests
6. Update README with supported features

## Testing Guidelines

- **Unit tests** for individual components
- **Integration tests** for end-to-end workflows
- Use **pytest fixtures** for reusable test data
- Aim for >80% code coverage
- Test both success and error paths

## Security Considerations

- **Never commit secrets** or credentials
- Use `password_ref` and secret references
- Validate and sanitize all inputs
- Consider injection attacks in generated configs
- Report security issues privately

## Documentation

- Update README for user-facing changes
- Add docstrings for new functions/classes
- Update examples if behavior changes
- Keep CHANGELOG.md current

## Commit Messages

- Use clear, descriptive commit messages
- Reference issue numbers where applicable
- Use conventional commits format:
  - `feat:` new feature
  - `fix:` bug fix
  - `docs:` documentation only
  - `test:` adding tests
  - `refactor:` code refactoring

## Questions?

- Open a discussion on GitHub
- Check existing issues and PRs
- Contact maintainers at https://run-as-daemon.ru

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
