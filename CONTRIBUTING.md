# Contributing to Evershade

Thank you for interested in contributing to Evershade!

---

## Code of Conduct

Be respectful, constructive, and inclusive. Harassment or abusive behavior will not be tolerated.

---

## How to Contribute

### Reporting Bugs

1. Search existing issues to avoid duplicates
2. Use the bug report template
3. Include steps to reproduce, expected vs actual behavior, and environment details
4. **Do not** include API keys, secrets, or sensitive data

### Suggesting Features

1. Check `ROADMAP.md` and existing issues
2. Use the feature request template
3. Explain the problem, proposed solution, and alternatives considered

### Pull Requests

1. Fork the repository
2. Create a feature branch from `main`
3. Make your changes
4. Run tests: `pytest` (Python) or `npm test` (TypeScript)
5. Lint and format code
6. Update documentation if applicable
7. Use Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, etc.
8. Submit the pull request

### PR Requirements

- All tests pass
- No linting or formatting errors
- Documentation updated if behavior changes
- No secrets or credentials committed
- Clear description of changes and motivation

---

## Development Setup

See `docs/DEVELOPMENT.md` for detailed setup instructions.

```bash
# Quick start
git clone https://github.com/LukaG712/Evershade.git
cd Evershade
cp .env.example .env
docker compose --profile dev up -d
```

---

## Code Style

- **Python:** PEP 8, `ruff` for linting/formatting
- **TypeScript:** ESLint config, `prettier` for formatting
- **Commits:** Conventional Commits format

---

## Security Issues

Do **not** open public issues for security vulnerabilities. Report them privately to the repository maintainers.

---

## License

By contributing, you agree that your contributions will be licensed under the project's license (MIT). See `LICENSE` for details.
