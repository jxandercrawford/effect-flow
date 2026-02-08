
from abc import ABC, abstractmethod
from typing import Optional, Any, List

class Monad(ABC):

    @abstractmethod
    def map(self, f):
        pass

    @abstractmethod
    def flat_map(self, f):
        pass

    @abstractmethod
    def get(self):
        pass


class Either(Monad):

    def __init__(self, left: Optional[Any] = None, right: Optional[Any] = None):
        if left is None and right is None:
            raise ValueError("Either left or right must be defined.")
        self.__left = left
        self.__right = right

    def __str__(self):
        if self.is_left():
            return f"Left({self.__left})"
        return f"Right({self.__right})"

    def get(self):
        self.raise_left()
        return self.__right

    def is_left(self) -> bool:
        return self.__left is not None

    def is_right(self) -> bool:
        return self.__right is not None

    def map(self, f):
        if self.is_left():
            return Either(left=self.__left)
        try:
            return Either(right=f(self.__right))
        except Exception as err:
            return Either(left=err)

    def flat_map(self, f):
        if self.is_left():
            return Either(left=self.__left)
        try:
            return f(self.__right)
        except Exception as err:
            return Either(left=err)

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
