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

Backend tests run against a real MongoDB. `make run-lint` runs `mypy` (strict) and a `pylint` cyclic-import
check; `make run-format` and `make run-format-check` run autoflake, isort, and black (line length 120). Keep
all of these green before pushing.

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

#### 8. No Swallowed Errors

An `except` block does one of three things and never a fourth:

1. Re-raises.
2. Raises a different typed error in its place.
3. Logs enough detail to act on and continues, for a reason the surrounding code makes obvious.

Catching broadly is fine when the handler re-raises or converts. The problem is a handler that ends
without raising and without logging, because the failure then looks exactly like success to everything
upstream.

`AccessTokenUtil.verify_access_token` is the converting form: it catches the library's
`jwt.exceptions.DecodeError` and `jwt.ExpiredSignatureError` and raises `AccessTokenInvalidError` /
`AccessTokenExpiredError`, so callers depend on our error types rather than on JWT internals.

The third form needs the surrounding code to justify it. In `AccountView.get`, a missing
`AccountNotificationPreferencesNotFoundError` is caught and passed over because the preferences block
is an optional add-on to the response and its absence is a real state, not a failure. That is
deliberate, and it is visible from the two lines around it.

**Background jobs are a special case.** `Job` (`modules/core/job.py`) registers its Celery task with
`autoretry_for=(Exception,)`. An exception leaving `perform` is retried automatically, the `job_run`
row is marked `failed`, and a persistent failure stays visible. A job that catches its own error and
returns normally tells Celery the work succeeded: no retry, a `job_run` row marked `succeeded`, and
nothing anywhere saying the work did not happen. Let the exception out of `perform`, or log it and be
explicit that you are choosing not to retry.

#### 9. Nothing Ships Without a Caller

Every public name a change adds has a caller in the same change. Before opening a pull request, grep
for each new public name. If the only matches are the definition and its own passthrough (a service
method that only forwards to a reader nobody else calls), delete both.

Unused surface is not free. The next reader assumes it is load bearing, works around it, keeps it
compiling, and writes tests for it. A speculative helper added "for the next feature" costs more to
carry than it costs to write again when the next feature actually arrives.

#### 10. Imports Go at the Top

Never import inside a function body. A module's import list is the honest statement of what it depends
on; an import buried in a method hides the dependency and turns a load-time error into a call-time one
that only shows up on the path that reaches it.

An import inside a function is almost always working around a circular import. Fix the cycle instead:
move the shared type into `modules/core/common/types.py`, or invert the direction so the lower layer
stops importing the higher one. `make run-lint` runs a `pylint` cyclic-import check for exactly this
reason.

The same applies to `if TYPE_CHECKING:` blocks added so a module can annotate a type it is not allowed
to import at runtime. That is the same cycle, deferred to the type checker.

#### 11. An Entity Has One Shape

One type per entity, used everywhere that entity is read, with every field always populated.

- No optional fields added because one caller happens to know less. An `Optional` on a domain type
  should mean the value is genuinely absent in the domain, the way `Account.phone_number` is optional
  because an account created by username has no phone number.
- No second near-identical class. `Task` is the task, whether it came from a list, a detail read, or a
  create.

If a read genuinely needs more than the entity, that is a composition named for what it adds, and it
holds the entity rather than being a variant of it. Never name it after the route or the caller:
`TaskWithAssignee`, not `TaskListItem` or `DashboardTask`. A type named after its consumer stops being
reusable the moment a second consumer appears.

#### 12. A Module Names What It Serves, Never Who Calls It

A view, service method, or file with a role in its name states an assumption it has no business
holding. Access control is decided by middleware at the boundary, and the domain layer should not
encode a guess about it.

The same goes for URLs: a path segment names a resource, never a permission or an audience.
`/admin/accounts` is wrong. Our routes are `/accounts/<account_id>` and
`/accounts/<account_id>/tasks`: the noun is the resource, and `enforce_account_ownership` decides who
gets an answer. When the permission model changes, a resource-named route keeps working and a
role-named route has to be renamed everywhere.

#### 13. Name the Mutation

