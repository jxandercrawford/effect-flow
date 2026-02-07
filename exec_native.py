
from lib.executor import ExecutionBuilderNative
from lib.runtime import ConfigParser, EffectRegistry, read_yaml, build_workflow, register_effect_plugins
import argparse
import os


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Effect Flow Native Executor")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        required=True,
        help="Path to workflow YAML config file"
    )
    parser.add_argument(
        "--effects",
        type=str,
        default="",
        help=f"Optional. Effect plugins paths to load. Should be specified as 'path.to.module.Name1,path.to.module.Name2'. Defaults to ''.",
    )

    args = parser.parse_args()
    registry = EffectRegistry()
    register_effect_plugins(args.effects.strip().split(","), registry)
    parser = ConfigParser(registry)

    builder = ExecutionBuilderNative()
    definition = read_yaml(args.config, parser)

    context, executor = build_workflow(definition, builder)

    executor.execute(context)