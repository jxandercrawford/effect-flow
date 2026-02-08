from abc import ABC, abstractmethod
from typing import Any, List, Optional, Callable
from lib.base import Either
from lib.effect import Effect, EffectBinding, FunctionEffect
from lib.context import Context


ExecutionNative = FunctionEffect


class ExecutionBuilderNative:

    def __init__(self, steps: Optional[List[EffectBinding]] = []):
        self.__steps = steps

    def add_step(self, effect: EffectBinding):
        self.__steps.append(effect)

    def __compile_effect(self, binding: EffectBinding, context: Context) -> Effect:
        return binding.init(context)

    def compile(self):
        def f(context: Optional[Context] = {}):
            data = Either(right=context)
            for step in self.__steps:
                def run_step(ctx, binding=step):
                    try:
                        effect = self.__compile_effect(binding, ctx)
                        return Either.try_of(lambda : effect.execute(ctx))
                    except Exception as e:
                        raise RuntimeError(f"Effect '{binding.name}' failed: {e}") from e
                data = data.flat_map(run_step)
                if data.is_left():
                    return f"Error at '{step}': {data.left}"
            return data.get()
        return ExecutionNative(f)