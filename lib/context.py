
from typing import Any, Dict, List, Optional, TypeAlias, Callable

Context: TypeAlias = Dict[str, Any]

def get_path(context: Context, path: str) -> Optional[Any]:
    if not path or not context:
        return None
    return reduce(
        lambda acc, key: acc.get(key) if isinstance(acc, dict) else None,
        path.strip().split('.'),
        context
    )

def set_path(context: Context, path: str, value: Any) -> Context:
    if not path:
        return context
    steps = path.strip().split(".", 1)
    if len(steps) == 1:
        return {**context, steps[0]: value}
    return {
        **context,
        steps[0]: set_path(context.get(steps[0], {}), steps[1], value)
    }