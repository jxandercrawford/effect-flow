
from lib.effect import Effect, Context

class Print(Effect):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__value = kwargs.get("value")

    def execute(self, context: Context, *args, **kwargs) -> Context:
        print(self.__value)
        context[self._eid] = {}
        context[self._eid]["value"] = self.__value
        return context
