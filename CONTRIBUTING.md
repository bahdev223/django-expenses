# Contributing to django-expenses

Thank you for your interest! Here's how to get started.

## Development setup

```bash
git clone https://github.com/bahdev223/django-expenses.git
cd django-expenses
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Running tests

```bash
pytest
```

With coverage:

```bash
coverage run -m pytest
coverage report
```

## Code style

We use Ruff for linting. Run before committing:

```bash
ruff check src/
ruff format src/
```

## Pull request process

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feat/amazing-feature`)
5. Open a Pull Request

## Commit convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation
- `refactor:` code refactoring
- `test:` adding tests
- `chore:` maintenance
