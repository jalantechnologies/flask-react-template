import os
import urllib.parse
from abc import ABC, abstractmethod
from typing import ClassVar, Optional

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.server_api import ServerApi

from modules.config.config_service import ConfigService
from modules.logger.logger import Logger


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


class ApplicationRepository(ABC):
    _collection: Optional[Collection] = None

    @property
    @abstractmethod
    def collection_name(self) -> str:
        """Return collection name of the Repository"""
        pass

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
        return False
