"""
effect class
"""

from abc import ABC, abstractmethod
from typing import Optional, Any, Dict, TypeAlias
from enum import IntEnum
from dataclasses import dataclass
import random
import string

ID_LENGTH: int = 16

Context: TypeAlias = Dict[str, Any]


def _generate_string(length: int) -> str:
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choice(chars) for _ in range(length))

class Effect(ABC):
    def __init__(self, id: Optional[str] = None):
        self._id = id or _generate_string(ID_LENGTH)

    @abstractmethod
    def execute(self, context: Context, *args, **kwargs) -> Context:
        pass
