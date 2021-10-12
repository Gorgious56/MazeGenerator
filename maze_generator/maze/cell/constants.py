from enum import Enum


class CellType(Enum):
    POLAR = "0"
    TRIANGLE = "1"
    SQUARE = "2"
    HEXAGON = "3"
    OCTOGON = "4"
    DODECAGON = "5"
    DEFAULT = "2"

    @staticmethod
    def get_type_enum():
        return [(e.value, e.name.capitalize(), "") for e in CellType]
