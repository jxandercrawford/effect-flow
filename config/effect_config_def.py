
from enum import IntEnum
from typing import Any

class FieldType(IntEnum):
    STRING = 1
    INTEGER = 2
    DOUBLE = 3
    ARRAY = 4

    def validate(self, d: Any, raise_error: bool = False) -> bool:
        try:
            match self:
                case 1:
                    str(d)
                case 2:
                    int(d)
                case 3:
                    float(d)
                case 4:
                    list(d)
        except Exception as err:
            if raise_error:
                raise err
            return False
        return True


class ConfigField:
    def __init__(self, name: str=None, dtype: FieldType=None, default: Any=None, desc: str=None):
        self.__name = name
        self.__dtype = dtype
        self.__default = default
        self.__desc = desc

    def __str__(self):
        return f"Field({self.__name},{self.__dtype},{self.__default},{self.__desc})"

    @property
    def name(self):
        return self.__name

    @property
    def dtype(self):
        return self.__dtype

    @property
    def default(self):
        return self.__default

    @property
    def desc(self):
        return self.__desc

    def name(self, name: str):
        return ConfigField(name, self.__dtype, self.__default, self.__desc)

    def dtype(self, dtype: FieldType):
        return ConfigField(self.__name, dtype, self.__default, self.__desc)

    def default(self, default: Any):
        if not self.__dtype.validate(default):
            raise ValueError(f"Invalid default of '{default}' for type: {self.__dtype.name} ({self.__dtype})")
        return ConfigField(self.__name, self.__dtype, default, self.__desc)

    def desc(self, desc: str):
        return ConfigField(self.__name, self.__dtype, self.__default, desc)


class ConfigDef:

    def __init__(self, fields=[]):
        self.__fields = fields

    def field(self, f: ConfigField):
        return ConfigDef(**[self.__fields, f])


f = ConfigField()
print(f)
f1 = f.name("id")
print(f1)
f2 = f1.dtype(FieldType.STRING)
print(f2)
f3 = f2.default("ABC")
print(f3)
f4 = f3.desc("The ID.")
print(f4)