A function that changes something outside itself says so in its name. Use a verb that names the
change: `create`, `write`, `update`, `delete`, `send`, `publish`, `archive`, `record`, `enqueue`,
`revoke`. `AccountWriter.create_account_by_username_and_password` and
`AuditService.record_audit` read as the writes they are.

Functions that compute and return without touching anything can be named for what they answer:
`AccountReader.get_account_by_username`, `AccessTokenUtil.verify_access_token`.

The exception is framework entry points, which keep the names their frameworks gave them. `Job.perform`
stays `perform`.

#### 14. A Pull Request Contains Only What Its Issue Asked For

If you trip over an unrelated problem, file it. Do not fix it here.

The check is mechanical: run `git diff --stat origin/main...HEAD` and confirm every file in the list
belongs to the issue. A file you cannot justify is the signal.

Being right that the other problem is real is not the question. Where it gets fixed is. A mixed diff is
slower to review, harder to revert cleanly, and hides the change the reviewer was asked to look at.

---

### Backend-Specific Guidelines

#### 15. Module Independence

- **DON'T** import from another module's `internal/` packages.
- **DO** rely on the public service API (`*_service.py`) or shared types.

The backend (`src/apps/backend`) is organised into modules, one per domain concept (account, task,
authentication, notification, and so on). A module exposes a `<module>_service.py` as its public API;
other modules call only the service, never a module's internals. Inside a module:

- `internal/store/` — the persistence layer: a `*_model.py` (BSON dataclass) and a `*_repository.py`.
- `internal/*_reader.py` / `internal/*_writer.py` — business reads and writes.
- `internal/*_util.py` — pure helpers (hashing, generation, validation).
- `rest_api/` — Flask blueprint, router, and view.
- `types.py` / `errors.py` — DTOs (`@dataclass(frozen=True)`) and `AppError` subclasses.

#### 16. Database Indexes & Data Access

- Ensure MongoDB indexes cover every `find`, `find_one`, aggregation `$match`, or `sort` pattern.
- Declare indexes in the repository layer (`internal/store/*_repository.py`).

**Repositories inherit generic CRUD.** A repository extends `ApplicationRepository[Entity, Query]`
(in `modules/core/repository.py`) and inherits the generic CRUD surface. Do not re-implement these per
repository:

- `create(entity)` — insert one, return the stored entity.
- `find(id)` / `find_many(ids)` — read by primary id.
- `query(params)` / `query_one(params)` — read many / at-most-one by a typed query object.
- `query_paginated(params, pagination)` — a page of `query()` results plus totals (`PaginationResult`).
  This is the only place pagination math lives.
- `count(params)` — how many match a typed query.
- `update(id, fields)` — patch fields on one by id, return the refreshed entity.
- `update_fields(id, fields)` — same `$set` without the read-back; returns `True` if a document matched.
  Use this in writers that patch and discard the result, one round-trip instead of two.
- `delete(id)` — remove one by id.

A malformed id is treated as "no such document" (the verb returns `None`/`False`), not an error.

A concrete repository declares only what is specific to its collection:

- `collection_name` — the Mongo collection name.
- `on_init_collection(collection)` — declares indexes and JSON-Schema validation.
- `from_doc(doc) -> Entity` — hydrates a stored document into the domain entity. **Required.**
- `to_doc(entity) -> StoredDocument` — serializes an entity for insertion. Override when the default is
  not enough, for example when a separate `*Model` supplies stored-only fields (`active`, timestamps)
  the domain entity omits.
- `_to_filter(params) -> StoreFilter` — maps the module's typed query object to a store filter. Required
  only if the repository supports `query()`; a query-less repository (singleton, write-only log) declares
  `NoQuery` as its query type.
- `_to_sort(params) -> Optional[SortSpec]` — optional default ordering for `query()`/`query_paginated()`.

**No MongoDB syntax may cross the public surface.** Callers never write a `{"field": ...}` filter, an
`ObjectId`, or a `$set`. A field-combination read is a typed query object, `query(AccountQuery(username=x))`
and not `query({"username": x})`, and `_to_filter` is the single place domain fields become store syntax.
Every verb returns a domain dataclass (via `from_doc`), never a raw BSON document. The only intentionally
untyped values are the storage-boundary aliases `StoredDocument` / `StoreFilter` / `FieldUpdates` /
`SortSpec`. Use those names, not bare `dict[str, Any]`, so the boundary is visible.

