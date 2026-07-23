# CLAUDE.md

Guidance for working in this repository. See `docs/backend-architecture.md` and
`docs/frontend-architecture.md` for the longer form.

## Backend module structure

The backend (`src/apps/backend`) is organised into **modules**, one per domain concept (account, task,
authentication, notification, …). A module exposes a `<module>_service.py` as its public API; other modules
call only the service, never a module's internals.

Inside a module:

- `internal/store/` — the persistence layer: a `*_model.py` (BSON dataclass) and a `*_repository.py`.
- `internal/*_reader.py` / `internal/*_writer.py` — business reads and writes.
- `internal/*_util.py` — pure helpers (hashing, generation, validation).
- `rest_api/` — Flask blueprint, router, and view.
- `types.py` / `errors.py` — DTOs (`@dataclass(frozen=True)`) and `AppError` subclasses.

Service methods are thin: they call the right reader or writer. Logic needed only internally (password
hashing, OTP generation) lives in the writer/util, not the service.

## Repositories inherit generic CRUD

A repository extends `ApplicationRepository[Entity, Query]` (in `modules/core/repository.py`) and
inherits the generic CRUD surface — do not re-implement these per repository:

- `create(entity)` — insert one, return the stored entity.
- `find(id)` / `find_many(ids)` — read by primary id.
- `query(params)` / `query_one(params)` — read many / at-most-one by a typed query object.
- `query_paginated(params, pagination)` — a page of `query()` results plus totals (`PaginationResult`).
  This is the only place pagination math lives.
- `count(params)` — how many match a typed query.
- `update(id, fields)` — patch fields on one by id, return the refreshed entity.
- `update_fields(id, fields)` — same `$set` without the read-back; returns `True` if a document matched.
  Use this in writers that patch and discard the result — one round-trip instead of two.
- `delete(id)` — remove one by id.

A malformed id is treated as "no such document" (the verb returns `None`/`False`), not an error.

A concrete repository declares only what is specific to its collection:

- `collection_name` — the Mongo collection name.
- `on_init_collection(collection)` — declares indexes and JSON-Schema validation.
- `from_doc(doc) -> Entity` — hydrates a stored document into the domain entity. **Required.**
- `to_doc(entity) -> StoredDocument` — serializes an entity for insertion. Override when the default is
  not enough — e.g. a separate `*Model` supplies stored-only fields (`active`, timestamps) the domain
  entity omits.
- `_to_filter(params) -> StoreFilter` — maps the module's typed query object to a store filter. Required
  only if the repository supports `query()`; a query-less repository (singleton, write-only log) declares
  `NoQuery` as its query type.
- `_to_sort(params) -> Optional[SortSpec]` — optional default ordering for `query()`/`query_paginated()`.

**No MongoDB syntax may cross the public surface.** Callers never write a `{"field": ...}` filter, an
`ObjectId`, or a `$set`. A field-combination read is a typed query object — `query(AccountQuery(username=x))`,
not `query({"username": x})` — and `_to_filter` is the single place domain fields become store syntax. Every
verb returns a domain dataclass (via `from_doc`), never a raw BSON document. The only intentionally untyped
values are the storage-boundary aliases `StoredDocument` / `StoreFilter` / `FieldUpdates` / `SortSpec` — use
those names, not bare `dict[str, Any]`, so the boundary is visible.

**A repository is pure storage.** Thin domain reads and writes do NOT live on it — they live on the module's
reader (reads) or writer (writes), which call the verbs. `AccountReader.get_account_by_username` is
`AccountRepository.query_one(AccountQuery(username=username))`; the account writer's soft-delete is
`AccountRepository.update_fields(id, {"active": False, ...})`. Do not add `find_by_<field>` /
`update_<field>` / `count_<thing>` methods to a repository — put them on the reader/writer.

The only methods that stay on a repository beyond the verbs are operations no CRUD verb can express, which is
exactly the code a storage swap would rewrite: an upsert or update by a natural key
(`AccountNotificationPreferencesRepository.update_by_account_id`), a create that keys store-shaped fields the
domain entity does not carry (`PasswordResetTokenRepository.create_for_account` keys `account` as an
`ObjectId`), an atomic `$inc`/`$push`, an aggregation, a `distinct`. Implement these with the protected
helpers (`_query`, `_find_one`, `_count`, `_to_object_id`) where possible; reach for the raw `collection()`
only when the operation genuinely has no helper form.

Soft-deleted collections (account, task, notification preferences) carry an `active` flag; their query
objects default `active=True`, so reads see only live records and the soft-delete is a single
`update_fields(id, {"active": False, ...})` on the writer.

