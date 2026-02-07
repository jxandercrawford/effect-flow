
from glob import glob
from typing import Optional
from lib.effect import Effect, Context

class ListFiles(Effect):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__value = kwargs.get("path")

    def execute(self, context: Context, *args, **kwargs):
        context[self._id] = {}
        context[self._id]["files"] = glob(self.__value)
        return context