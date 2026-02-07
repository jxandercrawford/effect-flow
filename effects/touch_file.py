
from glob import glob
import io
import os
from typing import Optional
from lib.effect import Effect, Context

class TouchFile(Effect):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__value = kwargs.get("path")

    def execute(self, context: Context, *args, **kwargs):
        if isinstance(self.__value, (list)):
            for path in self.__value:
                with io.open(path, "ab"):
                    os.utime(path, None)
        else:
            with io.open(self.__value, "ab"):
                    os.utime(path, None)
        return context