**A repository is pure storage.** Thin domain reads and writes do NOT live on it. They live on the module's
reader (reads) or writer (writes), which call the verbs. `AccountReader.get_account_by_username` is
`AccountRepository.query_one(AccountQuery(username=username))`; the account writer's soft-delete is
`AccountRepository.update_fields(id, {"active": False, ...})`. Do not add `find_by_<field>` /
`update_<field>` / `count_<thing>` methods to a repository, put them on the reader or writer.

The only methods that stay on a repository beyond the verbs are operations no CRUD verb can express, which is
exactly the code a storage swap would rewrite: an upsert or update by a natural key
(`AccountNotificationPreferencesRepository.update_by_account_id`), a create that keys store-shaped fields the
domain entity does not carry (`PasswordResetTokenRepository.create_for_account` keys `account` as an
`ObjectId`), an atomic `$inc`/`$push`, an aggregation, a `distinct`. Implement these with the protected
helpers (`_query`, `_find_one`, `_count`, `_to_object_id`) where possible; reach for the raw `collection()`
only when the operation genuinely has no helper form.

Soft-deleted collections (account, task, notification preferences) carry an `active` flag. Their query
objects default `active=True`, so reads see only live records and the soft-delete is a single
`update_fields(id, {"active": False, ...})` on the writer.

> The generic base uses Python 3.12 type-parameter syntax (`class ApplicationRepository[Entity, Query]:`,
> `type StoredDocument = ...`). The backend runs and is checked on Python 3.12.

#### 17. API Design

- Favor RESTful CRUD semantics: `GET`, `POST`, `PATCH`, `DELETE` on resource nouns.
- Provide a single `update` method per resource that accepts a well-defined DTO instead of field-specific methods.

#### 18. Business Logic Placement

- Keep business rules in the module, not in an execution layer. Avoid embedding domain logic inside Flask views, routers, workers, or CLI scripts—delegate to the module's service.
- Service methods are thin: they call the right reader or writer. Logic needed only internally (password hashing, OTP generation, validation) lives in the module's `internal/*_writer.py` or `*_util.py`, not in the service itself.
- Build a typed object from a request body with a `from_dict()`-style factory on the DTO (`types.py`), not with parsing code in the view.

#### 19. Background Jobs

- A **job** is the unit of async work; a **worker** is the Celery process that runs it. Define jobs in the public `modules/<module>/jobs/` package of the domain that owns them, inheriting from `Job` (`modules/core/job.py`). Do not put them under `internal/`.
- The Celery app object lives in `modules/core/celery_app.py`. The process entrypoints are `web_app.py` (gunicorn `web_app:app`) and `worker_app.py` (celery `-A worker_app worker|beat|flower`); both import downward into modules. `JobRegistry` discovers jobs by importing every `modules/*/jobs/` package and registering each immediate `Job` subclass, so registration happens at entrypoint import, before the worker snapshots its task table.
- Use cron schedules for recurring tasks (e.g., `cron_schedule = "*/10 * * * *"`). Cron entries persist to the RedBeat Redis schedule.
- Every execution records a `job_run` row (job name, redacted arguments, start/end time, status `running`→`succeeded|failed`, retry count). The `Job` base creates it at the start of the run and finalizes it on completion or failure; the run's id becomes the job's audit actor (see §21). `perform` receives an `actor: AuditActor` keyword and threads it into every repository call so the writes attribute to that run.

#### 20. Query Efficiency

- Guard against N+1 queries by batching lookups or using aggregation pipelines.
- Push filtering into Mongo queries instead of post-processing large in-memory lists.

#### 21. Auditing (SOC2)

