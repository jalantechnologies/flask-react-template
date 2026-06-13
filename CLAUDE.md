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

A repository extends `ApplicationRepository[Entity, Query]` (in `modules/application/repository.py`) and
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
