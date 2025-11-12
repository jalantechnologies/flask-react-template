# Project Overview

Flask React Template is a full-stack application that pairs a modular Flask backend with a React + TypeScript frontend. MongoDB is the primary data store, Temporal powers background workflows, and both halves of the stack share a focus on layered, testable architecture.

**Stack:**
- **Backend:** Python 3.12 · Flask 3 · PyMongo · Pydantic · Temporal
- **Frontend:** React 18 · TypeScript · Tailwind CSS · Axios
- **Build Tooling:** Webpack 5 · Pipenv · npm scripts
- **Testing:** Pytest + pytest-cov
- **Deployment:** Docker · Kubernetes · Temporal Cloud/self-hosted workers

**Key Directories:**
- `/src/apps/backend` – Flask application and domain modules
- `/src/apps/frontend` – React single-page app
- `/tests` – Backend test suite (pytest)
- `/docs` – Architecture and operational documentation
- `/config` – Shared configuration and environment settings

## Build and Test Commands

```bash
# Launch backend and frontend together (Temporal services optional)
npm run serve

# Run only the Flask API (Gunicorn with reload)
npm run serve:backend

# Start the React dev server with hot reload
npm run serve:frontend

# Build production bundles for both backend assets and frontend
npm run build

# Backend test suite with coverage (pytest)
npm run test

# Python linting (mypy + pylint)
npm run lint:py

# TypeScript / React linting
npm run lint:ts

# Markdown linting
npm run lint:md
```

Use `pipenv install --dev` (from `src/apps/backend`) to bootstrap backend tooling and `npm install` for frontend dependencies.

## Architecture Principles

### Backend Architecture
- **Modular Design:** Each domain module (account, authentication, application, task, etc.) under `modules/` owns its REST API, service, and persistence layers.
- **Layered Structure:** HTTP (Flask blueprints) → View → Service → Reader/Writer → Repository → MongoDB.
- **Encapsulation:** Only expose `*_service.py`, `types.py`, and module-specific exceptions. Everything under `internal/` is private.
- **Clear Data Models:** Use Pydantic models and dataclasses to validate inputs/outputs at the boundaries.

### Frontend Architecture
- **Layer-Based:** Pages → Components → Contexts → Services.
- **State Management:** Prefer React Context + hooks; avoid introducing Redux-like solutions without team approval.
- **Service Layer:** All API calls flow through typed service modules that convert JSON into domain models/interfaces.

## Review Guidelines

### General Programming Principles

#### 1. Code Documentation
- **DO** write comments that capture intent, invariants, or non-obvious design decisions.
- **DON'T** narrate what the code already states.

#### 2. Naming Conventions
- Follow PEP 8 for Python (snake_case functions & variables, PascalCase classes) and idiomatic TypeScript naming.
- Choose descriptive names that communicate purpose.
- Avoid verb-based names for Python classes or React components. Functions, methods, and hooks should be verbs (e.g., `load_account`, `fetchUserData`).

#### 3. Function Size and Complexity
- Keep functions focused on a single responsibility.
- Break apart routines that exceed ~50 lines or mix multiple concerns.
- Prefer clear helper names over comments explaining control flow.

#### 4. Object-Oriented & Layered Design
- Keep domain behavior alongside the data it manipulates (services, domain objects, Pydantic models).
- Avoid scattering related logic across shared utilities when it belongs to a specific module.

#### 5. Defensive Programming
- Avoid sprinkling `if value is None` / optional checks without understanding nullability.
- Validate inputs at module boundaries (Pydantic models, request schemas) and rely on the types afterwards.

#### 6. Encapsulation Over Utilities
- Place behavior within the relevant module (e.g., reader/writer helpers) instead of creating broad utility modules.

#### 7. Code Reuse
- Audit existing modules, services, and hooks before writing new ones.
- Extract shared logic rather than duplicating code across modules or components.

---

### Backend-Specific Guidelines

#### 8. Module Independence
- **DON'T** import from another module's `internal/` packages.
- **DO** rely on the public service API (`*_service.py`) or shared types.

#### 9. Database Indexes & Data Access
- Ensure MongoDB indexes cover every `find`, `find_one`, aggregation `$match`, or `sort` pattern.
- Declare indexes in the repository layer (`internal/store/*_repository.py`).

#### 10. API Design
- Favor RESTful CRUD semantics: `GET`, `POST`, `PATCH`, `DELETE` on resource nouns.
- Provide a single `update` method per resource that accepts a well-defined DTO instead of field-specific methods.

#### 11. Business Logic Placement
- Keep business rules in the service layer.
- Avoid embedding domain logic inside Flask views, CLI scripts, or Temporal workers—delegate to services.

#### 12. Temporal & Background Workflows
- Use Temporal clients/workflows for asynchronous processing.
- Avoid ad-hoc threading, Celery, or CronJobs unless explicitly required.

#### 13. Query Efficiency
- Guard against N+1 queries by batching lookups or using aggregation pipelines.
- Push filtering into Mongo queries instead of post-processing large in-memory lists.

---

### Frontend-Specific Guidelines

#### 14. Styling Practices
- **DON'T** use inline styles.
- **DO** rely on Tailwind utility classes or shared CSS modules as needed.

#### 15. Component Contracts & Variants
- Avoid per-page style overrides. Create component variants/props for different presentations.
- Shared layout primitives should live under `src/apps/frontend/components` or `layouts` rather than page folders.

#### 16. Data Fetching & State
- Fetch data through service modules under `services/` or `api/`.
- Normalize API responses into typed models before storing them in state.
- Avoid performing side-effectful data fetching inside render without hooks.

#### 17. List Rendering Performance
- Batch API requests when rendering collections. Never fire N network calls for N items within a render loop.

---

## Security Considerations

- Never log or echo PII.
- Ensure protected routes are wrapped in authentication/authorization middleware (Flask decorators or blueprints).
- Validate and sanitize all incoming data; prefer Pydantic models for request bodies and query params.
- Use parameterized Mongo queries. Avoid building raw query strings with user input.
- Keep secrets in environment variables or Doppler; never commit credentials.

## Testing Requirements

- Add or update pytest coverage for new backend endpoints or services (`tests/modules/...`).
- Place integration tests alongside module directories under `tests/modules/<module>/`.
- Target ≥60% coverage (80% preferred). Pytest runs with coverage reporting via `npm run test` or `make run-test`.

## Commit and PR Guidelines

### Commit Messages
- Use Conventional Commits: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `style`.
- Write messages that communicate the why/purpose.
- Example: `fix: enforce unique index on account email`.

### Pull Request Requirements
- PR titles must summarize the change.
- Include a rationale and testing evidence in the PR body.
- Keep diffs focused on a single concern.
- All linting, type checks, and tests must pass (Python + TypeScript).
- Link any related issues or tickets.

---

## Additional Resources

- [Backend Architecture](docs/backend-architecture.md)
- [Frontend Architecture](docs/frontend-architecture.md)
- [Configuration Guide](docs/configuration.md)
- [Testing Guide](docs/testing.md)
- [Engineering Handbook](https://github.com/jalantechnologies/handbook/blob/main/engineering/index.md)

