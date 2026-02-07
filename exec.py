
from effects.common import Print, Error
from effects.executor import ExecutionBuilderNative
from effects.runtime import ConfigParser, EffectRegistry, read_yaml, build_workflow

if __name__ == "__main__":
    registry = EffectRegistry()
    registry.register("Print", Print)
    registry.register("Error", Error)
    parser = ConfigParser(registry)

    builder = ExecutionBuilderNative()
    definition = read_yaml("/Users/jxan/Documents/development/effect-flow/config/demo.yaml", parser)

    context, executor = build_workflow(definition, builder)

    executor.execute(context)