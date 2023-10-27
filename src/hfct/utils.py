from enum import Enum



class BaseEnum(Enum):
    pass

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]
