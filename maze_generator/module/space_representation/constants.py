from enum import Enum


class SpaceRepresentation(Enum):
    PLANE = "0"
    CYLINDER = "1"
    MOEBIUS = "2"
    TORUS = "3"
    BOX = "4"

    @classmethod
    def get_type_enum(cls):
        return [(e.value, e.name.capitalize(), "") for e in cls]