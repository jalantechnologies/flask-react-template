from dataclasses import dataclass
from typing import TypeVar

ConfigType = TypeVar("ConfigType", bound=bool | dict | float | int | list | str)


@dataclass(frozen=True)
class ErrorCode:
    MISSING_KEY: str = "KEY_ERR_404"
    VALUE_TYPE_MISMATCH: str = "INVALID_VALUE_TYPE_400"
