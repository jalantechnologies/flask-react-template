from abc import ABC, abstractmethod
from typing import Optional

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.server_api import ServerApi

from modules.config.config_service import ConfigService
from modules.logger.logger import Logger


class ApplicationRepositoryClient:
    _client: Optional[MongoClient] = None

    @classmethod
    def get_client(cls) -> MongoClient:
        connection_caching = ConfigService.get_string(key="MONGODB_CONNECTION_CACHING", section="SERVER_CONFIG")=="True"

        if connection_caching:
            if cls._client is None:
                cls._client = cls._create_client()

            return cls._client

        else:
            return cls._create_client()

    @staticmethod
    def _create_client() -> MongoClient:
        connection_uri = ConfigService.get_string(key="MONGODB_URI", section="MONGODB")
        Logger.info(message=f"connecting to database - {connection_uri}")
        client = MongoClient(connection_uri, server_api=ServerApi("1"))
        Logger.info(message=f"connected to database - {connection_uri}")

        return client


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
