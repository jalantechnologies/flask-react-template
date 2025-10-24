from modules.application.errors import AppError


class MissingKeyError(AppError):
    def __init__(self, *, missing_key: str, error_code: str) -> None:
        super().__init__(
            f"Missing configuration key: '{missing_key}'. Please ensure it is defined in the config files.", error_code
        )
        self.code = error_code


class ValueTypeMismatchError(Exception):
    def __init__(self, *, actual_value_type: str, error_code: str, expected_value_type: str, key: str):
        super().__init__(f"Value mismatch for key: {key}. Expected: {expected_value_type}, Actual: {actual_value_type}")
        self.code = error_code