- Every write through `ApplicationRepository` (`create`, `update`, `update_fields`, `delete`) is audited automatically. You do not add audit calls in views, services, readers, or writers — the base repository records the resource type, resource id, actor, action, and (on update) the changed fields. Keep audit code out of the execution and domain layers.
- Every mutating repository method takes a required `actor: AuditActor` keyword argument, threaded explicitly from the boundary through the service and writer. There is no ambient context; the type checker proves at compile time that no write happens without an actor. Choose the actor by whether identity is proven at the write: `AuditActor(ActorType.ACCOUNT, account_id)` when the credential/token in hand identifies an account (authenticated mutations, login OTP verify and access-token creation, password-reset completion); `AuditActor(ActorType.JOB, job_run_id)` for a background job execution, where the id is the `job_run` record for that run so every write the job makes joins back to a concrete run (the `Job` base builds this actor and passes it into `perform`, never a class name); `AuditActor(ActorType.WORKER, "<name>")` for a seed or system flow with no job run, and for the `job_run` record's own first write before its id exists; `AuditActor(ActorType.ANONYMOUS, None)` for a request with no proven identity yet (signup, OTP request/creation, forgot-password token request). There is no opt-out — completeness is the point.
- Never store a secret's value in the trail. The writer redacts sensitive field values (`password`, `token`, `secret`, `otp`, `mfa`, `hashed`); do not defeat this by renaming a sensitive field.
- Every entry carries an `outcome`: `success` (the default) or `denied`. All create/read/update/delete audits are `success`; the field is defaulted, so existing emission paths and stored rows are unchanged. A `denied` entry records an authenticated account that was rejected for crossing an ownership boundary: the auth middleware (`enforce_account_ownership`) emits one `outcome=denied` READ entry against the target account boundary before raising, with the real authenticated account as actor. Missing, invalid, or expired token rejections have no proven actor and are not audited.
- For the rare access a custom method performs that the generic CRUD does not cover, call `AuditService.record_audit(...)`. This should be uncommon; if you find yourself using it often, the data access likely belongs in a repository.

---

### Frontend-Specific Guidelines

#### 22. Styling Practices (Design System)

The frontend uses a token-driven design system. The full contract is in [Frontend Design System](docs/frontend-design-system.md). In review:

- **DON'T** pass `className` to raw DOM elements in `src/apps/frontend/pages/**`, and never use inline `style`. This is lint-enforced.
- **DON'T** reach for raw Tailwind spacing or color on a page. Use layout primitives (`Stack`, `Inline`, `Grid`) with `Spacing` gap tokens, and the semantic theme colors in `tailwind.config.js`.
- **DO** assemble pages from design-system components imported from `frontend/components`.

#### 23. Component Contracts & Variants

- Presentation is selected through tokens — `variant`, `size`, `gap` — not class strings. A look an existing component does not offer is a missing variant: add it to the component, do not inline it on the page.
- Interfaces are idiomatic, not consumer-shaped. Follow shadcn / Radix / Bootstrap / MUI: `variant` for status colour (the `Status` token), native events on form `onChange`, `checked` / `onCheckedChange` for `Switch` and `Checkbox`, `src` / `fallback` for `Avatar`, `DataTable` for the data grid.
- Never declare a `children` field in a Props interface or type. Type the component as `React.FC<PropsWithChildren<XProps>>`; for non-JSX content (a markdown string) use a named prop like `content`. Lint-enforced.
- A component's public props must not accept a `className` escape hatch. className and Tailwind classes live inside components only.
- Shared components and layout primitives live under `src/apps/frontend/components`, never in page folders.
- Every component declares an optional `testId?: string` and renders it as `data-testid` on its root element, icons and decorative primitives included. Tests address the UI through stable `data-testid` hooks, never brittle text or class selectors.
- Every component is accessible. An icon or shape that carries meaning exposes an accessible name (`ariaLabel` / `label`) and drops `aria-hidden`; a purely decorative glyph stays `aria-hidden`. An interactive element is a real semantic element (`button`, `a`, `input`) or carries the correct `role` plus keyboard handling. A form control associates its label and its error or description (`htmlFor` / `aria-describedby` / `aria-invalid`), and signals busy, expanded, or selected state with the right `aria-*` attribute. A component whose meaning or interactivity is not reachable by a screen reader or keyboard is incomplete; review rejects it.
- Reuse a catalogue component before writing new markup. If the component you need does not exist, build it under `frontend/components`, drive it with tokens, and export it from the barrel. Break long components and deeply nested JSX into smaller, named pieces.

