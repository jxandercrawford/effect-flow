
from effects.effect import Effect, Context
from abc import ABC, abstractmethod
from typing import Optional, Any, List

class Monoid(ABC):

    @abstractmethod
    def map(self, f):
        pass

    @abstractmethod
    def flat_map(self, f):
        pass

    @abstractmethod
    def get(self):
        pass


class Either(Monoid):

    def __init__(self, left: Optional[Any] = None, right: Optional[Any] = None):
        self.__left = left
        self.__right = right

    def __str__(self):
        return f"Either({self.__left},{self.__right})"

    def get(self):
        return self.__right

    def map(self, f):
        if self.__left is not None:
            return Either(left=self.__left, right=self.__right)
        try:
            return Either(right=f(self.__right))
        except Exception as err:
            return Either(left=err)

    def flat_map(self, f):
        if self.__left is not None:
            return Either(left=self.__left, right=self.__right)
        return f(self.__right)

    @property
    def left(self) -> Any:
        return self.__left

    @property
    def right(self) -> Any:
        return self.__right

    def raise_left(self):
        if isinstance(self.__left, Exception):
            raise self.__left
        elif self.__left is not None:
            raise RuntimeError(self.__left)


class ExecutionNative(Effect):

    def __init__(self, f, context: Optional[Context] = {}, name: Optional[str] = "abc"):
        self.__f = f
        self.__name = name
        self.__context = context

    def execute(self, context: Context, *args, **kwargs) -> Context:
        return self.__f(context)


class ExecutionBuilderNative:

    def __init__(self, steps: Optional[List[Effect]] = []):
        self.__steps = steps

    def add_step(self, effect: Effect):
        self.__steps.append(effect)

    def compile(self):
        def f(context: Optional[Context] = {}, *args, **kwargs):
            data = Either(right=context)
            for step in self.__steps:
                data = data.map(step.execute)
                data.raise_left()
            return data.get()
        return ExecutionNative(f)
