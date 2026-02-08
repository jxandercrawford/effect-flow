
from lib.effect import Effect, Context, EffectBinding
from lib.base import Either
from abc import ABC, abstractmethod
from typing import Optional, Any, List


class ExecutionNative(Effect):

    def __init__(self, f, context: Optional[Context] = {}, name: Optional[str] = "abc"):
        self.__f = f
        self.__name = name
        self.__context = context

    def execute(self, context: Context, *args, **kwargs) -> Context:
        return self.__f(context)


class ExecutionBuilderNative:

    def __init__(self, steps: Optional[List[EffectBinding]] = []):
        self.__steps = steps

    def add_step(self, effect: EffectBinding):
        self.__steps.append(effect)

    def __compile_effect(self, binding: EffectBinding, context: Context) -> Effect:
        return binding.init(context)

    def compile(self):
        def f(context: Optional[Context] = {}, *args, **kwargs):
            data = Either(right=context)
            for step in self.__steps:
                data = data.map(lambda x: self.__compile_effect(step, x).execute(x))
                data.raise_left()
            return data.get()
        return ExecutionNative(f)
