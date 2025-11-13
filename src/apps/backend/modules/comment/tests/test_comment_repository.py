import pytest
from datetime import datetime
from bson import ObjectId
from unittest.mock import Mock, patch, MagicMock

from modules.comment.internal.store.comment_model import CommentModel
from modules.comment.internal.store.comment_repository import CommentRepository


class TestCommentRepository:
    """Test suite for CommentRepository"""

    @pytest.fixture
    def sample_comment(self):
        """Fixture to create a sample comment"""
        return CommentModel(
            task_id="test_task_123",
            account_id="test_account_456",
            content="This is a test comment",
            active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    @pytest.fixture
    def mock_collection(self):
        """Fixture to create a mock MongoDB collection"""
        return Mock()

    @patch.object(CommentRepository, 'get_collection')
    def test_create_comment(self, mock_get_collection, sample_comment, mock_collection):
        """Test creating a new comment"""
        # Arrange
        mock_get_collection.return_value = mock_collection
        mock_result = Mock()
        mock_result.inserted_id = ObjectId()
        mock_collection.insert_one.return_value = mock_result

        # Act
        result = CommentRepository.create(sample_comment)

        # Assert
        assert result.id == mock_result.inserted_id
        assert result.content == "This is a test comment"
        assert result.task_id == "test_task_123"
        assert result.account_id == "test_account_456"
        mock_collection.insert_one.assert_called_once()

    @patch.object(CommentRepository, 'get_collection')
    def test_find_by_task_id(self, mock_get_collection, mock_collection):
        """Test retrieving comments by task_id"""
        # Arrange
        mock_get_collection.return_value = mock_collection
        
        mock_cursor = Mock()
        mock_cursor.sort.return_value = [
            {
                "_id": ObjectId(),
                "task_id": "test_task_123",
                "account_id": "test_account_456",
                "content": "Comment 1",
                "active": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "_id": ObjectId(),
                "task_id": "test_task_123",
                "account_id": "test_account_456",
                "content": "Comment 2",
                "active": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        ]
        mock_collection.find.return_value = mock_cursor

        # Act
        results = CommentRepository.find_by_task_id("test_task_123", "test_account_456")

        # Assert
        assert len(results) == 2
        assert results[0].content == "Comment 1"
        assert results[1].content == "Comment 2"
        mock_collection.find.assert_called_once_with({
            "task_id": "test_task_123",
            "account_id": "test_account_456",
            "active": True
        })
        mock_cursor.sort.assert_called_once_with("created_at", -1)

    @patch.object(CommentRepository, 'get_collection')
    def test_find_by_id(self, mock_get_collection, mock_collection):
        """Test retrieving a comment by ID"""
        # Arrange
        mock_get_collection.return_value = mock_collection
        comment_id = ObjectId()
        
        mock_collection.find_one.return_value = {
            "_id": comment_id,
            "task_id": "test_task_123",
            "account_id": "test_account_456",
            "content": "Test comment",
            "active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        # Act
        result = CommentRepository.find_by_id(str(comment_id), "test_account_456")

        # Assert
        assert result is not None
        assert result.id == comment_id
        assert result.content == "Test comment"
        mock_collection.find_one.assert_called_once()

    @patch.object(CommentRepository, 'get_collection')
    def test_find_by_id_not_found(self, mock_get_collection, mock_collection):
        """Test retrieving a non-existent comment"""
        # Arrange
        mock_get_collection.return_value = mock_collection
        mock_collection.find_one.return_value = None

        # Act
        result = CommentRepository.find_by_id(str(ObjectId()), "test_account_456")

        # Assert
        assert result is None

    @patch.object(CommentRepository, 'get_collection')
    def test_update_comment(self, mock_get_collection, mock_collection):
        """Test updating a comment"""
        # Arrange
        mock_get_collection.return_value = mock_collection
        comment_id = ObjectId()
        
        updated_comment = {
            "_id": comment_id,
            "task_id": "test_task_123",
            "account_id": "test_account_456",
            "content": "Updated comment content",
            "active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        mock_collection.find_one_and_update.return_value = updated_comment

        # Act
        result = CommentRepository.update(str(comment_id), "test_account_456", "Updated comment content")

        # Assert
        assert result is not None
        assert result.content == "Updated comment content"
        mock_collection.find_one_and_update.assert_called_once()
        
        # Verify the update query structure
        call_args = mock_collection.find_one_and_update.call_args
        assert call_args[0][0]["_id"] == comment_id
        assert call_args[0][1]["$set"]["content"] == "Updated comment content"

    @patch.object(CommentRepository, 'get_collection')
    def test_update_comment_not_found(self, mock_get_collection, mock_collection):
        """Test updating a non-existent comment"""
        # Arrange
        mock_get_collection.return_value = mock_collection
        mock_collection.find_one_and_update.return_value = None

        # Act
        result = CommentRepository.update(str(ObjectId()), "test_account_456", "New content")

        # Assert
        assert result is None

    @patch.object(CommentRepository, 'get_collection')
    def test_delete_comment(self, mock_get_collection, mock_collection):
        """Test deleting (soft delete) a comment"""
        # Arrange
        mock_get_collection.return_value = mock_collection
        mock_result = Mock()
        mock_result.modified_count = 1
        mock_collection.update_one.return_value = mock_result

        # Act
        result = CommentRepository.delete(str(ObjectId()), "test_account_456")

        # Assert
        assert result is True
        mock_collection.update_one.assert_called_once()
        
        # Verify soft delete (sets active=False)
        call_args = mock_collection.update_one.call_args
        assert call_args[0][1]["$set"]["active"] is False

    @patch.object(CommentRepository, 'get_collection')
    def test_delete_comment_not_found(self, mock_get_collection, mock_collection):
        """Test deleting a non-existent comment"""
        # Arrange
        mock_get_collection.return_value = mock_collection
        mock_result = Mock()
        mock_result.modified_count = 0
        mock_collection.update_one.return_value = mock_result

        # Act
        result = CommentRepository.delete(str(ObjectId()), "test_account_456")

        # Assert
        assert result is False

    def test_comment_model_from_bson(self):
        """Test CommentModel.from_bson method"""
        # Arrange
        bson_data = {
            "_id": ObjectId(),
            "task_id": "test_task_123",
            "account_id": "test_account_456",
            "content": "Test comment from BSON",
            "active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        # Act
        comment = CommentModel.from_bson(bson_data)

        # Assert
        assert comment.id == bson_data["_id"]
        assert comment.task_id == "test_task_123"
        assert comment.account_id == "test_account_456"
        assert comment.content == "Test comment from BSON"
        assert comment.active is True

    def test_comment_model_get_collection_name(self):
        """Test CommentModel.get_collection_name method"""
        # Act
        collection_name = CommentModel.get_collection_name()

        # Assert
        assert collection_name == "comments"