#### 24. File Naming and Language Use

- All frontend files (TypeScript, TSX) use kebab-case names, for example `panel-header.tsx`, `chat-bubble-icon.tsx`. Never PascalCase or camelCase for file names. Split a TSX file that holds several independently reusable components into kebab-case files (`add-user-modal.tsx`, `reset-password-modal.tsx`).
- TypeScript interfaces and types use camelCase fields. No snake_case properties on frontend types.
- Use `async`/`await` for all async work, never `.then()` / `.catch()` chains.

#### 25. Data Fetching & State

- Fetch data through service modules under `services/` or `api/`.
- Normalize API responses into typed models before storing them in state.
- Avoid performing side-effectful data fetching inside render without hooks.

#### 26. List Rendering Performance

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

**Audit-log facts must come from something the user cannot fake.** Never record a client header like `X-Forwarded-For` as the actor's IP. Use `request.remote_addr`, which `ProxyFix` already sets correctly behind the trusted proxy (see `web_app.py`). Also make sure a failed action still writes its audit event, including when the route fails by raising. An audit trail the user can forge or skip is not a trail.

## Testing Requirements

- Add or update pytest coverage for new backend endpoints or services (`tests/modules/...`).
- Place integration tests alongside module directories under `tests/modules/<module>/`.
- CI enforces a hard coverage floor and fails the build below it: **80% backend**, **35% frontend**. These
  are floors, not targets. The `test-backend` and `test-frontend` jobs each run `CodeCoverageSummary` with
  `fail_below_min: true` and fail the check on a shortfall. Backend tests run with coverage via `npm run test`
  or `make run-test`; the frontend suite runs via `npm run test:frontend -- --coverage`. See
  [Testing Guide](docs/testing.md) for why each floor sits where it does and how to move one.

### Never mock MongoDB or Redis

The test stack runs both for real. `npm run test` brings up Mongo, and `tests/conftest.py` purges the
Celery broker queues around every test so the broker is a live one, not a stand-in. A test that patches
a repository, the Mongo client, or the broker proves nothing about the integration it stands in for: it
asserts that the mock was called the way the test author expected, which is the same thing the test
author already believed.

### Never mock our own code

Not a service, reader, writer, repository, or client class. Those are the code under test. Mocking one
means the test passes whether or not the real thing works, and it goes on passing after the real thing
is refactored into something broken.

Build the state the test needs by going through the real path. `tests/modules/task/test_task_service.py`
creates a second account and a real task through the API, then makes a cross-account request against it.
Nothing is patched, so the test exercises the actual auth middleware, the actual repository, and the
actual ownership check.

For third-party APIs, replace them at the HTTP boundary with a fake server rather than patching the
client class. `tests/modules/core/test_health_check_job.py` stands up a real `HTTPServer` on a random
local port, points config at it, and asserts on what `HealthCheckJob` logs. The `requests` call is real
all the way to a socket; only the far end is ours.

### Prove the test can fail

A test that passes against broken code proves nothing. After writing it, break the thing it guards and
watch it go red before trusting it.

This is not optional for anything guarding an access control boundary. Comment out the ownership check,
run the test, confirm it fails, restore the check. A test asserting a 401 that would also pass against a
route with no check at all is worse than no test, because it reads as coverage.

### Cover the refusals

A feature whose tests only prove it works for the intended user has not been tested. Access control
does not fail loudly; it fails by quietly returning 200 to the wrong person.

Every route that takes an owner-scoped path parameter needs a test for the other account. The task suite
does this: it asserts the cross-account `PATCH` and `DELETE` are rejected, and then reads the record back
as its real owner to prove the data was not modified or deleted on the way to the rejection. The status
code alone is not the assertion; the unchanged record is.

## Writing Style

Documentation, pull request bodies, and commit messages use plain, simple English.

- Short paragraphs. One idea each.
- No emoji.
- No marketing tone. Describe what the change does and why, not how significant it is.
- No em-dashes. Use a period, a comma, a colon, or parentheses instead.

Write for a reader who has no background on the change. Say what the situation was, what the change does
about it, and what a reviewer should look at.

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
