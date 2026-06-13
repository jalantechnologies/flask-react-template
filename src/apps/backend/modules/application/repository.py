import dataclasses
import os
import urllib.parse
from abc import ABC, abstractmethod
from typing import Any, ClassVar, Optional

from bson import ObjectId
from bson.errors import InvalidId
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.server_api import ServerApi

from modules.application.common.types import PaginationParams, PaginationResult, QueryParams
from modules.config.config_service import ConfigService
from modules.logger.logger import Logger

# Storage-boundary shapes: the only heterogeneous maps in the repository layer. Naming them keeps the
# `dict[str, Any]` blur confined to the database edge and visible (see docs/backend-architecture.md).
type StoredDocument = dict[str, Any]
type StoreFilter = dict[str, Any]
type FieldUpdates = dict[str, Any]
type SortSpec = list[tuple[str, int]]  # direction is 1 asc / -1 desc, a convention the type can't express


class ApplicationRepositoryClient:
    _client: Optional[MongoClient] = None

    # TLS on the MongoDB connection is only enforced outside local development and the test suite,
    # where plaintext traffic to a loopback Mongo is expected.
    NON_TLS_EXEMPT_ENVS: ClassVar[frozenset[str]] = frozenset({"development", "testing"})

    @classmethod
    def get_client(cls) -> MongoClient:
        connection_caching = ConfigService[bool].get_value(key="mongodb.connection_caching")

        if connection_caching:
            if cls._client is None:
                cls._client = cls._create_client()

            return cls._client

        else:
            return cls._create_client()

    @classmethod
    def _create_client(cls) -> MongoClient:
        connection_uri = ConfigService[str].get_value(key="mongodb.uri")
        cls._warn_if_uri_lacks_tls(connection_uri)
        Logger.info(message=f"connecting to database - {connection_uri}")
        client = MongoClient(connection_uri, server_api=ServerApi("1"))
        Logger.info(message=f"connected to database - {connection_uri}")

        return client

    @classmethod
    def _warn_if_uri_lacks_tls(cls, connection_uri: str) -> None:
        # Plaintext Mongo traffic exposes credentials and data in transit to anyone on the network
        # segment (SOC 2 CC6.7, ISO 27001 A.10.1). Warn — non-fatal — when the URI does not opt into
        # TLS, since TLS may instead be terminated at the network layer (proxy, service mesh) without
        # appearing in the URI. See docs/mongodb-security.md.
        app_env = os.environ.get("APP_ENV", "development")
        if app_env in cls.NON_TLS_EXEMPT_ENVS:
            return

        parsed = urllib.parse.urlsplit(connection_uri)
        query_params = urllib.parse.parse_qs(parsed.query)

        has_tls = (
            parsed.scheme == "mongodb+srv"
            or query_params.get("tls", [""])[0].lower() == "true"
            or query_params.get("ssl", [""])[0].lower() == "true"
        )

        if not has_tls:
            Logger.warn(
                message=(
                    "MONGODB_URI does not appear to use TLS. In production this exposes data in transit. "
                    "Use mongodb+srv:// (e.g. MongoDB Atlas) or append ?tls=true&tlsCAFile=/path/to/ca.pem "
                    "to a mongodb:// URI. See docs/mongodb-security.md for guidance."
                )
            )


