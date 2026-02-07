
from typing import Optional, Dict, Tuple, Any, List
from lib.effect import Effect, _generate_string, Context
from lib.executor import ExecutionBuilderNative, ExecutionNative
from dataclasses import dataclass
import yaml
import importlib
import pkgutil
from pathlib import Path
from dataclasses import dataclass, field
import sys


class EffectRegistry:

    def __init__(self, effects: Optional[Dict[str, Effect]] = {}):
        self.__effects = effects

    def register(self, name: str, effect: Effect):
        self.__effects[name] = effect

    def get(self, key: str) -> Effect:
        return self.__effects[key]


@dataclass
class WorkflowDefinition:
    name: str
    effects: list = field(default_factory=list)
    context: dict = field(default_factory=dict)


class ConfigParser:

    def __init__(self, registry: EffectRegistry):
        self.__registry = registry

    def __get_effect(self, name):
        return self.__registry.get(name)

    def __parse_effect(self, d):
        name = d["name"]
        eclass = d["class"]
        config = d.get("config", {})
        effect_id = name + "-" + _generate_string(16)
        return self.__get_effect(eclass)(id=effect_id, **config)

    def parse(self, config: Dict[str, Any]) -> WorkflowDefinition:
        workflow_config = config.get("workflow")
        return WorkflowDefinition(
            name=workflow_config.get("name"),
            context=workflow_config.get("context", {}),
            effects=[self.__parse_effect(d) for d in workflow_config.get("effects", [])]
        )


import importlib
from typing import Iterable


def register_effect_plugins(effects: List[str], registry):
    for entry in effects:
        try:
            module_path, class_name = entry.rsplit(".", 1)
            module = importlib.import_module(module_path)
            effect_class = getattr(module, class_name)
            if not issubclass(effect_class, Effect):
                raise ValueError(f"{entry} is not an Effect type.")
            registry.register(entry, effect_class)

        except ValueError:
            raise ValueError(
                f"Invalid effect path '{entry}'. Expected 'module.ClassName'"
            )
        except ImportError as e:
            raise ImportError(f"Could not import module '{module_path}'") from e
        except AttributeError as e:
            raise AttributeError(
                f"Module '{module_path}' has no class '{class_name}'"
            ) from e



def read_yaml(path, parser) -> WorkflowDefinition:
    with open(path, "r") as fp:
        return parser.parse(yaml.safe_load(fp))

def build_workflow(definition: WorkflowDefinition, builder: ExecutionBuilderNative) -> Tuple[Context, ExecutionNative]:
    for effect in definition.effects:
        builder.add_step(effect)
    return (definition.context, builder.compile())
