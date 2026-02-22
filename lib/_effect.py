
from typing import TypeVar, ParamSpec, Callable, Generic, Union, TypeAlias, Any, get_type_hints, get_origin
from types import UnionType
import inspect
from dataclasses import dataclass

P = ParamSpec("P")
R = TypeVar("R")
E = TypeVar("E")
B = TypeVar("B")  # For map return type

DataType: TypeAlias = Any

@dataclass(frozen=True)
class Ok(Generic[R]):
    value: R

    def map(self, func: Callable[[R], B]) -> "Result[B, E]":
        try:
            value = func(self.value)
        except Exception as err:
            return Err(err)
        return Ok(value)

@dataclass(frozen=True)
class Err(Generic[E]):
    error: E

    def map(self, func: Callable[[R], B]) -> "Err[E]":
        return Err(self.error)

Result = Union[Ok[R], Err[E]]


def assert_type(actual: DataType, expected: DataType) -> bool:

    actual_origin = get_origin(actual)
    expected_origin = get_origin(expected)

    if actual == expected:
        return True
    elif expected_origin is Union or expected_origin is UnionType:
        return any([assert_type(actual, arg) for arg in expected.__args__])

    elif actual_origin is None and actual == expected_origin:
        return True

    elif actual_origin is not None and actual_origin == expected_origin:
        return any([assert_type(a, e) for a, e in zip(actual.__args__, expected.__args__)])
    return False

@dataclass(frozen=True)
class EffectResults(Generic[P, R]):
    parameters: P
    returns: R

class Effect(Generic[P, R, E]):

    def __init__(self, func: Callable[P, R]):
        self.__func = func
        self.__params, self.__defaults, self.__returns = self.inspect_callable(func)

    def __str__(self) -> str:
        return f"Effect({','.join([f'{k}:{v}' for k, v in self.__params.items()])}) => {self.__returns}"

    @property
    def __doc__(self) -> str | None:
        return self.__func.__doc__

    def __call__(self, *args, **kwargs) -> Result[R, E]:
        return self._run(*args, **kwargs)

    @staticmethod
    def inspect_callable(func: Callable[P, R]) -> tuple[dict[str, DataType], dict[str, Any], R | None]:
        params = {}
        returns = None
        for k, v in func.__annotations__.items():
            if k == "return":
                returns = v
            else:
                params[k] = v

        raw_defaults = func.__defaults__
        if raw_defaults:
            defaults = dict(zip(list(params.keys())[-len(raw_defaults):], raw_defaults))
        else:
            defaults = {}
        return (params, defaults, returns)

    def __full_param_dict(self, *args, **kwargs):
        given_args = dict(zip(list(self.__params.keys())[:len(args)], args))
        defaults = dict(self.__defaults)
        kwargs.update(given_args)
        kwargs.update(defaults)
        return kwargs

    def _validate_params(self, *args: P.args, **kwargs: P.kwargs) -> bool:
        full_args = self.__full_param_dict(*args, **kwargs)
        if len(args) + len(kwargs) > len(self.__params):
            return False
        return all([assert_type(type(v), self.__params.get(k)) for k, v in full_args.items()])

    def _validate_returns(self, value: R) -> bool:
        return assert_type(type(value), self.__returns)

    def _run(self, *args: P.args, **kwargs: P.kwargs) -> Result[R, E]:
        try:
            produced = self.__func(*args, **kwargs)
            if not self._validate_returns(produced):
                return Err(TypeError(f"Expected return type of '{self.__returns}' got value '{produced}' ({type(produced)})."))
        except Exception as err:
            return Err(err)
        return Ok(produced)

    def map(self, func: Callable[R, B]) -> "Effect[P, B, E]":
        _, _, new_returns = self.inspect_callable(func)
        def mapped(*args, **kwargs) -> B:
            match self._run(*args, **kwargs):
                case Ok(r):
                    value = func(r)
                case Err(e):
                    return Err(e)
            return value
        if new_returns:
            ann = dict(self.__params)
            ann["return"] = new_returns
            mapped.__annotations__ = ann
        return Effect(mapped)


def effect(func: Callable[P, R]) -> Effect:
    return Effect(func)

@effect
def n_lines(s: str, linesep: str = "\n") -> int:
    """Count lines in string"""
    return len(s.split("\n"))

def times_n(x: int, n: int | float) -> int:
    return x * n

def times_2(x: int | float) -> int | float:
    return x * 2

v = n_lines("a\nb\nc\n")
print(v)
print(n_lines("abc", 1))
double_lines = n_lines.map(times_2)
v2 = double_lines("a\nb\nc\n")
print(v2.map(lambda x: times_n(x, 5)))