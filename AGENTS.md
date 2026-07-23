# Project Overview

Flask React Template is a full-stack application that pairs a modular Flask backend with a React + TypeScript frontend. MongoDB is the primary data store, Celery + Redis handle background jobs, and both halves of the stack share a focus on layered, testable architecture.

**Stack:**

- **Backend:** Python 3.12 · Flask 3 · PyMongo · Pydantic · Celery
- **Frontend:** React 18 · TypeScript · Tailwind CSS · Axios
- **Infrastructure:** MongoDB · Redis
- **Build Tooling:** Webpack 5 · Pipenv · npm scripts
- **Testing:** Pytest + pytest-cov
- **Deployment:** Docker · Kubernetes

**Key Directories:**

- `/src/apps/backend` – Flask application and domain modules
- `/src/apps/frontend` – React single-page app
- `/tests` – Backend test suite (pytest)
- `/docs` – Architecture and operational documentation
- `/config` – Shared configuration and environment settings

## Build and Test Commands

```bash
# Launch backend, frontend, and workers together
npm run serve

# Run only the Flask API (Gunicorn with reload)
npm run serve:backend

# Run only Celery workers
npm run serve:worker

# Run only Celery beat scheduler (cron jobs)
npm run serve:beat

# Start Flower dashboard (worker monitoring UI at `localhost:5555`)
npm run serve:flower

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

- **Modular Design:** Each domain module (account, authentication, core, task, etc.) under `modules/` owns its REST API, service, and persistence layers.
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

- **DON'T** write comments. Code must be self-explanatory: express intent through clear names, small
  single-purpose functions, and well-named intermediate variables and helpers instead of prose.
- A comment is a signal that the code is not clear enough. When tempted to explain a block, extract it
  into a named helper or introduce a named constant instead.
- The only permitted exceptions are mechanical directives the toolchain requires (`type: ignore`,
  `pylint: disable`, `noqa`) and a single irreducible line where the _why_ cannot be encoded in the
  code itself (a non-obvious external constraint or workaround). Never narrate what the code states.
- Docstrings follow the same rule: none, except where a public abstract base method's contract cannot
  be conveyed by its signature.

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
- A repository is pure storage. It inherits the CRUD verbs from `ApplicationRepository` (`modules/core/repository.py`); don't add `find_by_<field>` / `update_<field>` / `count_<thing>` methods—those belong on the module's reader or writer.
- No MongoDB syntax crosses a repository's public surface. Callers pass a typed query object, never a `{"field": ...}` filter, an `ObjectId`, or a `$set`; every verb returns a domain dataclass, never a raw BSON document.

#### 10. API Design

- Favor RESTful CRUD semantics: `GET`, `POST`, `PATCH`, `DELETE` on resource nouns.
- Provide a single `update` method per resource that accepts a well-defined DTO instead of field-specific methods.

#### 11. Business Logic Placement

- Keep business rules in the module, not in an execution layer. Avoid embedding domain logic inside Flask views, routers, workers, or CLI scripts—delegate to the module's service.
- Service methods are thin: they call the right reader or writer. Logic needed only internally (password hashing, OTP generation, validation) lives in the module's `internal/*_writer.py` or `*_util.py`, not in the service itself.
- Build a typed object from a request body with a `from_dict()`-style factory on the DTO (`types.py`), not with parsing code in the view.

#### 12. Background Jobs

- Use Celery workers for async job processing (document processing, entity extraction, etc.).
- Define workers in `modules/core/workers/` inheriting from `Worker`.
- Use cron schedules for recurring tasks (e.g., `cron_schedule = "*/10 * * * *"`).

#### 13. Query Efficiency

- Guard against N+1 queries by batching lookups or using aggregation pipelines.
- Push filtering into Mongo queries instead of post-processing large in-memory lists.

#### 14. Auditing (SOC2)

