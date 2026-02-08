
from lib.effect import Effect, FunctionEffect
from lib.context import Context, get_path, set_path
from time import sleep

class Sleep(Effect):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__seconds = int(kwargs.get("seconds"))

    def execute(self, context: Context, *args, **kwargs) -> Context:
        sleep(self.__seconds)
        return context
