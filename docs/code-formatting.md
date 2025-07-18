# Code Formatting

We use opinionated formatters to ensure consistent code style across the codebase—backend, frontend, and tests.

---

## Python Formatting

All Python files (backend and tests) are auto-formatted using:

- **[autoflake](https://pypi.org/project/autoflake/)** – Removes unused imports and variables.
- **[isort](https://pycqa.github.io/isort/)** – Sorts and groups imports.
- **[black](https://black.readthedocs.io/)** – Formats Python code to a consistent style.

### Format All Python Files

```bash
npm run fmt:py
```

This will recursively format everything under `src/` and `tests/`.

### Test-Specific Configuration

Test files have a separate configuration in:

```
tests/pyproject.toml
```

---

## JS/TS Formatting

For JavaScript and TypeScript files, we use **[Prettier](https://prettier.io/)**.

### Format All JS/TS Files

```bash
npm run fmt:ts
```

---

## Pre-commit Hook (lint-staged)

We use `lint-staged` to format staged files automatically before a commit.

- Runs `black`, `isort`, and `autoflake` for staged `.py` files.
- Runs `prettier` for staged `.js`, `.ts`, `.tsx`, `.json`, etc.