- Every write through `ApplicationRepository` (`create`, `update`, `update_fields`, `delete`) is audited automatically. You do not add audit calls in views, services, readers, or writers — the base repository records the resource type, resource id, actor, action, and (on update) the changed fields. Keep audit code out of the execution and domain layers.
- Every mutating repository method takes a required `actor: AuditActor` keyword argument, threaded explicitly from the boundary through the service and writer. There is no ambient context; the type checker proves at compile time that no write happens without an actor. Choose the actor by whether identity is proven at the write: `AuditActor(ActorType.ACCOUNT, account_id)` when the credential/token in hand identifies an account (authenticated mutations, login OTP verify and access-token creation, password-reset completion); `AuditActor(ActorType.WORKER, "<name>")` for a background job, seed, or system flow; `AuditActor(ActorType.ANONYMOUS, None)` for a request with no proven identity yet (signup, OTP request/creation, forgot-password token request). There is no opt-out — completeness is the point.
- Never store a secret's value in the trail. The writer redacts sensitive field values (`password`, `token`, `secret`, `otp`, `mfa`, `hashed`); do not defeat this by renaming a sensitive field.
- Every entry carries an `outcome`: `success` (the default) or `denied`. All create/read/update/delete audits are `success`; the field is defaulted, so existing emission paths and stored rows are unchanged. A `denied` entry records an authenticated account that was rejected for crossing an ownership boundary: the auth middleware (`enforce_account_ownership`) emits one `outcome=denied` READ entry against the target account boundary before raising, with the real authenticated account as actor. Missing, invalid, or expired token rejections have no proven actor and are not audited.
- For the rare access a custom method performs that the generic CRUD does not cover, call `ApplicationService.record_audit(...)`. This should be uncommon; if you find yourself using it often, the data access likely belongs in a repository.

---

### Frontend-Specific Guidelines

#### 14. Styling Practices (Design System)

The frontend uses a token-driven design system. The full contract is in [Frontend Design System](docs/frontend-design-system.md). In review:

- **DON'T** pass `className` to raw DOM elements in `src/apps/frontend/pages/**`, and never use inline `style`. This is lint-enforced.
- **DON'T** reach for raw Tailwind spacing or color on a page. Use layout primitives (`Stack`, `Inline`, `Grid`) with `Spacing` gap tokens, and the semantic theme colors in `tailwind.config.js`.
- **DO** assemble pages from design-system components imported from `frontend/components`.

#### 15. Component Contracts & Variants

- Presentation is selected through tokens — `variant`, `size`, `gap` — not class strings. A look an existing component does not offer is a missing variant: add it to the component, do not inline it on the page.
- Interfaces are idiomatic, not consumer-shaped. Follow shadcn / Radix / Bootstrap / MUI: `variant` for status colour (the `Status` token), native events on form `onChange`, `checked` / `onCheckedChange` for `Switch` and `Checkbox`, `src` / `fallback` for `Avatar`, `DataTable` for the data grid.
- Never declare a `children` field in a Props interface or type. Type the component as `React.FC<PropsWithChildren<XProps>>`; for non-JSX content (a markdown string) use a named prop like `content`. Lint-enforced.
- A component's public props must not accept a `className` escape hatch. className and Tailwind classes live inside components only.
- Shared components and layout primitives live under `src/apps/frontend/components`, never in page folders.
- Every component declares an optional `testId?: string` and renders it as `data-testid` on its root element, icons and decorative primitives included. Tests address the UI through stable `data-testid` hooks, never brittle text or class selectors.
- Every component is accessible. An icon or shape that carries meaning exposes an accessible name (`ariaLabel` / `label`) and drops `aria-hidden`; a purely decorative glyph stays `aria-hidden`. An interactive element is a real semantic element (`button`, `a`, `input`) or carries the correct `role` plus keyboard handling. A form control associates its label and its error (`htmlFor` / `aria-describedby` / `aria-invalid`).

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
- Use TLS on the MongoDB connection outside local development. Startup warns when `MONGODB_URI` lacks TLS — see [MongoDB Security](docs/mongodb-security.md).

## Security

This template is meant to be SOC2-ready by default. Security is part of the feature, not a later pass. This section is a checklist to apply to every change and to flag in the pull request.

**On any change, check it against the rules below and call out the risk in the PR.** If a change adds a route, a provider, a subprocess, an outbound HTTP call, a login or session step, or a new stored secret, it touches one of these rules. Say which rule applies and how the change satisfies it. If it touches audit logging, access control, credentials, encryption, or session handling, label it SOC2-relevant in the PR so the control is visible. The author raises this, not the reviewer. Do not wait for a security review.

Each rule below is the generic form of a real, shipped, exploitable bug. Follow them so the same bug does not come back in a new provider or route.

**Do not pass the whole environment into a subprocess or an outside call.** `{**os.environ}` hands over every secret the process holds, even ones the callee never needs. One leak like this can expose a database password to a process that had no reason to see it. Pass only the exact variables the callee needs, as an explicit allowlist.

**Take away the ability, not just the option.** You cannot block a bad action by filtering commands or inputs, because a shell or a downstream call can phrase the same thing many ways. Give the caller a credential that simply cannot do the dangerous thing. A database user with a read-only role cannot write, no matter what query it runs.

