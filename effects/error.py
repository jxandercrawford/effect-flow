
from lib.effect import Effect, Context

class Error(Effect):

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.__value = kwargs.get("value")

    def execute(self, context: Context, *args, **kwargs) -> Context:
        raise RuntimeError(f"Error effect ({self._eid}) executed.")
