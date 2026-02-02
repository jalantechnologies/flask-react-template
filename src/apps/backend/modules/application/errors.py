from typing import Any, Optional


class AppError(Exception):
    def __init__(self, message: str, code: str, http_status_code: Optional[int] = None) -> None:
        self.message = message
        self.code = code
        self.http_code = http_status_code
        super().__init__(self.message)

    def to_str(self) -> str:
        return f"{self.code}: {self.message}"

    def to_dict(self) -> dict[str, Any]:
        error_dict = {
            "message": self.message,
            "code": self.code,
            "http_code": self.http_code,
            "args": self.args,
            "with_traceback": self.with_traceback,
        }
        return error_dict