**Fix a shared gap in the shared code, once.** When many routes or providers go through the same function, put the check there. One change protects every caller, now and later, for the same effort as fixing one spot. For example, if `Link` and `Markdown` both render links through a single `isSafeHref` allowlist, the XSS fix lives in one place.

**Check any URL you will fetch or display, and turn off redirects.** An attacker-controlled URL is an SSRF risk when the server fetches it and an XSS risk when the browser renders it. Validate it with the same parser the fetch library uses, since parsers disagree on odd input and a mismatch lets a bad host through. Allow only the scheme and host you expect (`https` and a known domain), reject a `javascript:` link on the frontend, and pass `allow_redirects=False` so an allowed host cannot bounce you somewhere internal.

**Do not turn a failed read into a "nothing here" answer.** `items = resp.json() if resp.status_code == 200 else []` turns a temporary 5xx into "the list is empty," which then causes a duplicate write or a wrong disabled state on the next call. Raise on a non-200 and let the caller decide whether to retry.

**Audit-log facts must come from something the user cannot fake.** Never record a client header like `X-Forwarded-For` as the actor's IP. Use `request.remote_addr`, which `ProxyFix` already sets correctly behind the trusted proxy (see `server.py`). Also make sure a failed action still writes its audit event, including when the route fails by raising. An audit trail the user can forge or skip is not a trail.

## Testing Requirements

- Add or update pytest coverage for new backend endpoints or services (`tests/modules/...`).
- Place integration tests alongside module directories under `tests/modules/<module>/`.
- Target ≥60% coverage (80% preferred). Pytest runs with coverage reporting via `npm run test` or `make run-test`.

## Commit and PR Guidelines

### Commit Messages

Format:

```
<type>(<scope>): <subject>
```

Where `<scope>` is optional.

```
feat(claims): add confidence bounds validation
^--^ ^----^   ^-----------------------------^
|    |        |
|    |        +-> Summary in present tense, imperative mood
|    +-> Scope: component or module affected
+-> Type
```

Types:

- `feat` — new feature for users
- `fix` — bug fix for users
- `docs` — documentation only
- `style` — formatting, no logic change
- `refactor` — code restructuring, no behavior change
- `test` — adding or updating tests
- `chore` — maintenance tasks
- `build` — build system or dependencies
- `ci` — CI configuration
- `perf` — performance improvements
- `revert` — reverts a previous commit

Breaking changes: add `!` after type:

```
feat(api)!: remove deprecated endpoint
```

Rules:

- 50 characters max for subject line
- Use present tense, imperative mood ("add" not "added")
- No period at end
- Write messages that communicate the why/purpose

Examples:

- `feat(account): add email verification flow`
- `fix(auth): preserve session on token refresh`
- `refactor(store): extract append-only writer`
- `docs: update deployment architecture guide`

### PR Title Format

PR titles follow the same semantic format as commit messages:

```
<type>(<scope>): <subject>
```

This ensures consistency across commits, PRs, and changelogs. The title prefix also drives automatic labeling (see below).

### Auto-Labeling

PRs are automatically labeled based on title prefix via the `pr-labeler` workflow:

| PR Title Prefix              | Type Label                 | Semver Label    |
| ---------------------------- | -------------------------- | --------------- |
| `feat:`                      | `type: feat`               | `semver: minor` |
| `fix:`                       | `type: fix`                | `semver: patch` |
| `perf:`                      | `type: perf`               | `semver: patch` |
| `docs:`                      | `type: docs`               | —               |
| `style:`                     | `type: style`              | —               |
| `refactor:`                  | `type: refactor`           | —               |
| `test:`                      | `type: test`               | —               |
| `chore:`                     | `type: chore`              | —               |
| `build:`                     | `type: build`              | —               |
| `ci:`                        | `type: ci`                 | —               |
| `revert:`                    | `type: revert`             | —               |
| Breaking (`feat!:`, `fix!:`) | `type: feat` / `type: fix` | `semver: major` |

Choose your type carefully — it determines the label and semver impact.

### Pull Request Requirements

- PR titles must follow the semantic format above.
- Include a rationale and testing evidence in the PR body.
- Keep diffs focused on a single concern.
- All linting, type checks, and tests must pass (Python + TypeScript).
- Link any related issues or tickets.

---

## Additional Resources

- [Backend Architecture](docs/backend-architecture.md)
- [Frontend Architecture](docs/frontend-architecture.md)
- [Configuration Guide](docs/configuration.md)
- [MongoDB Security](docs/mongodb-security.md)
- [Testing Guide](docs/testing.md)
- [Engineering Handbook](https://github.com/jalantechnologies/handbook/blob/main/engineering/index.md)