> The generic base uses Python 3.12 type-parameter syntax (`class ApplicationRepository[Entity, Query]:`,
> `type StoredDocument = ...`). The backend runs and is checked on Python 3.12.

## Tooling

- Tests run against MongoDB; `npm run test` (or `make run-test`) runs the backend suite.
- `make run-lint` runs `mypy` (strict) and a `pylint` cyclic-import check; `make run-format` /
  `make run-format-check` run autoflake + isort + black (line length 120). Keep all green before pushing.

## Frontend file naming

All frontend files (TypeScript, TSX) use kebab-case names, for example `panel-header.tsx`, `chat-bubble-icon.tsx`. Never PascalCase or camelCase for file names. TypeScript interfaces and types use camelCase fields. No snake_case properties on frontend types.

## Frontend: ES6

Use `async/await` for all async work, not `.then()/.catch()` chains.

## Frontend: design system

Building a page is assembling Lego, not writing CSS. A page identifies the generic components it needs, lays them out with layout primitives, and selects presentation through tokens. The full contract is in `docs/frontend-design-system.md`; the rules below are enforced in review.

**No custom CSS on pages.** A file under `src/apps/frontend/pages` must not pass `className` to a raw DOM element (`div`, `button`, `span`, `input`, …) and must never use inline `style`. Compose the page from design-system components (`frontend/components`) and layout primitives instead. This is lint-enforced.

**Select presentation through tokens, not classes.** Components expose `variant`, `size`, and `gap` props (`Variant.Primary`, `Size.Sm`, `Status.Danger`, `Spacing.Md`). Pick a token, do not hand-write Tailwind. If you want a look the component does not offer, the component is missing a variant. Add the variant to the component under `frontend/components`; do not inline it on the page. A component's public API must not accept a `className` escape hatch.

**Idiomatic component interfaces.** Generic components follow ecosystem conventions (shadcn / Radix / Bootstrap / MUI), not consumer-specific shaping: `variant` for status colour (the `Status` token), native change events on form `onChange` (`onChange={(e) => setX(e.target.value)}`), Radix `checked` / `onCheckedChange` for `Switch` and `Checkbox`, `src` / `fallback` for `Avatar`. The data grid is `DataTable`.

**Children via `PropsWithChildren`.** Never declare a `children` field in a Props interface or type. Type the component as `React.FC<PropsWithChildren<XProps>>`. If the content is data rather than JSX (e.g. a markdown string), make it a named prop like `content`. This is lint-enforced.

**Lay out with primitives, space with gap tokens.** Vertical and horizontal arrangement comes from `Stack` and `Inline`; page chrome from `Page`, `PageBody`, `Toolbar`, `Grid`. Gaps come from the `Spacing` scale (`Xs`, `Sm`, `Md`, `Lg`, `Xl`, `Xxl`), never a raw `gap-*` or `space-y-*` class.

**Theme tokens, not raw palette.** Colors come from the semantic theme in `tailwind.config.js` (`primary`, `surface`, `line`, `content`, `danger`, `success`, …). Components reference these names; never `gray-900` or a hex value.

**Every component takes a `testId` and forwards it.** A generic component declares an optional `testId?: string` prop and renders it as `data-testid={testId}` on its root element (icons and decorative primitives included). Tests and automation address the UI through stable `data-testid` hooks, never brittle text or class selectors. A new component without `testId` is incomplete; review rejects it.

**Every component is accessible.** Accessibility is part of the interface, not an afterthought:

- An icon or shape that conveys meaning on its own exposes an accessible name (`ariaLabel` / `label`) and drops `aria-hidden`; a purely decorative glyph stays `aria-hidden`. Icons default to decorative — make them meaningful explicitly when they carry information.
- An interactive element is a real semantic element (`button`, `a`, `input`) or carries the correct `role` plus keyboard handling. An icon-only control requires a `label` that becomes its accessible name.
- A form control associates its label and its error/description (`htmlFor` / `aria-describedby` / `aria-invalid`), and signals busy/expanded/selected state with the right `aria-*` attribute.

A component whose meaning or interactivity is not reachable by a screen reader or keyboard is incomplete; review rejects it.

Reuse a catalogue component before writing new markup. If the component you need does not exist, build it under `frontend/components`, drive it with tokens, and export it from the barrel. Split a TSX file that holds several independently reusable components into kebab-case files (`add-user-modal.tsx`, `reset-password-modal.tsx`). Break long components and deeply nested JSX into smaller, named pieces.
