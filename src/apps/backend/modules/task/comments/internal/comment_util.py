from typing import Any
from modules.task.comments.internal.store.comment_model import CommentModel
from modules.task.comments.types import Comment

class CommentUtil:
    """
    Utility class for comment data transformations

    Single responsibility: Data conversion between layers
    - Database layer (BSON) -> Model layer (CommentModel)
    - Model layer (CommentModel) -> Model layer (Comment)
    - Ensures type safety and validation at each step

    Design pattern: Static utility class
    - No state required, pure function
    - Easy to test and reason about
    - Consistent with TaskUtil pattern
    """

    @staticmethod
    def convert_comment_bson_to_comment(comment_bson: dict[str, Any]) -> Comment:
        """
        Convert MongoDB BSON document to business logic Comment object

        Conversion process:
        - BSON dict -> CommentModel (with validation)
        - CommentModel -> Comment (business object)

        Data transforamtions:
        - ObjectId -> string for (API serialisaton)
        - MongoDB field names -> business field names
        - Timestamp preservation (no timezone conversion)
        - Validation through comment model

        Assumptions:
        - comment_bson contains valid MongoDB document
        - CommentModel.from_bson() handles missing fields gracefully
        - Comment dataclass matches business requirements
        - no additional business logic transformation needed

        Error handling:
        - relies on CommentModel.from_bson() for validation
        - any missing required fields will use model defaults
        - invalid data types will raise appropriate exceptions
        """

        validated_comment_data = CommentModel.from_bson(comment_bson)

        # Convert to immutable business object with proper types
        return Comment(
            id=str(validated_comment_data.id),  # ObjectId -> string
            task_id=validated_comment_data.task_id,
            account_id=validated_comment_data.account_id,
            content=validated_comment_data.content,
            created_at=validated_comment_data.created_at,
            updated_at=validated_comment_data.updated_at
        )
        
