# Testing

Backend unit and integration tests live under:

```
tests/
└─ modules/
   ├─ account/
   ├─ application/
   └─ … (one folder per backend module)
```

Each module mirrors the structure of `src/apps/backend/modules`, keeping test code close to the implementation it exercises.

---

## Running the Test Suite

### Option 1: Docker (Recommended)

```bash
docker compose -f docker-compose.test.yml up --build
```

This will run all tests inside a fresh container, using the correct environment and dependencies.

### Option 2: Locally with NPM

```bash
npm run test
```

This command bootstraps the testing environment and runs `pytest` under the hood using the `testing` config.

---

## Conventions & Guidelines

| Topic              | Convention                                                                                          |
|--------------------|-----------------------------------------------------------------------------------------------------|
| **Test discovery** | Standard `pytest` discovery (`test_*.py` / `*_test.py`).                                            |
| **Database**       | Each test spins up fresh test collections; no mocks for DB operations.                              |
| **Naming**         | Test methods use `snake_case`; test classes inherit from sensible base fixtures (`base_test_*.py`). |
