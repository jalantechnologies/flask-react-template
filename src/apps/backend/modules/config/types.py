from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T", bound=int | str | bool | list | dict)
