from datetime import datetime
from typing import Dict, Any

from modules.task_comment.types import TaskComment
from modules.logger.logger import Logger


class TaskCommentUtil:
    """Utility class for task comment operations"""
    
    @staticmethod
    def convert_comment_bson_to_comment(comment_bson: Dict[str, Any]) -> TaskComment:
        """
        Convert MongoDB BSON document to TaskComment domain model
        
        Args:
            comment_bson: BSON document from MongoDB
            
        Returns:
            TaskComment: Domain model object
        """
        try:
            # Handle ObjectId conversion
            comment_id = str(comment_bson["_id"]) if comment_bson.get("_id") else None
            
            # Handle datetime fields
            created_at = comment_bson.get("created_at", datetime.utcnow())
            updated_at = comment_bson.get("updated_at", datetime.utcnow())
            
            # Create TaskComment object
            return TaskComment(
                id=comment_id,
                task_id=comment_bson.get("task_id", ""),
                account_id=comment_bson.get("account_id", ""),
                content=comment_bson.get("content", ""),
                created_at=created_at,
                updated_at=updated_at
            )
            
        except Exception as e:
            Logger.error(message=f"Error converting BSON to TaskComment: {str(e)}")
            raise
    
    @staticmethod
    def convert_comment_bson_to_dict(comment_bson: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert MongoDB BSON document to dictionary
        
        Args:
            comment_bson: BSON document from MongoDB
            
        Returns:
            Dict: Dictionary representation of the comment
        """
        try:
            # Handle ObjectId conversion
            comment_id = str(comment_bson["_id"]) if comment_bson.get("_id") else None
            
            # Handle datetime fields
            created_at = comment_bson.get("created_at", datetime.utcnow())
            updated_at = comment_bson.get("updated_at", datetime.utcnow())
            
            return {
                "id": comment_id,
                "task_id": comment_bson.get("task_id", ""),
                "account_id": comment_bson.get("account_id", ""),
                "content": comment_bson.get("content", ""),
                "created_at": created_at,
                "updated_at": updated_at
            }
            
        except Exception as e:
            Logger.error(message=f"Error converting BSON to dict: {str(e)}")
            raise
    
    @staticmethod
    def validate_comment_content(content: str) -> bool:
        """
        Validate comment content
        
        Args:
            content: Comment content to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not content or len(content.strip()) == 0:
            return False
        
        if len(content) > 1000:
            return False
        
        return True
    
    @staticmethod
    def sanitize_comment_content(content: str) -> str:
        """
        Sanitize comment content by stripping whitespace and limiting length
        
        Args:
            content: Raw comment content
            
        Returns:
            str: Sanitized content
        """
        # Strip leading/trailing whitespace
        sanitized = content.strip()
        
        # Limit length (truncate if necessary)
        if len(sanitized) > 1000:
            sanitized = sanitized[:997] + "..."
        
        return sanitized
    
    @staticmethod
    def format_comment_for_display(comment: TaskComment) -> Dict[str, Any]:
        """
        Format a comment for display in the UI
        
        Args:
            comment: TaskComment object
            
        Returns:
            Dict: Formatted comment data
        """
        return {
            "id": comment.id,
            "task_id": comment.task_id,
            "account_id": comment.account_id,
            "content": comment.content,
            "created_at": comment.created_at.isoformat() if isinstance(comment.created_at, datetime) else str(comment.created_at),
            "updated_at": comment.updated_at.isoformat() if isinstance(comment.updated_at, datetime) else str(comment.updated_at),
            "time_ago": TaskCommentUtil.get_time_ago(comment.created_at)
        }
    
    @staticmethod
    def get_time_ago(timestamp: datetime) -> str:
        """
        Get human-readable time difference
        
        Args:
            timestamp: DateTime to compare
            
        Returns:
            str: Human-readable time difference (e.g., "2 hours ago")
        """
        now = datetime.utcnow()
        
        # Ensure timestamp is datetime
        if not isinstance(timestamp, datetime):
            return "Unknown time"
        
        diff = now - timestamp
        
        # Calculate time differences
        seconds = diff.total_seconds()
        minutes = seconds / 60
        hours = minutes / 60
        days = hours / 24
        weeks = days / 7
        months = days / 30
        years = days / 365
        
        # Return appropriate string
        if seconds < 60:
            return "just now"
        elif minutes < 60:
            mins = int(minutes)
            return f"{mins} minute{'s' if mins != 1 else ''} ago"
        elif hours < 24:
            hrs = int(hours)
            return f"{hrs} hour{'s' if hrs != 1 else ''} ago"
        elif days < 7:
            d = int(days)
            return f"{d} day{'s' if d != 1 else ''} ago"
        elif weeks < 4:
            w = int(weeks)
            return f"{w} week{'s' if w != 1 else ''} ago"
        elif months < 12:
            m = int(months)
            return f"{m} month{'s' if m != 1 else ''} ago"
        else:
            y = int(years)
            return f"{y} year{'s' if y != 1 else ''} ago"
    
    @staticmethod
    def check_edit_time_limit(created_at: datetime, limit_days: int = 7) -> bool:
        """
        Check if a comment is still within the edit time limit
        
        Args:
            created_at: Comment creation timestamp
            limit_days: Number of days after which editing is disabled
            
        Returns:
            bool: True if still editable, False if time limit exceeded
        """
        if not isinstance(created_at, datetime):
            return False
        
        time_since_creation = datetime.utcnow() - created_at
        return time_since_creation.days <= limit_days