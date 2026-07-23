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

## Coverage Gates

CI enforces a minimum coverage floor on both halves of the stack. The `test-backend` and `test-frontend` jobs each run `CodeCoverageSummary` with `fail_below_min: true`, and a follow-up step fails the build when the report step reports a shortfall. Coverage is no longer just a number in a PR comment; a drop below the floor turns the check red and blocks the merge.

Current floors:

| Suite    | Floor |
| -------- | ----- |
| Backend  | 80%   |
| Frontend | 35%   |

Each floor sits a little below where the suite actually runs today. That gap is deliberate: it lets ordinary churn move the real number up and down without going red, while still catching a genuine regression the moment coverage falls past the floor. Moving a floor is a deliberate change to the gate, not something to work around by adding assertion-free tests to pad the number.

---

## Conventions & Guidelines

| Topic              | Convention                                                                                          |
| ------------------ | --------------------------------------------------------------------------------------------------- |
| **Test discovery** | Standard `pytest` discovery (`test_*.py` / `*_test.py`).                                            |
| **Database**       | Each test spins up fresh test collections; no mocks for DB operations.                              |
| **Naming**         | Test methods use `snake_case`; test classes inherit from sensible base fixtures (`base_test_*.py`). |
