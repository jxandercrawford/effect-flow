
from typing import Optional, Dict, Tuple, Any, List
from lib.effect import Effect, Context, EffectBinding
from lib.registry import EffectRegistry
from dataclasses import dataclass
import yaml
import importlib
import pkgutil
from pathlib import Path
from dataclasses import dataclass, field
import sys
import importlib
from typing import Iterable


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

    def __parse_effect(self, d) -> EffectBinding:
        name = d["name"]
        eclass = d["class"]
        config = d.get("config", {})
        return EffectBinding(name, self.__get_effect(eclass), config)

    def parse(self, config: Dict[str, Any]) -> WorkflowDefinition:
        workflow_config = config.get("workflow")
        return WorkflowDefinition(
            name=workflow_config.get("name"),
            context=workflow_config.get("context", {}),
            effects=[self.__parse_effect(d) for d in workflow_config.get("effects", [])]
        )


def read_yaml(path: str, parser: ConfigParser) -> WorkflowDefinition:
    with open(path, "r") as fp:
        return parser.parse(yaml.safe_load(fp))


def build_workflow(definition: WorkflowDefinition, builder: "ExecutionBuilderNative") -> Tuple[Context, "ExecutionNative"]:
    for effect in definition.effects:
        builder.add_step(effect)
    return (definition.context, builder.compile())
