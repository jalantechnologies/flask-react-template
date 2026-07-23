from dataclasses import dataclass
from typing import Any, TypeVar

ConfigType = TypeVar("ConfigType", bound=bool | dict[str, Any] | float | int | list[Any] | str)


@dataclass(frozen=True)
class ErrorCode:
    MISSING_KEY: str = "KEY_ERR_404"
    VALUE_TYPE_MISMATCH: str = "INVALID_VALUE_TYPE_400"
