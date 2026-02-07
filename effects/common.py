
from effects.effect import Effect, Context

class Print(Effect):

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.__value = kwargs.get("value")

    def execute(self, context: Context, *args, **kwargs) -> Context:
        print(self.__value)
        context[self._id] = self.__value
        return context


class Error(Effect):

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.__value = kwargs.get("value")

    def execute(self, context: Context, *args, **kwargs) -> Context:
        raise RuntimeError(f"Error effect ({self._id}) executed.")
