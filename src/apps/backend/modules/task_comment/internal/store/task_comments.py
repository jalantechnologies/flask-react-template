from datetime import datetime
from typing import List, Optional, Dict, Any
from bson import ObjectId

from pymongo.collection import Collection
from pymongo.errors import OperationFailure
from pymongo import DESCENDING, ASCENDING

from modules.application.repository import ApplicationRepository
from modules.task_comment.internal.store.task_comment_model import TaskCommentModel
from modules.logger.logger import Logger

# MongoDB validation schema for task comments
TASK_COMMENT_VALIDATION_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["task_id", "account_id", "content", "created_at", "updated_at"],
        "properties": {
            "task_id": {
                "bsonType": "string",
                "description": "ID of the task this comment belongs to"
            },
            "account_id": {
                "bsonType": "string", 
                "description": "ID of the user who created the comment"
            },
            "content": {
                "bsonType": "string",
                "minLength": 1,
                "maxLength": 1000,
                "description": "Comment content"
            },
            "created_at": {
                "bsonType": "date",
                "description": "Comment creation timestamp"
            },
            "updated_at": {
                "bsonType": "date",
                "description": "Last update timestamp"
            }
        }
    }
}


class TaskCommentRepository(ApplicationRepository):
    """Repository for task comment operations using MongoDB"""
    
    collection_name = TaskCommentModel.get_collection_name()

    @classmethod
    def on_init_collection(cls, collection: Collection) -> bool:
        """Initialize collection with indexes and validation"""
        
        # Create compound index for task comments (most common query)
        collection.create_index(
            [("task_id", 1), ("created_at", DESCENDING)], 
            name="task_id_created_at_index"
        )
        
        # Index for user's comments
        collection.create_index(
            [("account_id", 1), ("created_at", DESCENDING)],
            name="account_id_created_at_index"
        )
        
        # Full text search index on content
        collection.create_index(
            [("content", "text")],
            name="content_text_index"
        )

        # Add validation schema
        Logger.info(message=f"Adding validation schema for collection {cls.collection_name}")
        add_validation_command = {
            "collMod": cls.collection_name,
            "validator": TASK_COMMENT_VALIDATION_SCHEMA,
            "validationLevel": "strict",
        }

        try:
            collection.database.command(add_validation_command)
        except OperationFailure as e:
            if e.code == 26:  # Collection doesn't exist
                collection.database.create_collection(
                    cls.collection_name, 
                    validator=TASK_COMMENT_VALIDATION_SCHEMA
                )
            else:
                Logger.error(message=f"OperationFailure occurred for collection {cls.collection_name}: {e.details}")
        
        return True
    
    @classmethod
    def create_comment(cls, comment_data: dict) -> TaskCommentModel:
        """Create a new task comment"""
        comment_model = TaskCommentModel(
            task_id=comment_data["task_id"],
            account_id=comment_data["account_id"],
            content=comment_data["content"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Insert into MongoDB
        result = cls.collection().insert_one(comment_model.to_bson())
        comment_model.id = result.inserted_id
        
        Logger.info(message=f"Created comment {comment_model.id} for task {comment_model.task_id}")
        return comment_model
    
    @classmethod
    def get_comment_by_id(cls, comment_id: str) -> Optional[TaskCommentModel]:
        """Get a single comment by ID"""
        try:
            object_id = ObjectId(comment_id)
            document = cls.collection().find_one({"_id": object_id})
            
            if document:
                return TaskCommentModel.from_bson(document)
            return None
            
        except Exception as e:
            Logger.error(message=f"Error getting comment by id {comment_id}: {str(e)}")
            return None
    
    @classmethod
    def get_comments_by_task(
        cls,
        task_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[TaskCommentModel]:
        """Get all comments for a task with pagination"""
        
        cursor = cls.collection().find(
            {"task_id": task_id}
        ).sort(
            "created_at", DESCENDING
        ).skip(skip).limit(limit)
        
        comments = []
        for document in cursor:
            comments.append(TaskCommentModel.from_bson(document))
        
        return comments
    
    @classmethod
    def count_comments_by_task(cls, task_id: str) -> int:
        """Count total comments for a task"""
        return cls.collection().count_documents({"task_id": task_id})
    
    @classmethod
    def update_comment(cls, comment_id: str, content: str) -> bool:
        """Update comment content"""
        try:
            object_id = ObjectId(comment_id)
            result = cls.collection().update_one(
                {"_id": object_id},
                {
                    "$set": {
                        "content": content,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            Logger.error(message=f"Error updating comment {comment_id}: {str(e)}")
            return False
    
    @classmethod
    def delete_comment(cls, comment_id: str) -> bool:
        """Delete a comment permanently"""
        try:
            object_id = ObjectId(comment_id)
            result = cls.collection().delete_one({"_id": object_id})
            return result.deleted_count > 0
                
        except Exception as e:
            Logger.error(message=f"Error deleting comment {comment_id}: {str(e)}")
            return False
    
    @classmethod
    def search_comments(
        cls,
        search_text: str,
        task_id: Optional[str] = None,
        account_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[TaskCommentModel]:
        """Search comments using text search"""
        
        # Build query
        query = {"$text": {"$search": search_text}}
        
        if task_id:
            query["task_id"] = task_id
        if account_id:
            query["account_id"] = account_id
        
        # Execute search with relevance score
        cursor = cls.collection().find(
            query,
            {"score": {"$meta": "textScore"}}
        ).sort(
            [("score", {"$meta": "textScore"})]
        ).skip(skip).limit(limit)
        
        comments = []
        for document in cursor:
            comments.append(TaskCommentModel.from_bson(document))
        
        return comments
    
    @classmethod
    def get_user_comments(
        cls,
        account_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[TaskCommentModel]:
        """Get all comments by a specific user"""
        
        cursor = cls.collection().find(
            {"account_id": account_id}
        ).sort(
            "created_at", DESCENDING
        ).skip(skip).limit(limit)
        
        comments = []
        for document in cursor:
            comments.append(TaskCommentModel.from_bson(document))
        
        return comments
    
    @classmethod
    def bulk_delete_task_comments(cls, task_id: str) -> int:
        """Delete all comments for a task (when task is deleted)"""
        result = cls.collection().delete_many({"task_id": task_id})
        
        Logger.info(message=f"Deleted {result.deleted_count} comments for task {task_id}")
        return result.deleted_count