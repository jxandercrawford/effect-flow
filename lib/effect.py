"""
effect class
"""

from abc import ABC, abstractmethod
from typing import Optional, Any, Dict, TypeAlias, List
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
    def __init__(self, id: Optional[str] = None, *args, **kwargs):
        self._id = id or _generate_string(ID_LENGTH)

    @abstractmethod
    def execute(self, context: Context, *args, **kwargs) -> Context:
        pass


class EffectBinding:

    def __init__(self, name: str, effect, config_bindings: Dict[str, Dict[str, Any]]):
        self.__name = name
        self.__effect = effect
        self.__config_bindings = config_bindings

    def __get_context_value(self, context: Context, path: List[str]):
        if context is None or len(path) < 1:
            return None
        elif len(path) == 1:
            return context.get(path[0])
        return self.__get_context_value(context.get(path[0]), path[1:])

    def init(self, context: Context) -> Effect:
        kwargs = {}
        for name, binding in self.__config_bindings.items():
            context_path = binding.get("context").strip().split(".") if binding.get("context") is not None else []
            context_value = self.__get_context_value(context, context_path)
            kwargs[name] = context_value or binding.get("default")
        return self.__effect(id=self.__name, **kwargs)
