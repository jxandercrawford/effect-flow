from importlib import import_module
from typing import Dict, Optional

from lib.effect import Effect


class EffectRegistry:

    def __init__(self, effects: Optional[Dict[str, Effect]] = {}):
        self.__effects = effects

    def register(self, name: str, effect: Effect):
        effects = self.__effects
        effects[name] = effect
        return EffectRegistry(effects)

    def get(self, key: str) -> Effect:
        return self.__effects[key]


def register_effect_plugins(path: str, registry: EffectRegistry) -> EffectRegistry:
    module_path, class_name = path.rsplit(".", 1)
    module = import_module(module_path)
    effect_class = getattr(module, class_name)

    if not issubclass(effect_class, Effect):
        raise ValueError(f"{entry} is not an Effect type.")

    return registry.register(path, effect_class)
