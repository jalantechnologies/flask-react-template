# Comment write operations
#
# This module provides operations for comment data persistence.
# Follows same pattern as taskwriter
# 


from datetime import datetime
from bson.objectid import ObjectId
from pymongo import ReturnDocument
from modules.task.comments.internal.comment_reader import CommentReader
from modules.task.comments.internal.store import comment_model
from modules.task.comments.errors import CommentNotFoundError
from modules.task.comments.internal.store.comment_model import CommentModel
from modules.task.comments.internal.store.comment_repository import CommentRepository
from modules.task.comments.internal import comment_reader
from modules.task.comments.internal.comment_util import CommentUtil
from modules.task.comments.types import (
    CreateCommentParams,
    UpdateCommentParams,
    DeleteCommentParams,
    GetCommentParams,
    Comment,
    CommentDeletionResult
)

class CommentWriter:
    @staticmethod
    def create_comment(*, params: CreateCommentParams) -> Comment:
        """
        Create a new comment with automatic timestamp
        
        CREATION PROCESS:
        1. create CommentModel with auto-timestamps
        2. convert gto bson for database insertion
        3. insert document and retrieve with generated id
        4. convert back to busines object

        Timestamp handling:
        - created_at and updated_at set to same time
        - CommentModel.__post_init__() handles automatic timestamps
        - database insertion preserves timestamp precision
        - no manual timestamp manipulation needed

        Validation:
        - database schema validates required fields
        - CommentModel ensures proper data types
        - Parent task existence to be validated at service layer

        Errors:
        - Invalid content (empty string) -> Database validation error
        - Missing required fields -> Schema validation error
        - Database connection issues -> Connection error
        - Duplicate key constraints

        """

        comment_model = CommentModel(
            task_id=params.task_id,
            account_id=params.account_id,
            content=params.content
        )

        comment_bson = comment_model.to_bson()

        # insert into db
        insert_result = CommentRepository.collection().insert_one(comment_bson)

        # retrieve complete dicument with generated id
        created_comment_bson = CommentRepository.collection().find_one(
            {"_id": insert_result.inserted_id}
        )

        # convert back to business object
        return CommentUtil.convert_comment_bson_to_comment(created_comment_bson)
    
    @staticmethod
    def update_comment(*, params: UpdateCommentParams) -> Comment:
        """
        Update comment content with automatic timestamp refresh.

        UPDATE STRATEGY:
        - Atomic find_one_and_update operation
        - Security validation through compound filter
        - Automatic updated_at timestamp refresh
        - Return updated document in single operation

        SECURITY VALIDATION:
        - Requires exact match on comment_id, task_id, account_id

        CONTENT HANDLING:
        - Full content replacement (not partial update)
        - Content validation through database schema
        - Empty content prevented by schema constraints
        """

        update_document = {
            "$set": {
                "content": params.content,
                "updated_at": datetime.now()
            }
        }

        filter_query = {
            "_id": ObjectId(params.comment_id),
            "task_id": params.task_id,
            "account_id": params.account_id,
            "active": True
        }

        updated_comment_bson = CommentRepository.collection().find_one_and_update(
            filter_query,
            update_document,
            return_document=ReturnDocument.AFTER # Updated doc
        )

        if updated_comment_bson is None:
            raise CommentNotFoundError(comment_id=params.comment_id)
        
        return CommentUtil.convert_comment_bson_to_comment(updated_comment_bson)
    
    @staticmethod
    def delete_comment(*, params: DeleteCommentParams) -> CommentDeletionResult:
        """
        Soft delete comment by setting active=False.

        Strategy:
        - Sets active = false instead of removign document
        - preserves data for potential recovery
        - updates timestamp for audit trail
        - consistent with task deltion pattern

        Security process:
        1. Validate comment exists and user owns it
        2. Perform atomic soft delete update
        3. Return deletion confirmation with timestamp

        Validation approach:
        - First check exsistence/ownership via commentreader
        - perform atomic update on ObjectId

        """

        comment = CommentReader.get_comment(
            params= GetCommentParams(
                account_id=params.account_id,
                task_id=params.task_id,
                comment_id=params.comment_id
            )
        )

        deletion_time = datetime.now()

        # perform atomic soft delete operation
        updated_comment_bson = CommentRepository.collection().find_one_and_update(
            {"_id": ObjectId(comment.id)},
            {
                "$set": {
                    "active": False,
                    "updated_at": deletion_time
                }
            },
            return_document=ReturnDocument.AFTER
        )

        if updated_comment_bson is None:
            raise CommentNotFoundError(comment_id=params.comment_id)
        
        # Return deletion confirmation
        return CommentDeletionResult(
            comment_id=params.comment_id,
            deleted_at=deletion_time,
            success=True
        )