class ApplicationRepository[EntityT, QueryT: QueryParams](ABC):
    """Generic MongoDB persistence base. A concrete repository declares only what is specific to its
    collection — `collection_name`, `on_init_collection` (indexes), `from_doc`, and `_to_filter` — and
    inherits the CRUD surface. It is the only place that knows about MongoDB, so no store detail
    (`ObjectId`, `$set`, filter dicts) crosses its public boundary. See docs/backend-architecture.md."""

    _collection: ClassVar[Optional[Collection]] = None

    collection_name: ClassVar[str]

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
    def create(cls, entity: EntityT) -> EntityT:
        doc = cls.to_doc(entity)
        result = cls.collection().insert_one(doc)
        return cls.from_doc({**doc, "_id": result.inserted_id})

    @classmethod
    def find(cls, entity_id: str) -> Optional[EntityT]:
        object_id = cls._to_object_id(entity_id)
        if object_id is None:
            return None
        doc = cls.collection().find_one({"_id": object_id})
        return cls.from_doc(doc) if doc is not None else None

    @classmethod
    def find_many(cls, entity_ids: list[str]) -> list[EntityT]:
        # $in returns store/index order, not entity_ids order; callers needing positional alignment must
        # build their own id->entity map rather than rely on this list order.
        object_ids = [oid for oid in (cls._to_object_id(eid) for eid in entity_ids) if oid is not None]
        cursor = cls.collection().find({"_id": {"$in": object_ids}})
        return [cls.from_doc(doc) for doc in cursor]

    @classmethod
    def query(cls, params: QueryT, *, sort: Optional[SortSpec] = None) -> list[EntityT]:
        # An explicit `sort` (including [] for "no ordering") wins; only None falls back to _to_sort.
        resolved_sort = sort if sort is not None else cls._to_sort(params)
        return cls._query(cls._to_filter(params), sort=resolved_sort)

    @classmethod
    def query_one(cls, params: QueryT, *, sort: Optional[SortSpec] = None) -> Optional[EntityT]:
        resolved_sort = sort if sort is not None else cls._to_sort(params)
        cursor = cls.collection().find(cls._to_filter(params))
        if resolved_sort:
            cursor = cursor.sort(resolved_sort)
        doc = next(iter(cursor.limit(1)), None)
        return cls.from_doc(doc) if doc is not None else None

    @classmethod
    def query_paginated(
        cls, params: QueryT, pagination: PaginationParams, *, sort: Optional[SortSpec] = None
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
        items = cls._query(store_filter, sort=resolved_sort, skip=skip, limit=pagination.size)
        return PaginationResult(
            items=items, pagination_params=pagination, total_count=total_count, total_pages=total_pages
        )

    @classmethod
    def count(cls, params: QueryT) -> int:
        return cls._count(cls._to_filter(params))

    @classmethod
    def update(cls, entity_id: str, fields: FieldUpdates) -> Optional[EntityT]:
        # Two round-trips (not atomic): a concurrent write can skew the read-back. Use update_fields()
        # to skip the read-back when the caller discards the result.
        if not cls.update_fields(entity_id, fields):
            return None
        return cls.find(entity_id)

    @classmethod
    def update_fields(cls, entity_id: str, fields: FieldUpdates) -> bool:
        # One-round-trip $set returning only whether a document matched; update() adds the read-back.
        object_id = cls._to_object_id(entity_id)
        if object_id is None:
            return False
        result = cls.collection().update_one({"_id": object_id}, {"$set": fields})
        return bool(result.matched_count > 0)

    @classmethod
    def delete(cls, entity_id: str) -> bool:
        object_id = cls._to_object_id(entity_id)
        if object_id is None:
            return False
        result = cls.collection().delete_one({"_id": object_id})
        return bool(result.deleted_count > 0)

    @classmethod
    def _query(
        cls, store_filter: StoreFilter, *, sort: Optional[SortSpec] = None, skip: int = 0, limit: int = 0
    ) -> list[EntityT]:
        cursor = cls.collection().find(store_filter)
        if sort:  # [] means "no ordering"; query() already resolved None -> _to_sort before calling
            cursor = cursor.sort(sort)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        return [cls.from_doc(doc) for doc in cursor]

    @classmethod
    def _find_one(cls, store_filter: StoreFilter, *, sort: Optional[SortSpec] = None) -> Optional[EntityT]:
        cursor = cls.collection().find(store_filter)
        if sort:
            cursor = cursor.sort(sort)
        doc = next(iter(cursor.limit(1)), None)
        return cls.from_doc(doc) if doc is not None else None

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
