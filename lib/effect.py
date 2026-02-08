"""
effect class
"""

import random
import string
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TypeAlias, Callable
from functools import reduce
from lib.context import Context, get_path, set_path

ID_LENGTH: int = 16

def _generate_string(length: int) -> str:
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choice(chars) for _ in range(length))

# ===============

class Effect(ABC):
    def __init__(self, eid: Optional[str] = None, *args, **kwargs):
        self._eid = eid or _generate_string(ID_LENGTH)

    @abstractmethod
    def execute(self, context: Context, *args, **kwargs) -> Context:
        pass

    def then(self, _next: "Effect") -> "Effect":
        return _Sequential([self, _next])

    def map(self, path: str, f: Callable[[Any], Any]) -> "Effect":
        return self.then(_MapEffect(path, f))


class _MapEffect(Effect):
    def __init__(self, path: str, f: Callable):
        super().__init__()
        self.path, self.f = path, f

    def execute(self, context: Context) -> Context:
        value = get_path(context, self.path)
        return set_path(context, self.path, self.f(value)) if value is not None else context


class _Sequential(Effect):
    def __init__(self, effects: list):
        super().__init__()
        self.effects = effects

    def execute(self, context: Context) -> Context:
        return reduce(lambda ctx, eff: eff.execute(ctx), self.effects, context)

    def then(self, next_effect: Effect) -> Effect:
        return _Sequential(self.effects + [next_effect])


class FunctionEffect(Effect):
    def __init__(self, f: Callable[[Context], Context], eid: Optional[str] = None):
        super().__init__(eid)
        self.f = f

    def execute(self, context: Context) -> Context:
        return self.f(context)


class ConditionalEffect(Effect):
    def __init__(self, predicate: Callable[[Context], bool], then_effect: Effect, else_effect: Optional[Effect] = None):
        super().__init__()
        self.predicate = predicate
        self.then_effect = then_effect
        self.else_effect = else_effect or FunctionEffect(lambda ctx: ctx)

    def execute(self, context: Context) -> Context:
        return (
            self.then_effect if self.predicate(context)
            else self.else_effect
        ).execute(context)


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
            context_path = (
                binding.get("context").strip().split(".")
                if binding.get("context") is not None
                else []
            )
            context_value = self.__get_context_value(context, context_path)
            kwargs[name] = context_value or binding.get("default")
        return self.__effect(eid=self.__name, **kwargs)

    @property
    def name(self):
        return self.__name
