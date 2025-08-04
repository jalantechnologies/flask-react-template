from logging import Logger
from pymongo.collection import Collection
from pymongo.errors import OperationFailure
from modules.application.repository import ApplicationRepository
from modules.task.comments.internal.store.comment_model import CommentModel

COMMENT_VALIDATION_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["task_id", "account_id", "content", "active", "created_at", "updated_at"],
        "properties": {
            "task_id": {
                "bsonType": "string",
                "description": "Parent task id, required reference",
            },
            "account_id": {
                "bsonType": "string",
                "description": "comment owner account id, required for security",
            },
            "content": {
                "bsonType": "string",
                "minLength": 1,
                "description": "Comment text content, required non-empty string",
            },
            "active": {
                "bsonType": "bool",
                "description": "soft delete flag, required"
            },
            "created_at": {
                "bsonType": "date",
                "description": "Creation timestamp - required date"
            },
            "updated_at": {
                "bsonType": "date", 
                "description": "Last update timestamp - required date"
            }
            
        }
    }
}

class CommentRepository(ApplicationRepository):
    """
    Mongodb repository for comment operations

    Inheritence: Extends ApplicationRepository for consistent database patterns
    - PRovides base collection management facility
    - handles collection pooling and error handling
    
    Management:
    - auto initialises collection with validation and indexes
    - handles schema migrationa nd version compatibility
    - provides centralised collection access point
    """

    collection_name = CommentModel.get_collection_name()

    @classmethod
    def on_init_collection(cls, collection: Collection) -> bool:
        """
        Indexing strategy:
        1. Primary index: (task_id, active, account_id)
            - most queries filter by task_id first
            - then filter by active status (exclude deleted)
            - finally by account_id for security
            - enables fast comment retrieval for task viewing
        2. Account index: (account_id, active)
            - for user-level operations (Get all user comments)
            - partial index on active documents only
            - supports cross task comemnt operations

        3. chrnological index: (created_at)
            - for time-based  sorting and pagination
            - used in combination with other indexes
            - supports chronological comment display

        TradeOffs:
        - More indexes = faster reads, slower writes
        - decision: optmise for reads, it will be a read heavy system
        """

        collection.create_index(
            [("task_id", 1), ("active", 1), ("account_id", 1)],
            name="task_active_account_index",
            partialFilterExpression={"active": True}
        )

        collection.create_index(
            [("account_id", 1), ("active", 1)],
            name="account_active_index",
        )

        collection.create_index(
            [("created_at", -1)],  # Descending: newest first
            name="created_at_desc_index"
        )

        # apply validation for data integrity
        add_validation_command = {
            "collMod": cls.collection_name,
            "validator": COMMENT_VALIDATION_SCHEMA,
            "validationLevel": "strict", # Reject invalid documents
        }

        try:
            collection.database.command(add_validation_command)
        except OperationFailure as e:
            if e.code == 26: # NamespaceNotFound - collection doesn't exist
                # create new collection with validation schema
                collection.database.create_collection(
                    cls.collection_name,
                    validator=COMMENT_VALIDATION_SCHEMA
                )
            else:
                # log other operation failures for monitoring
                Logger.error(
                    message=f"OperationFailure occurred for collection {cls.collection_name}: {e.details}"
                )
        return True
    