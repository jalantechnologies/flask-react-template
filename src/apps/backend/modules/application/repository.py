import dataclasses
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, ClassVar, Optional

if TYPE_CHECKING:
    from modules.application.common.types import AuditActor, FieldChanges, ResourceAction

from bson import ObjectId
from bson.errors import InvalidId
from pymongo import ReturnDocument
from pymongo.collection import Collection

from modules.application.common.types import PaginationParams, PaginationResult, QueryParams
from modules.application.repository_client import ApplicationRepositoryClient

# Storage-boundary shapes: the only heterogeneous maps in the repository layer. Naming them keeps the
# `dict[str, Any]` blur confined to the database edge and visible (see docs/backend-architecture.md).
type StoredDocument = dict[str, Any]
type StoreFilter = dict[str, Any]
type FieldUpdates = dict[str, Any]
type SortSpec = list[tuple[str, int]]  # direction is 1 asc / -1 desc, a convention the type can't express

__all__ = [
    "ApplicationRepository",
    "ApplicationRepositoryClient",
    "StoredDocument",
    "StoreFilter",
    "FieldUpdates",
    "SortSpec",
]


class ApplicationRepository[EntityT, QueryT: QueryParams](ABC):
    """Generic MongoDB persistence base. A concrete repository declares only what is specific to its
    collection — `collection_name`, `on_init_collection` (indexes), `from_doc`, and `_to_filter` — and
    inherits the CRUD surface. It is the only place that knows about MongoDB, so no store detail
    (`ObjectId`, `$set`, filter dicts) crosses its public boundary. See docs/backend-architecture.md."""

    _collection: ClassVar[Optional[Collection]] = None

    collection_name: ClassVar[str]

    audit_resource_type: ClassVar[Optional[str]] = None

    AUDIT_COLLECTION_NAME: ClassVar[str] = "audit_log"

    @classmethod
    def _resource_type(cls) -> str:
        return cls.audit_resource_type or cls.collection_name

    @classmethod
    def _audits(cls) -> bool:
        return cls.collection_name != cls.AUDIT_COLLECTION_NAME

    @classmethod
    def _emit_audit(
        cls, actor: "AuditActor", resource_id: str, action: "ResourceAction", changes: Optional["FieldChanges"] = None
    ) -> None:
        if not cls._audits():
            return
        from modules.application.internal.audit.audit_writer import AuditWriter

        AuditWriter.record(
            actor=actor, resource_type=cls._resource_type(), resource_id=resource_id, action=action, changes=changes
        )

    @classmethod
    def collection(cls) -> Collection:
        if cls._collection is None:
            client = ApplicationRepositoryClient.get_client()
            database = client.get_database()
            collection = database[cls.collection_name]

            # init hook
            cls.on_init_collection(collection)

            cls._collection = collection

        return cls._collection

    @classmethod
    def on_init_collection(cls, collection: Collection) -> bool:
        # Override to declare indexes (and any one-time index migrations) for this collection. Runs
        # once, lazily, the first time the collection is accessed.
        return False

    @classmethod
    @abstractmethod
    def from_doc(cls, doc: StoredDocument) -> EntityT:
        """Hydrate a stored document into the domain entity. Required for every repository."""
        ...

    @classmethod
    def to_doc(cls, entity: EntityT) -> StoredDocument:
        # Default serialization for any dataclass (or an object exposing `to_bson`); override for a
        # custom mapping (a separate storage model, nested value objects, an enum stored differently).
        to_bson = getattr(entity, "to_bson", None)
        if callable(to_bson):
            doc: StoredDocument = to_bson()
        elif dataclasses.is_dataclass(entity) and not isinstance(entity, type):
            doc = dataclasses.asdict(entity)
        else:
            raise TypeError(f"{cls.__name__}.to_doc cannot serialize {type(entity)!r}; override to_doc")
        # MongoDB owns identity: drop any domain id so insert assigns a fresh ObjectId.
        doc.pop("id", None)
        doc.pop("_id", None)
        return doc

    # Not @abstractmethod intentionally: NoQuery repos never override it; required only when query() is used.
    @classmethod
    def _to_filter(cls, params: QueryT) -> StoreFilter:
        raise NotImplementedError(f"{cls.__name__} does not support query(); implement _to_filter")

    @classmethod
    def _to_sort(cls, params: QueryT) -> Optional[SortSpec]:
        # Default: no ordering. Override to translate a query object's sort intent into a store sort.
        return None

    @classmethod
    def create(cls, entity: EntityT, *, actor: "AuditActor") -> EntityT:
        from modules.application.common.types import ResourceAction

        doc = cls.to_doc(entity)
        result = cls.collection().insert_one(doc)
        created = cls.from_doc({**doc, "_id": result.inserted_id})
        cls._emit_audit(actor, str(result.inserted_id), ResourceAction.CREATE)
        return created

    @classmethod
    def find(cls, entity_id: str, *, actor: "AuditActor") -> Optional[EntityT]:
        object_id = cls._to_object_id(entity_id)
        if object_id is None:
            return None
        doc = cls.collection().find_one({"_id": object_id})
        if doc is None:
            return None
        cls._emit_read_audit(actor, [str(doc["_id"])])
        return cls.from_doc(doc)

    @classmethod
    def find_many(cls, entity_ids: list[str], *, actor: "AuditActor") -> list[EntityT]:
        # $in returns store/index order, not entity_ids order; callers needing positional alignment must
        # build their own id->entity map rather than rely on this list order.
        object_ids = [oid for oid in (cls._to_object_id(eid) for eid in entity_ids) if oid is not None]
        docs = list(cls.collection().find({"_id": {"$in": object_ids}}))
        cls._emit_read_audit(actor, [str(doc["_id"]) for doc in docs])
        return [cls.from_doc(doc) for doc in docs]

    @classmethod
    def query(cls, params: QueryT, *, actor: "AuditActor", sort: Optional[SortSpec] = None) -> list[EntityT]:
        # An explicit `sort` (including [] for "no ordering") wins; only None falls back to _to_sort.
        resolved_sort = sort if sort is not None else cls._to_sort(params)
        docs = cls._query_docs(cls._to_filter(params), sort=resolved_sort)
        cls._emit_read_audit(actor, [str(doc["_id"]) for doc in docs])
        return [cls.from_doc(doc) for doc in docs]

    @classmethod
    def query_one(cls, params: QueryT, *, actor: "AuditActor", sort: Optional[SortSpec] = None) -> Optional[EntityT]:
        resolved_sort = sort if sort is not None else cls._to_sort(params)
        cursor = cls.collection().find(cls._to_filter(params))
        if resolved_sort:
            cursor = cursor.sort(resolved_sort)
        doc = next(iter(cursor.limit(1)), None)
        if doc is None:
            return None
        cls._emit_read_audit(actor, [str(doc["_id"])])
        return cls.from_doc(doc)

    @classmethod
    def query_paginated(
        cls, params: QueryT, pagination: PaginationParams, *, actor: "AuditActor", sort: Optional[SortSpec] = None
    ) -> PaginationResult[EntityT]:
        # A page of query() results plus totals, sharing one filter/sort so each listing avoids repeated
        # count + skip + limit + total_pages arithmetic. This is the only place pagination math lives.
        store_filter = cls._to_filter(params)
        total_count = cls._count(store_filter)
        # size<=0 means "no page of items"; return empty rather than falling through to _query, where
        # limit=0 is pymongo's "no limit" and would scan the whole collection.
        if pagination.size <= 0:
            return PaginationResult(items=[], pagination_params=pagination, total_count=total_count, total_pages=0)
        skip = (pagination.page - 1) * pagination.size + pagination.offset
        total_pages = (total_count + pagination.size - 1) // pagination.size
        resolved_sort = sort if sort is not None else cls._to_sort(params)
        docs = cls._query_docs(store_filter, sort=resolved_sort, skip=skip, limit=pagination.size)
        cls._emit_read_audit(actor, [str(doc["_id"]) for doc in docs])
        return PaginationResult(
            items=[cls.from_doc(doc) for doc in docs],
            pagination_params=pagination,
            total_count=total_count,
            total_pages=total_pages,
        )

    @classmethod
    def count(cls, params: QueryT) -> int:
        return cls._count(cls._to_filter(params))

    @classmethod
    def _emit_read_audit(cls, actor: "AuditActor", resource_ids: list[str]) -> None:
        from modules.application.common.types import ResourceAction

        for resource_id in resource_ids:
            cls._emit_audit(actor, resource_id, ResourceAction.READ)

    @classmethod
    def _query_docs(
        cls, store_filter: StoreFilter, *, sort: Optional[SortSpec] = None, skip: int = 0, limit: int = 0
    ) -> list[StoredDocument]:
        cursor = cls.collection().find(store_filter)
        if sort:
            cursor = cursor.sort(sort)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        return list(cursor)

    @classmethod
    def update(cls, entity_id: str, fields: FieldUpdates, *, actor: "AuditActor") -> Optional[EntityT]:
        # Two round-trips (not atomic): a concurrent write can skew the read-back. Use update_fields()
        # to skip the read-back when the caller discards the result.
        if not cls.update_fields(entity_id, fields, actor=actor):
            return None
        # Read back the updated document directly (not via find()) so an update records only its UPDATE
        # entry, not an extra READ for the same operation the caller asked to be a write.
        object_id = cls._to_object_id(entity_id)
        doc = cls.collection().find_one({"_id": object_id}) if object_id is not None else None
        return cls.from_doc(doc) if doc is not None else None

    @classmethod
    def update_fields(cls, entity_id: str, fields: FieldUpdates, *, actor: "AuditActor") -> bool:
        # One atomic round-trip: find_one_and_update returns the document exactly as it was before the
        # $set, so the audit diff's `old` value cannot be skewed by a concurrent write between read and
        # write. Returning BEFORE keeps this a single Mongo call, preserving the one-round-trip contract.
        object_id = cls._to_object_id(entity_id)
        if object_id is None:
            return False
        if not fields:
            return cls._count({"_id": object_id}) > 0
        patch = {"updated_at": datetime.now(UTC), **fields}
        previous = cls.collection().find_one_and_update(
            {"_id": object_id}, {"$set": patch}, return_document=ReturnDocument.BEFORE
        )
        if previous is None:
            return False
        cls._emit_field_update_audit(actor, entity_id, fields, previous)
        return True

    @classmethod
    def _emit_field_update_audit(
        cls, actor: "AuditActor", entity_id: str, fields: "FieldUpdates", previous: StoredDocument
    ) -> None:
        from modules.application.common.types import FieldChange, ResourceAction

        changes = {
            name: FieldChange(old=cls._audit_scalar(previous.get(name)), new=cls._audit_scalar(new_value))
            for name, new_value in fields.items()
            if name not in ("updated_at", "created_at")
        }
        cls._emit_audit(actor, entity_id, ResourceAction.UPDATE, changes)

    @staticmethod
    def _audit_scalar(value: Any) -> Any:
        return value if isinstance(value, (str, int, float, bool)) or value is None else str(value)

    @classmethod
    def delete(cls, entity_id: str, *, actor: "AuditActor") -> bool:
        from modules.application.common.types import ResourceAction

        object_id = cls._to_object_id(entity_id)
        if object_id is None:
            return False
        result = cls.collection().delete_one({"_id": object_id})
        deleted = bool(result.deleted_count > 0)
        if deleted:
            cls._emit_audit(actor, entity_id, ResourceAction.DELETE)
        return deleted

    @classmethod
    def _count(cls, store_filter: Optional[StoreFilter] = None) -> int:
        return int(cls.collection().count_documents(store_filter or {}))

    @staticmethod
    def _to_object_id(entity_id: str) -> Optional[ObjectId]:
        # A malformed id is "no such document", not an exception, so callers can pass a path param
        # straight through without validating it first.
        try:
            return ObjectId(entity_id)
        except InvalidId:
            return None
