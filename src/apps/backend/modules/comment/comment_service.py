from modules.account.account_service import AccountService
from modules.account.types import AccountSearchByIdParams
from modules.application.common.types import PaginationResult
from modules.comment.internal.comment_reader import CommentReader
from modules.comment.internal.comment_writer import CommentWriter
from modules.comment.types import (
    CreateCommentParams,
    DeleteCommentParams,
    GetPaginatedCommentsParams,
    GetCommentParams,
    Comment,
    CommentDeletionResult,
    UpdateCommentParams,
)


class CommentService:
    @staticmethod
    def create_comment(*, params: CreateCommentParams) -> Comment:
        # Get account information to retrieve author name
        account = AccountService.get_account_by_id(
            params=AccountSearchByIdParams(id=params.account_id)
        )
        author_name = f"{account.first_name} {account.last_name}".strip()

        return CommentWriter.create_comment(params=params, author_name=author_name)

    @staticmethod
    def get_comment(*, params: GetCommentParams) -> Comment:
        return CommentReader.get_comment(params=params)

    @staticmethod
    def get_paginated_comments(*, params: GetPaginatedCommentsParams) -> PaginationResult[Comment]:
        return CommentReader.get_paginated_comments(params=params)

    @staticmethod
    def update_comment(*, params: UpdateCommentParams) -> Comment:
        return CommentWriter.update_comment(params=params)

    @staticmethod
    def delete_comment(*, params: DeleteCommentParams) -> CommentDeletionResult:
        return CommentWriter.delete_comment(params=params)