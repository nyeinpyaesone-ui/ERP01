# Development Flow Guide

This document outlines the development workflow for the ERP01 project.

## Branching Strategy

- **main**: Production-ready code
- **feature/<ticket-id>-<description>**: Feature branches for new functionality
- **bugfix/<ticket-id>-<description>**: Bug fix branches
- **hotfix/<description>**: Urgent production fixes

## Commit Message Format

We follow the Conventional Commits specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning (white-space, formatting, etc)
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

### Examples:
```
feat(inventory): add stock tracking functionality
fix(auth): resolve login timeout issue
docs(readme): update installation instructions
test(config): add unit tests for configuration validation
```

## Development Workflow

### 1. Start a New Feature

```bash
# Create and switch to a new feature branch
git checkout -b feature/ERP-101-inventory-module
```

### 2. Make Changes

- Write code following project conventions
- Add/update tests for new functionality
- Ensure all tests pass before committing

### 3. Run Quality Checks

Before committing, run:

```bash
# Format code
black .

# Lint code
flake8 .

# Run tests with coverage
pytest --cov=.
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat(module): implement inventory module base"
```

### 5. Push and Create Pull Request

```bash
git push origin feature/ERP-101-inventory-module
```

Then create a Pull Request on GitHub targeting the `main` branch.

### 6. Code Review

- At least one team member must review and approve
- All CI checks must pass
- Address any review comments

### 7. Merge

Once approved:
- Squash and merge to keep history clean
- Delete the feature branch after merging

## Testing Requirements

- All new features must have corresponding tests
- Minimum code coverage: 80%
- Run full test suite before pushing: `pytest --cov=`

## Environment Setup

Ensure you have the development environment set up:

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Release Process

1. Update version in `__version__.py` or relevant file
2. Update CHANGELOG.md with new release notes
3. Create a git tag: `git tag -a v1.0.0 -m "Release v1.0.0"`
4. Push tag: `git push origin v1.0.0`
